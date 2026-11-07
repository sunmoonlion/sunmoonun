#!/usr/bin/env python3
"""Fast-forward configured workstations from one local committed baseline."""

import argparse
import fcntl
import hashlib
import re
import sys
import tempfile
from contextlib import ExitStack
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sync"))
from workstation_sync import (
    SyncError,
    ancestor,
    discover,
    git,
    links,
    ref,
    unchanged,
)


def workspace_root(home, name):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise SyncError(f"无效工位名：{name}")
    root = home / "master" if name == "master" else home / "worktrees" / name
    if root.resolve() != root.absolute():
        raise SyncError(f"{name}: 工位路径含符号链接，不自动跨目录对齐")
    return root


def lock_workspaces(stack, roots):
    for root in sorted(set(roots)):
        key = hashlib.sha256(str(root.resolve()).encode()).hexdigest()
        lock = stack.enter_context(
            (Path(tempfile.gettempdir()) / f"sunmoon-sync-{key}.lock").open("a")
        )
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise SyncError(f"{root.name}: 已有同步或对齐在运行") from exc


def run(home, baseline, workspaces, names, check=False):
    home = home.resolve()
    if not names or any(not re.fullmatch(r"[A-Za-z0-9_-]+", n) for n in names):
        raise SyncError("仓清单必须是非空的顶层仓名列表")
    if not workspaces:
        raise SyncError("目标工位清单不能为空")
    source_root = workspace_root(home, baseline)
    if not source_root.is_dir():
        raise SyncError(f"基准工位不存在：{baseline}")
    targets = {}
    for name in dict.fromkeys(workspaces):
        root = workspace_root(home, name)
        if name == baseline:
            continue
        if not root.exists():
            print(f"跳过本机不存在的工位：{name}", flush=True)
            continue
        targets[name] = root
    with ExitStack() as stack:
        lock_workspaces(stack, [source_root, *targets.values()])
        sources = discover(source_root, names, baseline, "align")
        for r in sources:
            if r.parent and links(r.parent.path, r.parent.head)[r.slot] != r.head:
                raise SyncError(f"基准 {r.label}: 子仓未钉入父仓")
        source_by_label = {r.label: r for r in sources}
        plans = []
        # Fetch only from local paths. Inspect every destination before moving any branch.
        for branch, root in targets.items():
            repos = discover(root, names, branch, "align")
            if {r.label for r in repos} != set(source_by_label):
                raise SyncError(f"{branch}: 子模块结构不同，请单独处理后重跑")
            for r in repos:
                source = source_by_label[r.label]
                r.target = source.head
                if not ref(r.path, r.target + "^{commit}"):
                    git(
                        r.path,
                        "fetch",
                        "--quiet",
                        "--no-tags",
                        "--no-recurse-submodules",
                        str(source.path),
                        source.head,
                    )
                for old in [r.head, ref(r.path, f"refs/heads/{branch}")]:
                    if old and not ancestor(r.path, old, r.target):
                        raise SyncError(
                            f"{branch}/{r.label}: 有基准未包含的提交（领先或分叉），"
                            "请先合入基准；未移动任何分支"
                        )
                print(
                    f"{branch}/{r.label}: {r.head[:8]} → {r.target[:8]}"
                    + ("（已一致）" if r.head == r.target else ""),
                    flush=True,
                )
            plans.append((branch, repos))
        unchanged(sources)
        for _, repos in plans:
            unchanged(repos)
        if check:
            print("检查通过；未移动分支。仅可能从本机基准读取 Git 对象。")
            return
        completed = []
        try:
            for branch, repos in plans:
                for r in repos:
                    if git(r.path, "rev-parse", "HEAD") != r.head:
                        raise SyncError(f"{branch}/{r.label}: 执行期间提交改变")
                    current = git(r.path, "branch", "--show-current")
                    if current and current != branch:
                        raise SyncError(f"{branch}/{r.label}: 执行期间分支改变")
                    if not current:
                        args = (
                            [branch]
                            if ref(r.path, f"refs/heads/{branch}")
                            else ["-c", branch]
                        )
                        git(r.path, "switch", "--quiet", *args)
                    git(
                        r.path,
                        "-c",
                        "submodule.recurse=false",
                        "merge",
                        "--quiet",
                        "--ff-only",
                        r.target,
                    )
                    completed.append(f"{branch}/{r.label}")
                for r in repos:
                    if git(r.path, "rev-parse", "HEAD") != r.target or git(
                        r.path, "status", "--porcelain"
                    ):
                        raise SyncError(f"{branch}/{r.label}: 对齐后核对失败")
            unchanged(sources)
        except (SyncError, OSError) as exc:
            raise SyncError(
                f"{exc}\n已处理：{', '.join(completed) or '无'}；"
                "不自动回滚，请核对现场后重跑。"
            ) from exc
        print(
            f"完成：以 {baseline} 为基准，对齐 {len(plans)} 个工位、"
            f"{len(completed)} 个仓；保留各工位分支，未提交、未推送。"
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--home", type=Path, required=True)
    parser.add_argument("--workspaces", nargs="*", required=True)
    parser.add_argument("--repos", nargs="*", required=True)
    args = parser.parse_args()
    run(args.home, args.baseline, args.workspaces, args.repos, args.check)


if __name__ == "__main__":
    try:
        main()
    except (SyncError, ValueError, OSError) as exc:
        print("对齐停止：" + str(exc), file=sys.stderr)
        sys.exit(1)
