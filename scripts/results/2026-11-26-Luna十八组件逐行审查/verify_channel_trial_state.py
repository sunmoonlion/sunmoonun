"""从 KnowFeed 后端 app 运行。用存储替身观察试采出错后的写回。"""
import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock

from app.application.supply.catalog import TrialRunner
from app.domain.supply.catalog import Trial
from app.domain.supply.models import Channel


def unavailable(channel):
    raise RuntimeError("local adapter initialization failed")


async def check():
    repo = AsyncMock()
    repo.start_trial.return_value = Trial("trial", "source", {}, "running", "author", datetime.now(UTC))
    repo.get_channel.return_value = Channel("source", "test", "web", "web", ("webpage",),
                                            ("text",), "self", "pending", 6, 200, 10)
    try:
        await TrialRunner(repo, unavailable).run("trial")
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected adapter construction error")
    repo.start_trial.assert_awaited_once()
    repo.finish_trial.assert_not_awaited()


asyncio.run(check())
