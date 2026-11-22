"""Exercise the guard with a real AsyncSession and an in-process HTTP transport."""

import asyncio
import os

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


def test_http_guard_at_transaction_boundaries():
    async def verify():
        engine = create_async_engine(
            make_url(os.environ["DELIVERY_TEST_DATABASE_URL"]).set(
                drivername="postgresql+asyncpg"
            )
        )
        sent = []

        def handle(request):
            sent.append(request)
            return httpx.Response(200)

        async def independent_request(client, started):
            await started.wait()
            await client.get("https://fixture.invalid")

        try:
            async with (
                AsyncSession(engine) as session,
                httpx.AsyncClient(transport=httpx.MockTransport(handle)) as client,
            ):
                started = asyncio.Event()
                sibling = asyncio.create_task(independent_request(client, started))
                try:
                    await session.execute(text("SELECT 1"))
                    started.set()
                    await sibling
                    with pytest.raises(AssertionError, match="Cross-service HTTP"):
                        await client.get("https://fixture.invalid")
                    await session.rollback()
                    async with session.begin():
                        with pytest.raises(AssertionError, match="Cross-service HTTP"):
                            await client.get("https://fixture.invalid")
                    await client.get("https://fixture.invalid")
                    assert len(sent) == 2
                finally:
                    sibling.cancel()
                    await asyncio.gather(sibling, return_exceptions=True)
        finally:
            await engine.dispose()

    asyncio.run(verify())
