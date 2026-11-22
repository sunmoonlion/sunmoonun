"""Join a real KnowBench gap and author/buyer handoffs to the real Lab and Mart runs."""

import asyncio
from contextlib import asynccontextmanager
import json
from pathlib import Path


class Lab:
    def __init__(self, peer):
        self.peer = peer

    async def send(self, doc):
        self.peer.stdin.write((json.dumps(doc) + "\n").encode())
        await self.peer.stdin.drain()
        raw = await asyncio.wait_for(self.peer.stdout.readline(), 60)
        if not raw:
            raise RuntimeError("KnowLab peer stopped")
        return json.loads(raw)

    async def submit(self, payload):
        return await self.send({"handoff": payload})

    async def freeze(self, db, ctx, request, version, *, missing=False):
        from test_formal_execution_db import status
        from test_public_expert_db import review_trial
        from app.domain.workbench.formal_method_admission_generated import (
            FrozenFormalMethod,
        )
        from app.domain.workbench.formal_method_execution_generated import (
            FormalMethodExecutionRequest,
        )
        from app.infrastructure.workbench.repository import WorkbenchRepository

        draft = ctx.request.draft.model_dump(mode="json", by_alias=True)
        if version == 2:
            draft["definition"]["capability_declaration"]["purpose"] += (
                " Include the approved receipt."
            )
        trial = await self.send(
            {
                "request": request,
                "owner": ctx.request.owner_subject,
                "missing": missing,
                "method": str(ctx.request.method_id),
                "version": version,
                "execution": ctx.request.execution.model_dump(mode="json"),
                "draft": draft,
            }
        )
        if missing:
            assert trial == {"missing": True}
            return
        ctx.request = FormalMethodExecutionRequest.model_validate(trial["trial"])
        assert str(ctx.request.request_id) == request
        if ctx.request.draft.source:
            from formal_recursive_support import accept_request, complete
            from app.application.workbench.test_runs import KnowbotTestConductor
            from app.bootstrap.workbench import workbench_stores

            original = ctx.factory

            def factory(repo):
                caps = original(repo)
                methods = caps.formal_sources
                (template,) = methods.business_reviews
                methods.business_reviews += (
                    template.model_copy(
                        update={
                            "method_id": ctx.request.method_id,
                            "suite_digest": ctx.request.execution.suite.digest,
                        }
                    ),
                )
                return caps

            ctx.factory = factory
            ctx.conductor = KnowbotTestConductor(
                workbench_stores(db), formal_capabilities=factory
            )
            await accept_request(db, ctx)
            await complete(db, ctx)
        else:
            await review_trial(db, ctx)
        result = await status(db, ctx.request, ctx.factory)
        assert result["status"] == "passed"
        response = await self.send(result)
        frozen = FrozenFormalMethod.model_validate(response["frozen"])
        assert (
            frozen.validation.model_dump(mode="json") == result["admission"]["receipt"]
        )
        async with db() as session:
            await ctx.factory(WorkbenchRepository(session)).formal_sources.register(
                frozen, caller="knowlab"
            )
        return frozen


@asynccontextmanager
async def lab_runtime():
    script = Path(__file__).with_name("expert_roundtrip_lab.py").resolve()
    root = script.parents[3] / "knowlab-app/knowlab-backend/app"
    peer = await asyncio.create_subprocess_exec(
        str(root / ".venv/bin/python"),
        str(script),
        cwd=root,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        limit=1024 * 1024,
    )
    try:
        yield Lab(peer)
    finally:
        peer.stdin.close()
        try:
            await asyncio.wait_for(peer.wait(), 15)
        except TimeoutError:
            peer.kill()
            await peer.wait()

    if peer.returncode:
        raise RuntimeError(f"KnowLab exited with status {peer.returncode}")


async def first_version(sessions, ctx, lab):
    from sqlalchemy import text
    from app.application.workbench.find_expert import FindExpertService
    from app.application.workbench.formal_handoff import Handoff, transfer
    from app.infrastructure.workbench.repository import WorkbenchRepository

    class EmptyMarket:
        async def planning_window(self, subject, start, limit):
            return [], False

    async with sessions() as sql:
        repo = WorkbenchRepository(sql)
        async with repo.transaction():
            env = await sql.scalar(
                text(
                    "SELECT id FROM workbench_environments WHERE owner_actor_id=:owner LIMIT 1"
                ),
                {"owner": ctx.owner},
            )
            project = await repo.create_project(
                owner_actor_id=ctx.owner,
                environment_id=str(env),
                workspace_root="/home/u/research",
                path="initial-gap",
                title="Initial gap",
            )
        registry = ctx.factory(repo).formal_sources.registry
        registry.methods.market = EmptyMarket()
        finder = FindExpertService(repo, formal_registry=registry, incubations=lab)
        from app.application.workbench.session_service import SessionService

        work = await SessionService(repo).start(
            owner_actor_id=ctx.owner, project_id=project, kind="work"
        )
        empty = await finder.start(
            owner_actor_id=ctx.owner,
            project_id=project,
            question="Please return a receipt",
            source_session=work["session_id"],
            idempotency_key="initial-gap",
            match_contract="knowbench/expert-match/v5",
            retain_empty=True,
        )
        origin = empty["task_id"]
        result = await finder.result(ctx.owner, origin)
        command = Handoff(
            review_digest=result["formal"]["review_digest"],
            gap="Need a two-step receipt expert.",
        )
        receipt = await transfer(finder, ctx.owner, origin, command)
        assert (
            receipt["mode"] == "new"
            and await transfer(finder, ctx.owner, origin, command) == receipt
        )
    from copy import copy
    from uuid import uuid4
    from app.domain.workbench.formal_method_execution_generated import (
        FormalMethodExecutionRequest,
    )

    tool = copy(ctx)
    tool.request = ctx.leaf_request.model_copy(update={"method_id": uuid4()})
    reference = ctx.leaf.reference.model_copy(
        update={"method_id": tool.request.method_id}
    )
    root = ctx.request.model_dump(mode="json", by_alias=True)
    for step in root["draft"]["definition"]["procedure"]["steps"]:
        step["candidates"] = [reference.model_dump(mode="json")]
    root["dependencies"] = [reference.model_dump(mode="json")]
    ctx.request = FormalMethodExecutionRequest.model_validate(root)
    await lab.freeze(sessions, ctx, receipt["request_id"], 1, missing=True)
    child = await lab.send({"tool_owner": tool.request.owner_subject})
    ctx.leaf = await lab.freeze(sessions, tool, child["request"], 1)
    assert ctx.leaf.reference == reference
    ctx.factory = tool.factory
    return await lab.freeze(sessions, ctx, receipt["request_id"], 1), origin
