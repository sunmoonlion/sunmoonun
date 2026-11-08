#!/usr/bin/env python3
"""One-machine Git handoff: bounded parallel reads, serial fast-forward/push writes."""

import argparse
import fcntl
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

DEFAULT_REPOS = [
    "sunmoonun",
    "knowfeed-app",
    "knowbench-app",
    "knowbase-app",
    "tpl-app",
    "knowlab-app",
    "knowmart-app",
    "sunmoon-link",
]
ENV = dict(os.environ, GIT_TERMINAL_PROMPT="0")
ENV.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o ConnectTimeout=10")
TIMEOUT = int(os.environ.get("SYNC_TIMEOUT", "120"))


class SyncError(Exception):
    pass


def redact(value):
    return re.sub(r"(https?://)[^/\s@]+@", r"\1<已删>@", value)


def git(path, *args, ok=True):
    try:
        r = subprocess.run(
            ["git", "-C", str(path), *args],
            check=False,
            capture_output=True,
            text=True,
            env=ENV,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired as exc:
        raise SyncError(
            f"{path.name}: git {args[0]} 超过 {TIMEOUT} 秒，已停止；请核对结果"
        ) from exc
    if ok and r.returncode:
        raise SyncError(f"{path}: git {args[0]} 失败：{redact(r.stderr.strip())}")
    return r.stdout.strip() if ok else r


def ancestor(path, old, new):
    r = git(path, "merge-base", "--is-ancestor", old, new, ok=False)
    if r.returncode not in (0, 1):
        raise SyncError(f"{path}: 无法核对提交祖先：{redact(r.stderr.strip())}")
    return r.returncode == 0


def ref(path, name):
    r = git(path, "rev-parse", "--verify", "--quiet", name, ok=False)
    return r.stdout.strip() if r.returncode == 0 else None


def links(path, commit):
    result = {}
    for entry in git(path, "ls-tree", "-rz", commit).split("\0"):
        if not entry:
            continue
        metadata, name = entry.split("\t", 1)
        mode, _, sha = metadata.split()
        if mode == "160000":
            result[name] = sha
    return result


@dataclass
class Repo:
    path: Path
    label: str
    head: str
    parent: object = None
    slot: str = ""
    target: str = ""


def select_repositories(root, names, target):
    """Select a registered root or a submodule reachable through committed gitlinks."""
    if target is None:
        return names, False
    parts = target.split("/")
    if any(part in ("", ".", "..") for part in parts) or parts[0] not in names:
        raise SyncError("范围须为 config.sh 中的仓名或其已登记子仓路径")
    current = parts[0]
    while True:
        path = root / current
        if root.resolve() not in path.resolve().parents:
            raise SyncError("所选仓路径超出当前工位")
        if current == target:
            return [target], target not in names
        if not (path / ".git").exists():
            raise SyncError(f"{current}: 仓不存在或子模块未初始化")
        candidates = [
            current + "/" + sub
            for sub in links(path, "HEAD")
            if target == current + "/" + sub
            or target.startswith(current + "/" + sub + "/")
        ]
        if not candidates:
            raise SyncError(f"{target}: 不是父仓已提交记录中的子模块")
        current = max(candidates, key=len)


def discover(root, names, branch, action, selected_submodule=False):
    repos = []

    def add(path, label, parent=None, slot=""):
        if not (path / ".git").exists():
            raise SyncError(f"{label}: 仓不存在或子模块未初始化，请先初始化再同步")
        if (
            path.resolve() != root.resolve()
            and root.resolve() not in path.resolve().parents
        ):
            raise SyncError(f"{label}: 路径超出当前工位")
        head = git(path, "rev-parse", "HEAD")
        current = git(path, "branch", "--show-current")
        status = git(path, "status", "--porcelain")
        if action != "status":
            if current != branch and not (
                (parent or selected_submodule) and not current
            ):
                raise SyncError(
                    f"{label}: 当前分支 {current or 'detached HEAD'}，预期 {branch}"
                )
            if status:
                raise SyncError(
                    f"{label}: 有未提交改动，请先自行检查和提交；同步不会自动提交"
                )
        repo = Repo(path, label, head, parent, slot)
        repos.append(repo)
        for sub in links(path, head):
            add(path / sub, label + "/" + sub, repo, sub)

    for name in names:
        add(root / name, name)
    return repos


def parallel(repos, work, jobs, label):
    errors = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {pool.submit(work, r): r for r in repos}
        for n, future in enumerate(as_completed(futures), 1):
            repo = futures[future]
            try:
                future.result()
                print(f"  [{n}/{len(repos)}] {label} {repo.label}", flush=True)
            except (SyncError, OSError) as exc:
                errors.append(str(exc))
    if errors:
        raise SyncError("\n".join(errors))


def unchanged(repos):
    for repo in repos:
        if git(repo.path, "rev-parse", "HEAD") != repo.head or git(
            repo.path, "status", "--porcelain"
        ):
            raise SyncError(f"{repo.label}: 检查期间本地发生变化，停止，未覆盖改动")


def pull(repos, branch, remote, jobs):
    # Exactly one normal fetch per repository; no second network request via pull.
    parallel(
        repos,
        lambda r: git(
            r.path,
            "fetch",
            "--quiet",
            "--prune",
            "--no-tags",
            "--no-recurse-submodules",
            remote,
        ),
        jobs,
        "已抓取",
    )
    for repo in repos:
        if repo.parent:
            repo.target = links(repo.parent.path, repo.parent.target)[repo.slot]
        else:
            repo.target = ref(repo.path, f"refs/remotes/{remote}/{branch}")
        if not repo.target:
            raise SyncError(f"{repo.label}: {remote}/{branch} 不存在")
        if not ref(repo.path, repo.target + "^{commit}"):
            # Newly published gitlink unreachable from configured fetch refs.
            git(
                repo.path,
                "fetch",
                "--quiet",
                "--no-tags",
                "--no-recurse-submodules",
                remote,
                repo.target,
            )
        if links(repo.path, repo.head).keys() != links(repo.path, repo.target).keys():
            raise SyncError(
                f"{repo.label}: 子模块结构改变，请先处理初始化后重跑；尚未合并"
            )
        for old in [repo.head, ref(repo.path, f"refs/heads/{branch}")]:
            if old and not ancestor(repo.path, old, repo.target):
                raise SyncError(
                    f"{repo.label}: 有未推提交、分叉或本地分支领先父仓指针；停止，不重置"
                )
    unchanged(repos)
    for repo in repos:
        # Parents are earlier in this list. Suppress implicit submodule checkout.
        current = git(repo.path, "branch", "--show-current")
        if not current:
            existing = ref(repo.path, f"refs/heads/{branch}")
            if existing:
                git(repo.path, "switch", "--quiet", branch)
            else:
                git(repo.path, "switch", "--quiet", "-c", branch)
        git(
            repo.path,
            "-c",
            "submodule.recurse=false",
            "merge",
            "--quiet",
            "--ff-only",
            repo.target,
        )
        if ref(repo.path, f"refs/remotes/{remote}/{branch}"):
            git(
                repo.path,
                "branch",
                "--quiet",
                "--set-upstream-to=" + remote + "/" + branch,
                branch,
            )
    for repo in repos:
        if git(repo.path, "rev-parse", "HEAD") != repo.target or git(
            repo.path, "status", "--porcelain"
        ):
            raise SyncError(f"{repo.label}: 更新后核对失败，请检查现场")


def push(repos, branch, remote, jobs):
    # Inspect every push endpoint, including mirrors. A failed lookup is not a missing branch.
    for repo in repos:
        if (
            repo.parent
            and links(repo.parent.path, repo.parent.head)[repo.slot] != repo.head
        ):
            raise SyncError(
                f"{repo.label}: 子仓 HEAD 与父仓已提交的 gitlink 不一致，请先确认并提交父仓指针"
            )
    plans = {}

    def inspect(repo):
        pending = []
        urls = git(
            repo.path, "remote", "get-url", "--push", "--all", remote
        ).splitlines()
        if not urls:
            raise SyncError(f"{repo.label}: 没有推送地址")
        for url in dict.fromkeys(urls):
            output = git(repo.path, "ls-remote", "--refs", url, f"refs/heads/{branch}")
            old = output.split()[0] if output else None
            if old == repo.head:
                continue
            if old:
                if not ref(repo.path, old + "^{commit}"):
                    git(
                        repo.path,
                        "fetch",
                        "--quiet",
                        "--no-tags",
                        "--no-recurse-submodules",
                        url,
                        f"refs/heads/{branch}",
                    )
                if not ancestor(repo.path, old, repo.head):
                    raise SyncError(
                        f"{repo.label}: 推送端有新提交或分叉，请先拉取处理；不 rebase、不强推"
                    )
            pending.append(url)
        plans[repo.label] = pending

    parallel(repos, inspect, jobs, "已核对推送端")
    unchanged(repos)
    count = 0
    # Deepest children first, roots last. Any child failure stops before all parents.
    for repo in sorted(repos, key=lambda r: r.label.count("/"), reverse=True):
        for url in plans[repo.label]:
            git(repo.path, "push", "--quiet", url, f"{repo.head}:refs/heads/{branch}")
            count += 1
        # Refresh our fetch-remote cache only if its address was also verified/pushed.
        fetch_url = git(repo.path, "remote", "get-url", remote)
        push_urls = git(
            repo.path, "remote", "get-url", "--push", "--all", remote
        ).splitlines()
        if fetch_url in push_urls:
            git(repo.path, "update-ref", f"refs/remotes/{remote}/{branch}", repo.head)
    print(f"实际推送 {count} 个仓/端点；其余已一致，跳过推送。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["pull", "push", "status"])
    parser.add_argument("--root", type=Path)
    parser.add_argument("--branch")
    parser.add_argument("--repos", nargs="+")
    parser.add_argument("--target", help="registered parent or parent/submodule path")
    args = parser.parse_args()
    ws = os.environ.get("WS", "")
    if not ws or not re.fullmatch(r"[A-Za-z0-9_.-]+", ws) or ws in (".", ".."):
        raise SyncError("必须指定有效工位，例如 WS=qwen；不猜工位、不批量同步全部工位")
    branch = args.branch or os.environ.get("BRANCH") or ws
    root = args.root or Path(
        os.environ.get("WORKTREE_ROOT", str(Path.home() / "worktrees" / ws))
    )
    git(root, "check-ref-format", "--branch", branch)
    if TIMEOUT <= 0:
        raise SyncError("SYNC_TIMEOUT 必须是正整数秒")
    names = args.repos or [os.environ.get("ROOT_REPO", "sunmoonun"), *DEFAULT_REPOS[1:]]
    jobs = int(os.environ.get("SYNC_JOBS", "4"))
    if not 1 <= jobs <= 16:
        raise SyncError("SYNC_JOBS 必须在 1–16 之间")
    remote = os.environ.get("GIT_REMOTE", "origin")
    start = time.monotonic()
    # One invocation per workstation; lock does not enter any Git working tree.
    lockname = (
        "sunmoon-sync-"
        + hashlib.sha256(str(root.resolve()).encode()).hexdigest()
        + ".lock"
    )
    with (Path(tempfile.gettempdir()) / lockname).open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SyncError("这个工位已有同步在运行") from exc
        selected, is_submodule = select_repositories(root, names, args.target)
        repos = discover(root, selected, branch, args.action, is_submodule)
        if args.action == "status":
            for repo in repos:
                print(repo.label, git(repo.path, "status", "--short", "--branch"))
            return
        print(
            f"{args.action}：工位 {ws}，分支 {branch}，范围 {args.target or '全部'}，"
            f"{len(repos)} 仓；并行联网 {jobs}，只操作本机与 Git。",
            flush=True,
        )
        if args.action == "pull":
            pull(repos, branch, remote, jobs)
        else:
            push(repos, branch, remote, jobs)
        print(f"同步完成，耗时 {time.monotonic() - start:.1f} 秒。", flush=True)
        if is_submodule:
            print(
                "本次未同步上级父仓；如需采用新的子仓版本，请另行核对、提交并推送父仓指针。"
            )
        if (
            args.action == "pull"
            and os.environ.get("ROOT_REPO", "sunmoonun") in selected
        ):
            cowork = (
                root
                / os.environ.get("ROOT_REPO", "sunmoonun")
                / "docs/sync-cowork"
            )
            print(f"协作请求入口：{cowork / 'requests'}（按明确指派查看；同步不派单）")
        elif args.action == "push":
            print("已推到 Git；对方开工前在自己的机器执行 pull。")


if __name__ == "__main__":
    try:
        main()
    except (SyncError, ValueError) as exc:
        print("同步停止：" + str(exc), file=sys.stderr)
        sys.exit(1)
