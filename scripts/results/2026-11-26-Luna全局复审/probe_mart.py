"""Follow one formal listing through license expiry and renewal using a simulated delivery service."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from tests.test_market_db import (
    OPS,
    OTHER,
    SELLER,
    approved_publisher,
    db as db,
    world as world,
)

from app.domain.market import FormalListingIn, LicenseIn, ReviewDecision
from app.infrastructure.repositories.market import SqlMarketRepository


@pytest.mark.asyncio
async def test_listing_after_expiry_and_renewal(world):
    category = "finance.securities_advisory"
    await approved_publisher(world)
    verify = AsyncMock(
        return_value={
            "title": "Synthetic formal tool",
            "method_kind": "tool",
            "purpose": "Review lifecycle",
            "skill_dependencies": [],
            "delivery_digest": "sha256:" + "c" * 64,
        }
    )

    async def license_until(expires, number):
        async with world.db() as session:
            svc, admin = world.svc(session), world.admin(session)
            doc = await svc.add_document(
                SELLER, "license", "application/pdf", b"%PDF-1"
            )
            lic = await svc.add_license(
                SELLER,
                LicenseIn(
                    category=category,
                    license_name="sample",
                    license_no=number,
                    valid_until=expires,
                    document_id=doc["document_id"],
                ),
            )
            await admin.decide_license(
                lic["license_id"], ReviewDecision(approve=True), OPS
            )

    async def visible():
        async with world.db() as session:
            rows, _ = await SqlMarketRepository(session).catalog_methods(
                OTHER,
                "tool",
                public=True,
                today=world.now.date(),
                words="",
                since=None,
                codes=None,
                sort="name",
                offset=0,
                limit=24,
            )
            return len(rows)

    await license_until(world.now.date() + timedelta(days=1), "1")
    async with world.db() as session:
        svc = world.svc(session)
        svc.public_market = True
        svc.formal_delivery = SimpleNamespace(check=verify)
        ref = {"method_id": str(uuid4()), "version": 1, "digest": "sha256:" + "a" * 64}
        pending = await svc.submit_formal(
            SELLER, FormalListingIn(reference=ref, category=category)
        )
        lid = UUID(pending["listing_id"])
        await svc.review_formal(OPS, lid, ReviewDecision(approve=True))
    assert await visible() == 1
    world.now += timedelta(days=3)
    async with world.db() as session:
        await world.admin(session).sweep()
    assert await visible() == 0
    async with world.db() as session:
        row = await SqlMarketRepository(session).formal_listing(lid, lock=False)
        assert row["status"] == "listed"
    await license_until(world.now.date() + timedelta(days=30), "2")
    assert await visible() == 1
