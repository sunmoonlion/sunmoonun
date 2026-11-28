"""An expert's qualifying verdict must concern the cases in the submitted test."""
from app.application.services.knowbot_service import KnowbotCreationService
from tests.knowbot_fakes import FakeRuntime, MemoryKnowlab, own_computer, result
from tests.test_knowbot_test_outputs import _testing


async def test_verdict_on_another_case_cannot_create_expert():
    repo, runtime = MemoryKnowlab(), FakeRuntime()
    own_computer(repo)
    service = KnowbotCreationService(repo, runtime)
    request, _, test = await _testing(service)
    submitted = runtime.started[-1][1]
    assert [case.case_id for case in submitted.cases] == ["c1"]
    case = result(test.run_id).cases[0].model_dump(mode="json")
    runtime.results[test.run_id] = result(
        test.run_id, "passed", cases=[{**case, "case_id": "other_case"}]
    )
    await service.refresh(str(test.id))
    assert not await repo.list_experts([request.id])
