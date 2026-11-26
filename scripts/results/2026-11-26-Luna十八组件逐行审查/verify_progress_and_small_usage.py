"""Exercise the same step guard and metering projection used by the runner."""

from decimal import Decimal

from app.domain.workbench.pricing import Usage, conversation_usage, parse_prices
from app.domain.workbench.step_progress import StepProgressGuard
from app.application.workbench.runner import Runner, SandboxLink


def test_distinct_native_searches():
    guard = StepProgressGuard(0)
    for i, query in enumerate(("museum hours", "train departures", "admission prices")):
        guard.observe(
            "item/completed",
            {
                "id": str(i),
                "type": "webSearch",
                "query": query,
                "action": {"type": "search", "query": query},
            },
            i + 1,
        )
    assert guard.failure == "repeated_result"


def test_call_and_turn_rounding_disagree():
    prices = parse_prices(
        '{"models":{"example":{"input":"0.1","output":"4","cached_input":"0.1","cache_write":"1.25"}}}'
    )
    link = SandboxLink(
        Runner(
            None, connector=None, runner_id="example", publisher=None, prices=prices
        ),
        {"id": "sandbox"},
    )
    link.models["thread"] = "example"
    events = []
    for total in range(1, 11):
        payload = link.priced(
            "thread/tokenUsage/updated",
            {
                "threadId": "thread",
                "turnId": "turn",
                "tokenUsage": {
                    "total": {"inputTokens": total},
                    "last": {"inputTokens": 1},
                },
            },
        )
        events.append({"payload": payload})
    assert link.turn_usage["turn"] == Usage(input=10)
    assert Decimal(events[-1]["payload"]["cost"]["turn"]) == Decimal("0.000001")
    assert Decimal(conversation_usage(events, prices)["cost"]) == 0
