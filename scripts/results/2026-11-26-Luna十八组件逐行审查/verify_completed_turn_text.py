"""Exercise completion receipts on the production expert-turn collector."""

import asyncio

from app.application.workbench.runner import SandboxLink


async def test_completion_only_and_unidentified_fragments():
    link = object.__new__(SandboxLink)

    def collect(messages, final, *, planning):
        waiter = {
            "future": asyncio.get_running_loop().create_future(),
            "thread_id": "demo",
            "files": [],
            "text": None,
        }
        if planning:
            waiter["planning_messages"] = {}
        link.turn_waiters = {"round": waiter}
        for item in messages:
            link._feed_turn_waiters(
                "item/completed", {"threadId": "demo", "turnId": "round", "item": item}
            )
        link._feed_turn_waiters(
            "turn/completed",
            {
                "threadId": "demo",
                "turn": {"id": "round", "status": "completed", "items": final},
            },
        )
        assert waiter["future"].done()
        return waiter["text"]

    body = {"type": "agentMessage", "text": '{"decision":"gap"}'}
    assert collect([], [body], planning=False) is None
    assert collect([], [body], planning=True) is not None
    assert collect([body], [body], planning=True) is None
    identified = {**body, "id": "item"}
    assert collect([identified], [identified], planning=True) is not None
