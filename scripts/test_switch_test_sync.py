"""Disposable real-Git regression tests for the single-machine handoff."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "docs/sync-cowork/sync/workstation_sync.py"
LAUNCHER = ROOT / "docs/sync-cowork/sync/sync.sh"
PARENTS = ["sunmoonun", "sample-app", "sunmoon-link"]
CHILD = "sample-app/sample-backend"


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, text=True, capture_output=True
    ).stdout.strip()


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="single-machine-sync-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.work = self.base / "worktrees/qwen"
        self.origins = {}
        for name in [*PARENTS, CHILD]:
            origin = self.base / (name.replace("/", "-") + ".git")
            git(self.base, "init", "--bare", str(origin))
            repo = self.work / name
            repo.parent.mkdir(parents=True, exist_ok=True)
            git(self.base, "clone", str(origin), str(repo))
            self.configure(repo)
            git(repo, "switch", "-c", "qwen")
            git(repo, "commit", "--allow-empty", "-m", "base")
            git(repo, "push", "-u", "origin", "qwen")
            self.origins[name] = origin
        parent = self.work / "sample-app"
        (parent / ".gitmodules").write_text(
            '[submodule "sample-backend"]\n\tpath = sample-backend\n'
            f"\turl = {self.origins[CHILD]}\n"
        )
        git(parent, "add", ".gitmodules", "sample-backend")
        git(parent, "commit", "-m", "pin child")
        git(parent, "push")
        self.env = dict(os.environ, WS="qwen", SYNC_JOBS="4")
        self.env.pop("BRANCH", None)
        self.env.pop("GIT_REMOTE", None)
        self.env.pop("GIT_CONFIG_COUNT", None)

    def configure(self, repo):
        for key, value in [
            ("user.name", "Test"),
            ("user.email", "test@example.invalid"),
            ("commit.gpgsign", "false"),
            ("core.hooksPath", "/dev/null"),
        ]:
            git(repo, "config", key, value)

    def commit(self, repo, name="note", text="change"):
        (repo / name).write_text(text)
        git(repo, "add", name)
        git(repo, "commit", "-m", name)
        return git(repo, "rev-parse", "HEAD")

    def other(self, name):
        path = self.base / ("other-" + name.replace("/", "-"))
        git(self.base, "clone", "-b", "qwen", str(self.origins[name]), str(path))
        self.configure(path)
        return path

    def sync(self, action, success=True, target=None):
        r = subprocess.run(
            [
                "python3",
                str(ENGINE),
                action,
                "--root",
                str(self.work),
                "--repos",
                *PARENTS,
                *(["--target=" + target] if target is not None else []),
            ],
            check=False,
            env=self.env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(r.returncode == 0, success, r.stdout + r.stderr)
        return r

    def test_pull_fast_forwards_and_fetches_each_repo_only_once(self):
        other = self.other("sunmoonun")
        target = self.commit(other)
        git(other, "push")
        trace = self.base / "git-calls"
        bindir = self.base / "bin"
        bindir.mkdir()
        actual = shutil.which("git")
        wrapper = bindir / "git"
        wrapper.write_text(
            "#!/usr/bin/env python3\nimport os,sys,json\n"
            f'with open({str(trace)!r}, "a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n'
            f"os.execv({actual!r}, [{actual!r}, *sys.argv[1:]])\n"
        )
        wrapper.chmod(0o755)
        self.env["PATH"] = str(bindir) + os.pathsep + self.env["PATH"]
        self.sync("pull")
        self.assertEqual(git(self.work / "sunmoonun", "rev-parse", "HEAD"), target)
        calls = [json.loads(line) for line in trace.read_text().splitlines()]
        self.assertEqual(sum(c[2] == "fetch" for c in calls), 4)
        self.assertFalse(any(c[2] == "pull" for c in calls))

    def test_pull_lists_cowork_and_review_requests_but_not_replies(self):
        other = self.other("sunmoonun")
        base = other / "docs/sync-cowork"
        entries = {
            "inbox-cowork/opus/build.md": "# build card\n",
            "inbox-review/luna/inbox/methods/request.md": "# review request\n",
            "inbox-review/luna/inbox/data/request.md": "# second request\n",
            "inbox-review/luna/inbox/methods/replies/opus.md": "# review reply\n",
            "inbox-review/luna/inbox/data/replies/request.md": "# not a request\n",
            "inbox-review/luna/inbox/README.md": "# instructions\n",
        }
        for name, content in entries.items():
            path = base / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        git(other, "add", "docs")
        git(other, "commit", "-m", "handoff cards")
        git(other, "push")
        result = self.sync("pull", target="sunmoonun")
        self.assertIn("协作待办 opus/build.md # build card", result.stdout)
        self.assertIn("luna/inbox/methods/request.md # review request", result.stdout)
        self.assertIn("luna/inbox/data/request.md # second request", result.stdout)
        self.assertNotIn("# not a request", result.stdout)
        self.assertNotIn("review reply", result.stdout)
        self.assertNotIn("# instructions", result.stdout)

    def test_fetch_parallelism_is_bounded(self):
        state = self.base / "fetch-state"
        state.write_text('{"active":0,"max":0}')
        bindir = self.base / "parallel-bin"
        bindir.mkdir()
        actual = shutil.which("git")
        wrapper = bindir / "git"
        wrapper.write_text(
            "#!/usr/bin/env python3\nimport os,sys,json,fcntl,time,subprocess\n"
            f"state={str(state)!r}\n"
            "def change(delta):\n"
            ' with open(state,"r+") as f:\n'
            '  fcntl.flock(f,fcntl.LOCK_EX);d=json.load(f);d["active"]+=delta;d["max"]=max(d["max"],d["active"]);f.seek(0);json.dump(d,f);f.truncate()\n'
            'fetch=len(sys.argv)>3 and sys.argv[3]=="fetch"\n'
            "if fetch: change(1);time.sleep(.2)\n"
            f"r=subprocess.run([{actual!r},*sys.argv[1:]])\n"
            "if fetch: change(-1)\n"
            "sys.exit(r.returncode)\n"
        )
        wrapper.chmod(0o755)
        self.env.update(PATH=str(bindir) + os.pathsep + self.env["PATH"], SYNC_JOBS="2")
        self.sync("pull")
        self.assertEqual(json.loads(state.read_text()), {"active": 0, "max": 2})

    def test_detached_child_does_not_reset_existing_branch(self):
        repo = self.work / CHILD
        old = git(repo, "rev-parse", "HEAD")
        newer = self.commit(repo, "local-only")
        git(repo, "switch", "--detach", old)
        self.sync("pull", False)
        self.assertEqual(git(repo, "rev-parse", "qwen"), newer)
        self.assertEqual(git(repo, "rev-parse", "HEAD"), old)

    def test_child_follows_gitlink_not_newer_branch_head(self):
        other = self.other(CHILD)
        new = self.commit(other)
        git(other, "push")
        pinned = git(self.work / CHILD, "rev-parse", "HEAD")
        self.sync("pull")
        self.assertEqual(git(self.work / CHILD, "rev-parse", "HEAD"), pinned)
        self.assertNotEqual(new, pinned)
        self.assertEqual(git(self.work / "sample-app", "status", "--porcelain"), "")

    def test_new_gitlink_and_detached_child_attach_safely(self):
        other = self.other(CHILD)
        new = self.commit(other)
        git(other, "push")
        parent = self.other("sample-app")
        git(parent, "update-index", "--cacheinfo", f"160000,{new},sample-backend")
        git(parent, "commit", "-m", "advance pin")
        git(parent, "push")
        git(self.work / CHILD, "switch", "--detach")
        self.sync("pull")
        self.assertEqual(git(self.work / CHILD, "rev-parse", "HEAD"), new)
        self.assertEqual(git(self.work / CHILD, "branch", "--show-current"), "qwen")
        self.assertEqual(git(self.work / "sample-app", "status", "--porcelain"), "")

    def test_pull_checks_all_before_merging_on_divergence(self):
        first = self.other("sunmoonun")
        self.commit(first)
        git(first, "push")
        other = self.other("sunmoon-link")
        self.commit(other, "remote")
        git(other, "push")
        self.commit(self.work / "sunmoon-link", "local")
        before = git(self.work / "sunmoonun", "rev-parse", "HEAD")
        self.sync("pull", False)
        self.assertEqual(git(self.work / "sunmoonun", "rev-parse", "HEAD"), before)

    def test_dirty_files_are_never_committed(self):
        repo = self.work / "sunmoonun"
        before = git(repo, "rev-parse", "HEAD")
        (repo / "private-note").write_text("do not publish")
        self.sync("push", False)
        self.sync("pull", False)
        self.assertEqual(git(repo, "rev-parse", "HEAD"), before)
        self.assertEqual(git(self.origins["sunmoonun"], "rev-parse", "qwen"), before)
        self.assertTrue((repo / "private-note").exists())

    def test_fetch_failure_stops_before_any_merge(self):
        other = self.other("sunmoonun")
        self.commit(other)
        git(other, "push")
        before = git(self.work / "sunmoonun", "rev-parse", "HEAD")
        git(
            self.work / "sunmoon-link",
            "remote",
            "set-url",
            "origin",
            str(self.base / "missing.git"),
        )
        self.sync("pull", False)
        self.assertEqual(git(self.work / "sunmoonun", "rev-parse", "HEAD"), before)

    def test_parent_is_pushed_after_child(self):
        child = self.work / CHILD
        new = self.commit(child)
        parent = self.work / "sample-app"
        git(parent, "add", "sample-backend")
        git(parent, "commit", "-m", "pin")
        hook = self.origins["sample-app"] / "hooks/pre-receive"
        hook.write_text(
            "#!/bin/sh\nset -eu\nwhile read old new ref; do\n"
            'expected=$(git rev-parse "$new:sample-backend")\n'
            f'actual=$(env -u GIT_DIR -u GIT_WORK_TREE git --git-dir="{self.origins[CHILD]}" rev-parse qwen)\n'
            'test "$expected" = "$actual"\ndone\n'
        )
        hook.chmod(0o755)
        self.sync("push")
        self.assertEqual(git(self.origins[CHILD], "rev-parse", "qwen"), new)
        self.assertEqual(
            git(self.origins["sample-app"], "rev-parse", "qwen:sample-backend"), new
        )

    def test_child_push_rejection_blocks_parent(self):
        before = git(self.origins["sample-app"], "rev-parse", "qwen")
        self.commit(self.work / CHILD)
        parent = self.work / "sample-app"
        git(parent, "add", "sample-backend")
        git(parent, "commit", "-m", "pin")
        hook = self.origins[CHILD] / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        self.sync("push", False)
        self.assertEqual(git(self.origins["sample-app"], "rev-parse", "qwen"), before)

    def test_mirror_receives_commit_even_when_primary_already_has_it(self):
        repo = self.work / "sunmoonun"
        mirror = self.base / "mirror.git"
        git(self.base, "clone", "--bare", str(self.origins["sunmoonun"]), str(mirror))
        new = self.commit(repo)
        git(repo, "push")
        git(
            repo,
            "remote",
            "set-url",
            "--add",
            "--push",
            "origin",
            str(self.origins["sunmoonun"]),
        )
        git(repo, "remote", "set-url", "--add", "--push", "origin", str(mirror))
        self.sync("push")
        self.assertEqual(git(mirror, "rev-parse", "qwen"), new)

    def test_unknown_push_endpoint_is_error_not_missing_branch(self):
        first = self.work / "sunmoonun"
        new = self.commit(first)
        repo = self.work / "sunmoon-link"
        git(
            repo,
            "remote",
            "set-url",
            "--add",
            "--push",
            "origin",
            str(self.base / "missing.git"),
        )
        self.sync("push", False)
        self.assertNotEqual(git(self.origins["sunmoonun"], "rev-parse", "qwen"), new)

    def test_push_refuses_remote_ahead_without_rebase(self):
        other = self.other("sunmoonun")
        self.commit(other, "remote")
        git(other, "push")
        before = self.commit(self.work / "sunmoonun", "local")
        self.sync("push", False)
        self.assertEqual(git(self.work / "sunmoonun", "rev-parse", "HEAD"), before)

    def test_wrong_named_child_branch_refuses(self):
        git(self.work / CHILD, "switch", "-c", "other")
        self.sync("pull", False)
        self.sync("push", False)

    def test_new_remote_branch_can_be_published(self):
        git(self.origins["sunmoonun"], "update-ref", "-d", "refs/heads/qwen")
        self.sync("push")
        self.assertEqual(
            git(self.origins["sunmoonun"], "rev-parse", "qwen"),
            git(self.work / "sunmoonun", "rev-parse", "HEAD"),
        )

    def test_status_does_not_contact_remote(self):
        git(
            self.work / "sunmoonun",
            "remote",
            "set-url",
            "origin",
            str(self.base / "missing.git"),
        )
        self.sync("status")

    def test_missing_workspace_fails(self):
        self.env.pop("WS")
        self.sync("pull", False)

    def test_parent_pull_isolated_and_child_still_follows_pin(self):
        other = self.other(CHILD)
        pinned = self.commit(other, "pin")
        self.commit(other, "newer-than-pin")
        git(other, "push")
        parent = self.other("sample-app")
        git(parent, "update-index", "--cacheinfo", f"160000,{pinned},sample-backend")
        git(parent, "commit", "-m", "advance pin")
        git(parent, "push")
        (self.work / "sunmoonun/private-note").write_text("unrelated")
        git(
            self.work / "sunmoon-link", "remote", "set-url", "origin", "/missing-remote"
        )
        result = self.sync("pull", target="sample-app")
        self.assertIn("2 仓", result.stdout)
        self.assertEqual(git(self.work / CHILD, "rev-parse", "HEAD"), pinned)
        self.assertEqual(git(self.work / "sample-app", "status", "--porcelain"), "")

    def test_parent_scope_launcher_pushes_children_before_parent(self):
        launcher = self.install_launcher()
        new = self.commit(self.work / CHILD)
        parent = self.work / "sample-app"
        git(parent, "add", "sample-backend")
        git(parent, "commit", "-m", "pin")
        hook = self.origins["sample-app"] / "hooks/pre-receive"
        hook.write_text(
            "#!/bin/sh\nset -eu\nwhile read old new ref; do\n"
            'expected=$(git rev-parse "$new:sample-backend")\n'
            f'actual=$(env -u GIT_DIR -u GIT_WORK_TREE git --git-dir="{self.origins[CHILD]}" rev-parse qwen)\n'
            'test "$expected" = "$actual"\ndone\n'
        )
        hook.chmod(0o755)
        (self.work / "sunmoonun/private-note").write_text("unrelated")
        result = subprocess.run(
            [str(launcher), "push", "sample-app"],
            check=False,
            env=self.env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(git(self.origins[CHILD], "rev-parse", "qwen"), new)
        self.assertEqual(
            git(self.origins["sample-app"], "rev-parse", "qwen:sample-backend"), new
        )

    def test_child_pull_uses_branch_without_changing_parent_commit(self):
        parent = self.work / "sample-app"
        before = git(parent, "rev-parse", "HEAD")
        other = self.other(CHILD)
        new = self.commit(other)
        git(other, "push")
        git(self.work / CHILD, "switch", "--detach")
        (parent / "author-note").write_text("keep this")
        result = self.sync("pull", target=CHILD)
        self.assertIn("1 仓", result.stdout)
        self.assertIn("本次未同步上级父仓", result.stdout)
        self.assertEqual(git(self.work / CHILD, "rev-parse", "HEAD"), new)
        self.assertEqual(git(parent, "rev-parse", "HEAD"), before)
        self.assertIn("sample-backend", git(parent, "status", "--porcelain"))

    def test_child_scope_launcher_pushes_only_child_despite_dirty_parent(self):
        launcher = self.install_launcher()
        parent_before = git(self.origins["sample-app"], "rev-parse", "qwen")
        new = self.commit(self.work / CHILD)
        (self.work / "sample-app/private-note").write_text("keep this")
        result = subprocess.run(
            [str(launcher), "push", CHILD],
            check=False,
            env=self.env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(git(self.origins[CHILD], "rev-parse", "qwen"), new)
        self.assertEqual(
            git(self.origins["sample-app"], "rev-parse", "qwen"), parent_before
        )

    def test_invalid_and_unregistered_scope_refused_before_network(self):
        (self.work / "sample-app/unregistered").mkdir()
        for target in [
            "",
            "fable",
            "../qwen/sunmoonun",
            str(self.work / CHILD),
            "sample-app/../sunmoonun",
            "sample-app/unregistered",
        ]:
            with self.subTest(target=target):
                result = self.sync("pull", False, target=target)
                self.assertNotIn("已抓取", result.stdout)

    def test_scope_refuses_symlink_outside_workstation(self):
        child = self.work / CHILD
        outside = self.base / "outside-child"
        child.rename(outside)
        child.symlink_to(outside, target_is_directory=True)
        result = self.sync("pull", False, target=CHILD)
        self.assertIn("超出当前工位", result.stderr)

    def test_child_status_does_not_include_parent_or_other_roots(self):
        result = self.sync("status", target=CHILD)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertTrue(result.stdout.startswith(CHILD + " "))

    def test_selected_child_preserves_nested_dependency_order(self):
        child = self.work / CHILD
        nested = child / "nested"
        origin = self.base / "nested.git"
        git(self.base, "init", "--bare", str(origin))
        git(self.base, "clone", str(origin), str(nested))
        self.configure(nested)
        git(nested, "switch", "-c", "qwen")
        new = self.commit(nested)
        (child / ".gitmodules").write_text(
            f'[submodule "nested"]\n\tpath = nested\n\turl = {origin}\n'
        )
        git(child, "add", ".gitmodules", "nested")
        git(child, "commit", "-m", "pin nested")
        hook = self.origins[CHILD] / "hooks/pre-receive"
        hook.write_text(
            "#!/bin/sh\nset -eu\nwhile read old new ref; do\n"
            'expected=$(git rev-parse "$new:nested")\n'
            f'actual=$(env -u GIT_DIR -u GIT_WORK_TREE git --git-dir="{origin}" rev-parse qwen)\n'
            'test "$expected" = "$actual"\ndone\n'
        )
        hook.chmod(0o755)
        before = git(self.origins["sample-app"], "rev-parse", "qwen")
        result = self.sync("push", target=CHILD)
        self.assertIn("2 仓", result.stdout)
        self.assertEqual(git(origin, "rev-parse", "qwen"), new)
        self.assertEqual(git(self.origins["sample-app"], "rev-parse", "qwen"), before)

    def install_launcher(self):
        tools = self.work / "sunmoonun/docs/sync-cowork/sync"
        tools.mkdir(parents=True)
        shutil.copy2(ENGINE, tools / ENGINE.name)
        shutil.copy2(LAUNCHER, tools / LAUNCHER.name)
        (tools / "config.sh").write_text(
            "GIT_REMOTE=origin\nREPOS=(sunmoonun sample-app sunmoon-link)\n"
        )
        repo = self.work / "sunmoonun"
        git(repo, "add", "docs")
        git(repo, "commit", "-m", "install daily engine")
        git(repo, "push")
        return tools / LAUNCHER.name

    def test_launcher_needs_no_home_install_or_workspace_config(self):
        launcher = self.install_launcher()
        env = dict(self.env, HOME=str(self.base / "empty-home"), WS="wrong-station")
        for action in ["status", "pull", "push"]:
            with self.subTest(action=action):
                r = subprocess.run(
                    [str(launcher), action],
                    check=False,
                    cwd=self.base,
                    env=env,
                    text=True,
                    capture_output=True,
                )
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                if action != "status":
                    self.assertIn("工位 qwen", r.stdout)

    def test_launcher_works_from_master_without_workspace_layout(self):
        self.install_launcher()
        for name in [*PARENTS, CHILD]:
            git(self.work / name, "switch", "-c", "master")
            git(self.work / name, "push", "-u", "origin", "master")
        master = self.base / "master"
        self.work.rename(master)
        launcher = master / "sunmoonun" / LAUNCHER.relative_to(ROOT)
        r = subprocess.run(
            [str(launcher), "pull"],
            check=False,
            env=dict(self.env, HOME=str(self.base / "empty-home")),
            text=True,
            capture_output=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("工位 master", r.stdout)

    def test_launcher_refuses_another_workspace_argument(self):
        launcher = self.install_launcher()
        r = subprocess.run(
            [str(launcher), "pull", "fable"],
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertEqual(r.returncode, 1)
        self.assertIn("范围须为", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
