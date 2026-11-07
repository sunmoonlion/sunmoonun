"""Real local Git fixtures: alignment must preserve work and parent pins."""

import fcntl
import hashlib
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from test_switch_test_sync import git

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "docs/sync-cowork/align/workstation_align.py"


class AlignTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="workstation-align-")
        self.addCleanup(temp.cleanup)
        self.home = Path(temp.name)
        self.source = self.home / "worktrees/qwen"
        self.target = self.home / "worktrees/kimi"
        self.labels = ["sunmoonun", "app", "app/child"]
        for label in self.labels:
            p = self.source / label
            p.mkdir(parents=True, exist_ok=True)
            git(p, "init", "-b", "qwen")
            self.configure(p)
            git(p, "commit", "--allow-empty", "-m", "initial")
        p = self.source / "app"
        (p / ".gitmodules").write_text(
            '[submodule "child"]\npath = child\nurl = ./unused\n'
        )
        git(p, "add", ".gitmodules", "child")
        git(p, "commit", "-m", "pin child")
        for label in self.labels:
            p = self.target / label
            p.parent.mkdir(parents=True, exist_ok=True)
            git(self.home, "clone", str(self.source / label), str(p))
            self.configure(p)
            git(p, "switch", "-c", "kimi")

    def configure(self, p):
        for k, v in [
            ("user.name", "Test"),
            ("user.email", "test@example.invalid"),
            ("commit.gpgsign", "false"),
            ("core.hooksPath", "/dev/null"),
        ]:
            git(p, "config", k, v)

    def advance(self, label, root=None, filename="new"):
        p = (root or self.source) / label
        (p / filename).write_text(filename)
        git(p, "add", filename)
        git(p, "commit", "-m", filename)
        return git(p, "rev-parse", "HEAD")

    def align(self, success=True, check=False, workspaces=None, baseline="qwen"):
        r = subprocess.run(
            [
                "python3",
                str(ENGINE),
                baseline,
                "--home",
                str(self.home),
                "--repos",
                "sunmoonun",
                "app",
                "--workspaces",
                *(workspaces or ["qwen", "kimi"]),
                *(["--check"] if check else []),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0 if success else 1, r.stdout + r.stderr)
        return r.stdout + r.stderr

    def heads(self):
        return [git(self.target / name, "rev-parse", "HEAD") for name in self.labels]

    def test_fast_forward_children_and_preserve_branch_names(self):
        self.advance("sunmoonun")
        self.advance("app/child")
        git(self.source / "app", "add", "child")
        git(self.source / "app", "commit", "-m", "advance pin")
        self.align()
        for name in self.labels:
            self.assertEqual(
                git(self.target / name, "rev-parse", "HEAD"),
                git(self.source / name, "rev-parse", "HEAD"),
            )
            self.assertEqual(
                git(self.target / name, "branch", "--show-current"), "kimi"
            )
            self.assertEqual(git(self.target / name, "status", "--porcelain"), "")

    def test_late_divergence_moves_no_earlier_repo(self):
        before = self.heads()
        self.advance("sunmoonun")
        self.advance("app", self.target, "target-only")
        changed = self.heads()
        self.assertIn("基准未包含", self.align(success=False))
        self.assertEqual(self.heads(), changed)
        self.assertEqual(self.heads()[0], before[0])

    def test_dirty_child_blocks_entire_alignment(self):
        self.advance("sunmoonun")
        before = self.heads()
        (self.target / "app/child/untracked").write_text("keep")
        self.assertIn("未提交", self.align(success=False))
        self.assertEqual(self.heads(), before)

    def test_unpinned_source_child_refused(self):
        self.advance("app/child")
        before = self.heads()
        self.assertIn("未提交", self.align(success=False))
        self.assertEqual(self.heads(), before)

    def test_check_does_not_move_any_branch(self):
        self.advance("sunmoonun")
        before = self.heads()
        self.assertIn("检查通过", self.align(check=True))
        self.assertEqual(self.heads(), before)

    def test_missing_workstation_skipped_but_existing_missing_repo_refused(self):
        self.assertIn("跳过本机不存在", self.align(workspaces=["absent", "kimi"]))
        (self.home / "worktrees/empty").mkdir()
        self.assertIn("仓不存在", self.align(success=False, workspaces=["empty"]))

    def test_wrong_branch_refused(self):
        git(self.target / "sunmoonun", "switch", "-c", "other")
        self.assertIn("预期 kimi", self.align(success=False))

    def test_detached_child_reattached_without_losing_existing_branch(self):
        git(self.target / "app/child", "switch", "--detach")
        self.align()
        self.assertEqual(
            git(self.target / "app/child", "branch", "--show-current"), "kimi"
        )

    def test_added_submodule_requires_separate_initialization(self):
        self.advance("sunmoonun")
        p = self.source / "app"
        sha = git(p / "child", "rev-parse", "HEAD")
        git(p, "update-index", "--add", "--cacheinfo", f"160000,{sha},added")
        git(p, "commit", "-m", "new module")
        before = self.heads()
        self.align(success=False)
        self.assertEqual(self.heads(), before)

    def test_lock_shared_with_sync(self):
        key = hashlib.sha256(str(self.target.resolve()).encode()).hexdigest()
        lockpath = Path(tempfile.gettempdir()) / f"sunmoon-sync-{key}.lock"
        self.addCleanup(lockpath.unlink, missing_ok=True)
        with lockpath.open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertIn("已有同步或对齐", self.align(success=False))

    def test_invalid_baseline_and_external_symlink_refused(self):
        self.assertIn("无效工位", self.align(success=False, baseline="../qwen"))
        (self.home / "worktrees/alias").symlink_to(
            self.target, target_is_directory=True
        )
        self.assertIn("符号链接", self.align(success=False, workspaces=["alias"]))

    def test_shared_git_worktrees(self):
        other = self.home / "worktrees/fable"
        for label in self.labels:
            p = other / label
            p.parent.mkdir(parents=True, exist_ok=True)
            git(self.source / label, "worktree", "add", "-b", "fable", str(p))
        self.advance("sunmoonun")
        self.align(workspaces=["fable"])
        self.assertEqual(
            git(other / "sunmoonun", "rev-parse", "HEAD"),
            git(self.source / "sunmoonun", "rev-parse", "HEAD"),
        )

    def test_shell_entry_and_master_layout(self):
        master = self.home / "master/sunmoonun"
        master.parent.mkdir()
        git(self.home, "clone", str(self.source / "sunmoonun"), str(master))
        self.configure(master)
        git(master, "switch", "-c", "master")
        shutil.copytree(
            ROOT / "docs/sync-cowork/align", master / "docs/sync-cowork/align"
        )
        shutil.copytree(
            ROOT / "docs/sync-cowork/sync", master / "docs/sync-cowork/sync"
        )
        config = master / "docs/sync-cowork/align/config.sh"
        config.write_text("ALIGN_WORKSPACES=(qwen kimi)\nALIGN_REPOS=(sunmoonun app)\n")
        git(master, "add", "docs")
        git(master, "commit", "-m", "install tool")
        r = subprocess.run(
            ["bash", str(config.parent / "align.sh"), "qwen", "--check"],
            cwd="/tmp",
            env=dict(os.environ, WS="wrong"),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("检查通过", r.stdout)
