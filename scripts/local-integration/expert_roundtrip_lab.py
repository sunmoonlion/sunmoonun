"""KnowLab side of the no-charge cross-application expert lifecycle check."""

import asyncio
import json
import sys
from pathlib import Path
from uuid import uuid4

sys.path[:0] = [str(Path.cwd()), str(Path.cwd() / "tests")]


def respond(doc):
    print(json.dumps(doc), flush=True)


async def main():
    from app.application.services.formal_methods import FormalMethodService
    from app.application.services.knowbot_service import KnowbotCreationService
    from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
    from app.domain.knowbots.drafts import KnowbotRequestIn
    from app.domain.knowbots.formal_method_admission import (
        FreezeFormalMethod,
    )
    from app.domain.knowbots.formal_method_execution import ExecuteFormalMethod
    from app.domain.knowbots.method_demand import FormalHandoff
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from tests.knowbot_fakes import request_body
    from tests.test_formal_method_service import Runtime
    from tests.test_knowbot_repository_db import db

    class RuntimePeer(Runtime):
        async def incubation_tool_versions(self, runtime, owner, **selection):
            return {"items": [], "next": None}

        async def submit_formal_method_execution(self, runtime, payload):
            self.validation_requests[payload.run_id] = payload
            respond({"trial": payload.model_dump(mode="json", by_alias=True)})
            self.result = json.loads(sys.stdin.readline())
            return self.result

        async def formal_method_execution(self, runtime, owner, run):
            assert run == self.result["run_id"]
            return self.result

        async def formal_method_validation(self, runtime, owner, run):
            assert run == self.result["run_id"]
            return self.result["admission"]

    schema = db.__wrapped__()
    sessions = await anext(schema)
    runtime = RuntimePeer()
    try:
        for line in sys.stdin:
            cmd = json.loads(line)
            async with sessions() as session:
                repo = SqlKnowlabRepository(session)
                svc = KnowbotCreationService(repo, runtime)
                drafts = KnowbotWorkdraftService(repo)
                if "tool_owner" in cmd:
                    request = await svc.submit(
                        cmd["tool_owner"],
                        KnowbotRequestIn.model_validate(request_body()),
                    )
                    respond({"request": str(request.id)})
                elif "handoff" in cmd:
                    body = FormalHandoff.model_validate(cmd["handoff"])
                    user = body.owner_subject
                    request, _ = await svc.submit_from_runtime(
                        user, body, runtime="knowbench"
                    )
                    again, created = await svc.submit_from_runtime(
                        user, body, runtime="knowbench"
                    )
                    assert (
                        again.id == request.id
                        and not created
                        and request.origin["task_id"] == str(body.task_id)
                    )
                    if request.origin["handoff"] == "user_demand":
                        assert await repo.get_workdraft(request.id) is None
                    respond(
                        {
                            "request_id": str(request.id),
                            "handoff": request.origin["handoff"],
                        }
                    )
                else:
                    owner = cmd["owner"]
                    request_id, version = cmd["request"], cmd["version"]
                    _, work = await drafts.get(owner, request_id)
                    await drafts.save(
                        owner,
                        request_id,
                        revision=work.revision if work else 0,
                        edits=[("formal_method", cmd["draft"])],
                    )
                    _, work = await drafts.get(owner, request_id)
                    spec = cmd["execution"]
                    spec["suite"].pop("digest")
                    spec["suite"]["suite_id"] = str(uuid4())
                    command = ExecuteFormalMethod.model_validate(
                        {
                            "request_id": request_id,
                            "revision": work.revision,
                            "run_id": str(uuid4()),
                            "execution": spec,
                        }
                    )
                    methods = FormalMethodService(repo, runtime)
                    mid = cmd["method"]
                    if cmd.get("missing"):
                        from app.application.errors.exceptions import NotFoundError

                        try:
                            await methods.execute(owner, mid, command)
                        except NotFoundError as exc:
                            assert exc.code == "method_not_found"
                            respond({"missing": True})
                            continue
                        raise AssertionError("An unregistered dependency cannot run")
                    await methods.execute(owner, mid, command)
                    freeze = FreezeFormalMethod(
                        request_id=command.request_id,
                        revision=work.revision,
                        run_id=command.run_id,
                        visibility="public",
                    )
                    record = await methods.freeze(owner, mid, version, freeze)
                    assert (
                        await methods.freeze(owner, mid, version, freeze)
                    ).digest == record.digest
                    frozen = runtime.registrations[(record.method_id, version)]
                    assert str(frozen.validation.request_id) == request_id
                    respond({"frozen": frozen.model_dump(mode="json", by_alias=True)})
    finally:
        await schema.aclose()


if __name__ == "__main__":
    asyncio.run(main())
