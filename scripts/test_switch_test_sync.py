"""Regression checks for local result publishing, using disposable Git repos."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs/process/switch-test/human-remote.sh"
LOCAL_SCRIPT = ROOT / "docs/process/switch-test/human-local.sh"
ROOT_REPO = "sunmoonun"  # 根仓目录名，与 human-*.sh 的 ROOT_REPO 同步
# 与 human-*.sh 的 FIVE、SUBS 同一份（脚本要求每个仓都在）
PARENTS = (ROOT_REPO, "knowfeed-app", "knowbench-app", "knowbase-app", "tpl-app", "knowlab-app", "knowmart-app")
CHILDREN = tuple(
    f"{app}-app/{app}-{role}"
    for app in ("knowbench", "knowbase", "knowfeed", "tpl", "knowlab", "knowmart")
    for role in ("backend", "web-frontend", "admin-frontend")
)
LINK = "sunmoon-link"


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs)


def git(repo, *args):
    return run("git", "-C", str(repo), *args).stdout.strip()


class PublishTests(unittest.TestCase):
    BRANCH = "fable"  # 工位 fable 的分支；子类改成与工位不同名的分支

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="switch-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.worktrees = self.root / "worktrees" / "fable"
        self.origins = {}
        for name in (*PARENTS, LINK, *CHILDREN):
            origin = self.root / (name.replace("/", "-") + ".git")
            run("git", "init", "--bare", str(origin))
            self.origins[name] = origin
            repo = self.worktrees / name
            repo.parent.mkdir(parents=True, exist_ok=True)
            run("git", "clone", str(origin), str(repo))
            git(repo, "config", "user.name", "Sync Test")
            git(repo, "config", "user.email", "sync-test@example.invalid")
            git(repo, "config", "commit.gpgsign", "false")
            git(repo, "config", "core.hooksPath", "/dev/null")
            branch = "master" if name in CHILDREN else self.BRANCH
            git(repo, "checkout", "-b", branch)
            git(repo, "commit", "--allow-empty", "-m", "base")
            git(repo, "push", "origin", branch)
            if name in CHILDREN:
                git(repo, "checkout", "--detach")
        for parent in sorted({c.split("/")[0] for c in CHILDREN}):
            names = [c.split("/")[1] for c in CHILDREN if c.startswith(parent + "/")]
            repo = self.worktrees / parent
            (repo / ".gitmodules").write_text("".join(
                f'[submodule "{name}"]\n\tpath = {name}\n'
                f'\turl = {self.origins[parent + "/" + name]}\n'
                for name in names
            ))
            git(repo, "add", ".gitmodules", *names)
            git(repo, "commit", "-m", "record submodule")
            git(repo, "push", "origin", self.BRANCH)
        self.env = dict(
            os.environ,
            WORKTREE_ROOT=str(self.worktrees),
            SYNC_SCRIPT=str(self.root / "no-sync-script"),
            WS="fable",
        )
        self.env.pop("BRANCH", None)

    def publish(self, success=True):
        result = subprocess.run(
            ["bash", str(SCRIPT)], env=self.env, text=True, capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("本地回来了", result.stdout)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("本地回来了", result.stdout)
        return result

    def test_publish_rebases_onto_new_origin_commits(self):
        # 远程助手在本地跑测试期间又推了提交：回传要先叠上去再推，不应被非快进拒绝
        parent = self.worktrees / ROOT_REPO
        other = self.root / "other-k8s"
        run("git", "clone", "-q", "-b", self.BRANCH, str(self.origins[ROOT_REPO]), str(other))
        git(other, "config", "user.name", "Remote"); git(other, "config", "user.email", "remote@example.invalid")
        git(other, "config", "commit.gpgsign", "false")
        (other / "remote-note.txt").write_text("from remote\n")
        git(other, "add", "remote-note.txt"); git(other, "commit", "-q", "-m", "remote pushed meanwhile"); git(other, "push", "-q", "origin", self.BRANCH)
        (parent / "scripts").mkdir(exist_ok=True)
        (parent / "scripts" / "results.txt").write_text("local result\n")
        self.publish()
        head = git(parent, "rev-parse", "HEAD")
        self.assertEqual(git(parent, "ls-remote", "origin", "refs/heads/" + self.BRANCH).split()[0], head)
        self.assertIn("remote pushed meanwhile", git(parent, "log", "--oneline", "-3"))
        self.assertTrue((parent / "remote-note.txt").exists())

    def test_detached_children_without_local_fable(self):
        # 子仓有新结果时按 HEAD 推到工位分支，推完仍游离（没有新提交的子仓不推，见脚本第 2 步）
        for child in CHILDREN:
            (self.worktrees / child / "results.txt").write_text("child result\n")
        self.publish()
        for child in CHILDREN:
            repo = self.worktrees / child
            self.assertEqual(git(repo, "branch", "--show-current"), "")
            self.assertEqual(
                git(self.origins[child], "rev-parse", self.BRANCH),
                git(repo, "rev-parse", "HEAD"),
            )

    def test_new_child_commit_is_pushed_before_parent_gitlink(self):
        child = CHILDREN[0]
        repo = self.worktrees / child
        (repo / "results.txt").write_text("test evidence\n")
        # Reject a parent push if its gitlink has not already reached the child remote.
        hook = self.origins["knowbench-app"] / "hooks/pre-receive"
        hook.write_text(
            '#!/usr/bin/env bash\nset -euo pipefail\n'
            'while read -r old new ref; do\n'
            '  expected=$(git rev-parse "$new:knowbench-backend")\n'
            f'  actual=$(env -u GIT_DIR -u GIT_WORK_TREE git --git-dir="{self.origins[child]}" rev-parse {self.BRANCH})\n'
            '  test "$expected" = "$actual"\ndone\n'
        )
        hook.chmod(0o755)
        self.publish()
        child_head = git(repo, "rev-parse", "HEAD")
        self.assertEqual(git(self.origins[child], "rev-parse", self.BRANCH), child_head)
        self.assertEqual(
            git(self.origins["knowbench-app"], "rev-parse", self.BRANCH + ":knowbench-backend"),
            child_head,
        )

    def test_child_push_failure_stops_before_parent_commit(self):
        hook = self.origins[CHILDREN[0]] / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        (self.worktrees / CHILDREN[0] / "results.txt").write_text("needs a push\n")
        parent = self.worktrees / ROOT_REPO
        before = git(parent, "rev-parse", "HEAD")
        (parent / "local.txt").write_text("still uncommitted\n")
        self.publish(success=False)
        self.assertEqual(git(parent, "rev-parse", "HEAD"), before)
        self.assertEqual(git(self.origins[ROOT_REPO], "rev-parse", self.BRANCH), before)

    def test_wrong_named_child_branch_stops_before_commits(self):
        repo = self.worktrees / CHILDREN[0]
        git(repo, "checkout", "master")
        (repo / "local.txt").write_text("do not commit on master\n")
        before = git(repo, "rev-parse", "HEAD")
        self.publish(success=False)
        self.assertEqual(git(repo, "rev-parse", "HEAD"), before)

    def sync_stub(self):
        """sync-five-repos.sh 的替身：只记一笔被调过、照常成功。"""
        marker = self.root / "sync-called"
        stub = self.root / "sync-stub.sh"
        stub.write_text(f'#!/usr/bin/env bash\necho "$@" >> "{marker}"\n')
        stub.chmod(0o755)
        self.env["SYNC_SCRIPT"] = str(stub)
        return marker

    def test_sync_script_only_when_branch_is_the_workstation_name(self):
        # 同名照原来交给 sync-five-repos.sh；不同名不调它（它只认工位名），由脚本直接推
        marker = self.sync_stub()
        self.publish()
        if self.BRANCH == "fable":
            self.assertEqual(marker.read_text().split(), ["to-remote", "fable"])
        else:
            self.assertFalse(marker.exists())
            for parent in PARENTS:
                repo = self.worktrees / parent
                self.assertEqual(
                    git(self.origins[parent], "rev-parse", self.BRANCH),
                    git(repo, "rev-parse", "HEAD"),
                )

    def test_explicit_branch_must_match_checkouts(self):
        # BRANCH 写错（仓不在这个分支上）就停，不推不提交
        self.env["BRANCH"] = "some-other-branch"
        parent = self.worktrees / ROOT_REPO
        before = git(parent, "rev-parse", "HEAD")
        self.publish(success=False)
        self.assertEqual(git(parent, "rev-parse", "HEAD"), before)

    def test_local_pull_follows_branch(self):
        # human-local.sh：拉的是根仓当前所在的分支，子仓接回同名分支
        for child in CHILDREN:
            git(self.worktrees / child, "push", "-q", "origin", "HEAD:refs/heads/" + self.BRANCH)
        parent = self.worktrees / ROOT_REPO
        tools = parent / "docs/process/switch-test"
        tools.mkdir(parents=True)
        (tools / "human-local.sh").write_text(LOCAL_SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
        git(parent, "add", "docs"); git(parent, "commit", "-q", "-m", "tools"); git(parent, "push", "-q", "origin", self.BRANCH)
        other = self.root / "other-root"
        run("git", "clone", "-q", "-b", self.BRANCH, str(self.origins[ROOT_REPO]), str(other))
        git(other, "config", "user.name", "Remote"); git(other, "config", "user.email", "remote@example.invalid")
        git(other, "config", "commit.gpgsign", "false")
        (other / "remote-note.txt").write_text("from remote\n")
        git(other, "add", "remote-note.txt"); git(other, "commit", "-q", "-m", "remote pushed"); git(other, "push", "-q", "origin", self.BRANCH)
        env = dict(self.env, HOME=str(self.root))
        env.pop("WORKTREE_ROOT")
        result = subprocess.run(["bash", str(tools / "human-local.sh")], env=env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("同步完成", result.stdout)
        self.assertEqual(git(parent, "rev-parse", "HEAD"), git(self.origins[ROOT_REPO], "rev-parse", self.BRANCH))
        self.assertTrue((parent / "remote-note.txt").exists())
        for child in CHILDREN:
            self.assertEqual(git(self.worktrees / child, "branch", "--show-current"), self.BRANCH)


class PublishOnDifferentlyNamedBranchTests(PublishTests):
    """2026-11-06 起分支名可以和工位名不同（如 work/qwen-20261106）：同一组用例全部照跑。"""
    BRANCH = "work/fable-20261106"


if __name__ == "__main__":
    unittest.main(verbosity=2)
