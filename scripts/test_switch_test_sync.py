"""Disposable real-Git regression tests for the single-machine handoff."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "docs/process/switch-test/workstation_sync.py"
LAUNCHER = ROOT / "docs/process/switch-test/sync-five-repos.sh"
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

    def sync(self, action, success=True):
        r = subprocess.run(
            [
                "python3",
                str(ENGINE),
                action,
                "--root",
                str(self.work),
                "--repos",
                *PARENTS,
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

    def test_human_entries_share_the_same_engine(self):
        for name in ["human-local.sh", "human-remote.sh"]:
            r = subprocess.run(
                [
                    "bash",
                    str(ENGINE.with_name(name)),
                    "--root",
                    str(self.work),
                    "--repos",
                    *PARENTS,
                ],
                check=False,
                env=self.env,
                text=True,
                capture_output=True,
            )
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("同步完成", r.stdout)

    def test_launcher_needs_no_ssh_configuration(self):
        tools = self.work / "sunmoonun/docs/process/switch-test"
        tools.mkdir(parents=True)
        shutil.copy2(ENGINE, tools / ENGINE.name)
        config = self.base / "config.sh"
        layout = self.base / "layout.conf"
        layout.write_text(
            "LAYOUT_MASTER=master\nLAYOUT_WORKTREES=worktrees\nLAYOUT_WORKSPACES=(qwen)\n"
        )
        config.write_text(
            f'GIT_REMOTE=origin\nLAYOUT_CONF="{layout}"\ndeclare -A BRANCHES=()\nREPOS=(sunmoonun sample-app sunmoon-link)\n'
        )
        env = dict(self.env, HOME=str(self.base), FIVE_REPOS_CONFIG=str(config))
        r = subprocess.run(
            ["bash", str(LAUNCHER), "status", "qwen"],
            check=False,
            env=env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
