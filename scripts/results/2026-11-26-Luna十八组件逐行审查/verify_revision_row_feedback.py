"""Keep the row identity of failed and passed checks in the revision report."""
from dataclasses import replace

from app.domain.knowbots.drafts import KnowbotRequestIn
from tests.knowbot_fakes import OWNER, own_computer, request_body
from tests.test_knowbot_lab_extras import Wired, _finished_test


async def test_revision_distinguishes_which_year_failed():
    world = Wired()
    own_computer(world.repo)
    data = request_body(mode="self", budget_limit=None)
    case = data["cases"][0]
    original = case["expectations"][0]
    case["expectations"] = [
        {**original, "row": {"where": {"year": year}, "field": "ratio"}}
        for year in ["2024", "2025"]
    ]
    request = await world.svc.submit(OWNER, KnowbotRequestIn.model_validate(data))
    await _finished_test(world, request.id, 1, "failed")
    [test] = await world.repo.list_tests(request_ids=[request.id])
    report = test.report
    report["cases"][0]["expectations"] = [True, False]
    world.repo.tests[test.id] = replace(test, report=report)
    await world.inc.start(OWNER, str(request.id), action="revise", instruction="按报告改", with_test=True)
    checks = world.incubator.started[0].test_report.cases[0].expectations
    assert [check.passed for check in checks] == [True, False]
    locations = [check.model_dump(exclude={"passed"}) for check in checks]
    assert locations[0] != locations[1], locations
