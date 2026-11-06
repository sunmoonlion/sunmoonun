"""Exercise both sync directions with real Git repos and a local SSH stand-in."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "sync-five-repos.sh"


def run(*args, **kwargs):
    return subprocess.run(args, text=True, capture_output=True, check=True, **kwargs)


def git(repo, *args):
    return run("git", "-C", str(repo), *args).stdout.strip()


class SyncTests(unittest.TestCase):
    def setUp(self):
        # The production script resolves layout paths against the real HOME.
        # Keep fixtures beneath it without replacing HOME or touching real repos.
        self.temp = tempfile.TemporaryDirectory(prefix=".sync-test-", dir=Path.home())
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.origin = self.root / "origin.git"
        run("git", "init", "--bare", str(self.origin))
        self.local = self.root / "local" / "fable" / "sample"
        self.remote = self.root / "remote" / "fable" / "sample"
        for repo in (self.local, self.remote):
            repo.parent.mkdir(parents=True)
            run("git", "clone", str(self.origin), str(repo))
            git(repo, "config", "user.name", "Sync Test")
            git(repo, "config", "user.email", "sync-test@example.invalid")
            git(repo, "config", "commit.gpgsign", "false")
            git(repo, "config", "core.hooksPath", "/dev/null")
            git(repo, "checkout", "-b", "fable")
        self.commit(self.local, "base")
        git(self.local, "push", "origin", "fable")
        git(self.remote, "pull", "--ff-only", "origin", "fable")

        layout = self.root / "layout.conf"
        relative_root = self.root.relative_to(Path.home())
        layout.write_text(
            f'LAYOUT_MASTER="{relative_root}/local"\n'
            f'LAYOUT_WORKTREES="{relative_root}/local"\n'
            'LAYOUT_WORKSPACES=(fable)\n'
        )
        config = self.root / "config.sh"
        config.write_text(
            'REMOTE_HOST=fixture\nREMOTE_USER=fixture\nREMOTE_PORT=22\n'
            'REMOTE_IDENTITY_FILE=/dev/null\nGIT_REMOTE=origin\n'
            f'LAYOUT_CONF="{layout}"\nREPOS=(sample)\n'
        )
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        ssh = bin_dir / "ssh"
        ssh.write_text(
            '#!/usr/bin/env python3\n'
            'import os, sys\n'
            'args = sys.argv[sys.argv.index("--") + 1:]\n'
            'args[0] = args[0].replace("/local/", "/remote/")\n'
            'os.execvp("bash", ["bash", "-s", "--", *args])\n'
        )
        ssh.chmod(0o755)
        self.env = dict(os.environ, FIVE_REPOS_CONFIG=str(config))
        self.env["PATH"] = str(bin_dir) + os.pathsep + self.env["PATH"]

    def commit(self, repo, message):
        git(repo, "commit", "--allow-empty", "-m", message)
        return git(repo, "rev-parse", "HEAD")

    def sync(self, direction, success=True):
        result = subprocess.run(
            [str(SCRIPT), direction, "fable"],
            env=self.env, text=True, capture_output=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def exercise(self, direction, scenario):
        source, target = (
            (self.local, self.remote) if direction == "to-remote"
            else (self.remote, self.local)
        )
        if scenario == "behind":
            expected = self.commit(target, "returned test results")
            git(target, "push", "origin", "fable")
        elif scenario == "ahead":
            expected = self.commit(source, "new work")
        elif scenario == "new":
            expected = git(source, "rev-parse", "HEAD")
            git(self.origin, "update-ref", "-d", "refs/heads/fable")
        elif scenario == "diverged":
            source_head = self.commit(source, "source work")
            target_head = self.commit(target, "target work")
            git(target, "push", "origin", "fable")
            self.sync(direction, success=False)
            self.assertEqual(git(source, "rev-parse", "HEAD"), source_head)
            self.assertEqual(git(target, "rev-parse", "HEAD"), target_head)
            self.assertEqual(git(self.origin, "rev-parse", "fable"), target_head)
            return
        self.sync(direction)
        for repo in (source, target):
            self.assertEqual(git(repo, "rev-parse", "HEAD"), expected)
            self.assertEqual(git(repo, "status", "--porcelain"), "")
        self.assertEqual(git(self.origin, "rev-parse", "fable"), expected)


for direction in ("to-remote", "from-remote"):
    for scenario in ("behind", "ahead", "new", "diverged"):
        def test(self, direction=direction, scenario=scenario):
            self.exercise(direction, scenario)
        setattr(SyncTests, f"test_{direction.replace('-', '_')}_{scenario}", test)


if __name__ == "__main__":
    unittest.main(verbosity=2)
