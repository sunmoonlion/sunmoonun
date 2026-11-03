"""Operation rehearsal in a disposable PostgreSQL schema; no remote calls."""

import asyncio
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest
from app.application.services.knowbot_service import KnowbotCreationService
from app.domain.knowbots.drafts import KnowbotRequestIn
from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
from tests.knowbot_fakes import OWNER, FakeRuntime, request_body
from tests.test_knowbot_repository_db import db as db

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "accepted_financial_operation", HERE / "create_accepted_financial_draft.py"
)
operation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(operation)
pytestmark = pytest.mark.asyncio


async def baseline(db):
    manifest = json.loads(
        (HERE.parent / "2026-11-03-勾稽原式修复/published-manifest.json").read_text()
    )
    async with db() as session:
        repo = SqlKnowlabRepository(session)
        request = await KnowbotCreationService(repo, FakeRuntime()).submit(
            OWNER,
            KnowbotRequestIn.model_validate(
                request_body(
                    mode="self",
                    budget_limit=None,
                )
            ),
        )
        async with repo.transaction():
            draft = await repo.create_draft(
                request_id=request.id,
                request_version=1,
                revision=8,
                version="2",
                manifest=manifest,
                mode="self",
            )
    return request, draft


async def test_real_freeze_bind_publish_and_lost_reply_replay(db):
    request, source = await baseline(db)
    async with db() as session:
        repo = SqlKnowlabRepository(session)
        result = await operation.create(
            repo,
            FakeRuntime(),
            owner=OWNER,
            source_draft_id=str(source.id),
            bundle=operation.load_bundle(),
        )
    async with db() as session:
        repo = SqlKnowlabRepository(session)
        replay = await operation.create(
            repo,
            FakeRuntime(),
            owner=OWNER,
            source_draft_id=str(source.id),
            bundle=operation.load_bundle(),
        )
        assert replay == result
        assert len(result["methods"]) == 8
        assert len(await repo.list_requests_for_owner(OWNER)) == 2
        assert len(await repo.list_methods(OWNER, limit=100, offset=0)) == 8
        assert (await repo.get_draft(source.id)) == source
        target = await repo.get_request(operation.UUID(result["request_id"]))
        assert target.cases == request.cases
        assert not await repo.list_tests(request_ids=[target.id])
        draft = await repo.get_draft(operation.UUID(result["draft_id"]))
        assert draft.status == "pending_test"
        assert (
            draft.manifest["pack"]["runtime_contract"] == "knowbench/dynamic-methods/v3"
        )
        # Consume the actual independent-method projection with knowbench's
        # runtime, not just the pre-binding author preview or a hand-built pack.
        runtime = HERE.parents[5] / "knowbench-app/knowbench-backend/app"
        completed = await asyncio.to_thread(
            subprocess.run,
            [
                str(runtime / ".venv/bin/python"),
                str(HERE / "verify_financial_plans.py"),
                "--stdin",
            ],
            input=json.dumps(draft.manifest),
            text=True,
            capture_output=True,
            cwd=runtime,
            env={**os.environ, "PYTHONPATH": str(runtime)},
            timeout=30,
        )
        assert completed.returncode == 0, completed.stderr
        report = json.loads(completed.stdout)
        assert report["independent_methods"] == 8
        assert len(report["checks"]) == 10
        assert all(check["passed"] for check in report["checks"].values())
        assert [
            len(report["cases"][case]["methods"])
            for case in (
                "annual_trend",
                "employee_revenue",
                "quarter_trend",
                "annual_with_forecast",
            )
        ] == [6, 6, 7, 8]


async def test_binding_failure_rolls_back_every_new_asset(db, monkeypatch):
    _, source = await baseline(db)
    original = operation.KnowbotMethodService.bind_version
    count = 0

    async def fail(self, *args, **kwargs):
        nonlocal count
        count += 1
        if count == 4:
            raise RuntimeError("injected binding interruption")
        return await original(self, *args, **kwargs)

    monkeypatch.setattr(operation.KnowbotMethodService, "bind_version", fail)
    async with db() as session:
        with pytest.raises(RuntimeError, match="injected"):
            await operation.create(
                SqlKnowlabRepository(session),
                FakeRuntime(),
                owner=OWNER,
                source_draft_id=str(source.id),
                bundle=operation.load_bundle(),
            )
    async with db() as session:
        repo = SqlKnowlabRepository(session)
        assert len(await repo.list_requests_for_owner(OWNER)) == 1
        assert not await repo.list_methods(OWNER, limit=100, offset=0)
        assert (await repo.get_draft(source.id)) == source


async def test_source_owner_and_manifest_must_match_before_creation(db):
    _, source = await baseline(db)
    async with db() as session:
        repo = SqlKnowlabRepository(session)
        with pytest.raises(ValueError, match="owner"):
            await operation.create(
                repo,
                FakeRuntime(),
                owner="different-user",
                source_draft_id=str(source.id),
                bundle=operation.load_bundle(),
            )
        body, acceptance, status, definitions = operation.load_bundle()
        status = {**status, "source_manifest_sha256": "0" * 64}
        with pytest.raises(ValueError, match="baseline"):
            await operation.create(
                repo,
                FakeRuntime(),
                owner=OWNER,
                source_draft_id=str(source.id),
                bundle=(body, acceptance, status, definitions),
            )
        assert len(await repo.list_requests_for_owner(OWNER)) == 1
