"""Count complete plan expansions in a four-leaf execution on disposable PostgreSQL."""

from collections import Counter
from inspect import currentframe

from formal_plan_support import advance
from formal_recursive_support import setup_recursive
from test_formal_execution_db import approve
from test_workbench_ledger_db import db as db

from app.application.workbench import formal_recursive_runtime as runtime


async def test_four_leaf_tree(db, monkeypatch):
    calls = Counter()
    expand = runtime.expanded_plan

    def counted(snapshot):
        calls[currentframe().f_back.f_code.co_name] += 1
        return expand(snapshot)

    ctx = await setup_recursive(db)
    monkeypatch.setattr(runtime, "expanded_plan", counted)
    pending = await advance(db, ctx)
    for _ in range(4):
        await approve(db, ctx.request, ctx.factory, pending)
        pending = await advance(db, ctx)
    assert pending["status"] == "passed"
    assert len(ctx.remote.calls) == 4
    print("Full plan expansions by caller:", dict(calls))
    assert calls["_node"] > len(ctx.remote.calls)
