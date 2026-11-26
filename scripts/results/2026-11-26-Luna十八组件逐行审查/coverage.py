"""核对已读区间并按组件统计。字节相同的源码共享已读区间。"""

import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def rows(name):
    with (HERE / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def main():
    sources = {
        (item["component"], item["path"]): item
        for item in rows("inventory.tsv")
        if item["kind"] == "source"
    }
    seen = defaultdict(set)
    for item in rows("reviewed.tsv"):
        source = sources[item["component"], item["path"]]
        start, end = int(item["first"]), int(item["last"])
        if not (1 <= start <= end <= int(source["lines"])):
            raise ValueError(f"行段越界 {source['path']}")
        if source["git_blob"] != item["git_blob"] or not item["observation"].strip():
            raise ValueError(f"版本或审查记录有误 {source['path']}")
        seen[item["git_blob"]].update(range(start, end + 1))

    total, covered = defaultdict(int), defaultdict(int)
    complete = 0
    distinct = {}
    for (component, _), source in sources.items():
        blob = source["git_blob"]
        length = int(source["lines"])
        distinct[blob] = length
        count = len(seen.get(blob, ()))
        total[component] += length
        covered[component] += count
        complete += int(count == length and length > 0)
    for name in sorted(total):
        print(f"{name}\t{covered[name]} / {total[name]}")
    print(f"组件源码 {sum(covered.values())} / {sum(total.values())}")
    print(f"去重源码 {sum(map(len, seen.values()))} / {sum(distinct.values())}")
    print(f"完整覆盖的非空文件 {complete}")


if __name__ == "__main__":
    main()
