"""Compare standalone atomic method freezing with the persisted author service."""
from uuid import uuid4

from app.application.services.knowbot_methods import KnowbotMethodService
from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
from app.domain.knowbots.methods import freeze
from app.domain.knowbots.workdraft import WorkdraftBody
from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
from tests.dynamic_method_fixtures import body
from tests.knowbot_fakes import OWNER
from tests.test_atomic_methods import command
from tests.test_author_methods_db import source
from tests.test_knowbot_repository_db import db as db


async def test_independent_step_freezes_without_inventing_an_expert_plan(db):
    rid = await source(db)
    raw = body()
    steps = raw["steps"]
    steps[0]["why"] = "逐条保留输入集合"
    for step in steps:
        step.pop("selection")
    # Upstream first so even the ordinary workflow satisfies dependency ordering.
    steps[0], steps[1] = steps[1], steps[0]
    cmd = command().model_copy(update=dict(request_id=rid, revision=2,
        applies_when="需要确认输入条目无遗漏时", input_slots={"inspect": "records"},
        input_fields={"records": ("rows",)}, input_descriptions={"records": "待核对的条目"}))
    async with db() as session:
        repo = SqlKnowlabRepository(session)
        saved = await KnowbotWorkdraftService(repo).save(
            OWNER, str(rid), revision=1, edits=[("steps", steps), ("planning", None)])
        expected = freeze(WorkdraftBody.model_validate(saved.body), cmd)
        _, issues, _ = await KnowbotWorkdraftService(repo).preview(OWNER, str(rid))
        assert len(issues) == 1 and "固定 v2 专家已退役" in issues[0].message, issues
        record = await KnowbotMethodService(repo).publish(OWNER, str(uuid4()), 1, cmd)
        assert record.digest == expected.digest()
