"""同一用户的一次慢提交和一次后继提交，各自的确认进度应独立。"""
from datetime import timedelta

from tests.test_supply_subscriptions_db import Subs, db as db


async def test_late_writer_overwrites_the_replacement_confirmation(db):
    s = Subs(db)
    repo, now = s.w.repo, s.w.clock.now
    key = "retry-lease"
    first, later = "1" * 64, "2" * 64
    assert await repo.claim_submission("alice", key, first, now) is None
    at = now + timedelta(minutes=6)
    assert await repo.claim_submission("alice", key, later, at) is None
    await repo.save_submission_progress("alice", key, {"confirmed": {"id": "first"}})
    resumed = await repo.claim_submission("alice", key, later, at)
    assert (resumed["digest"], resumed["resumed"]["confirmed"]["id"]) == (later, "first")
