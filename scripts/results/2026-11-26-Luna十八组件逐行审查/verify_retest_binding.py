"""用 KnowLab 的宿主服务和内存运行适配器核对重测实际发出的命令。"""
import asyncio

from app.application.errors.exceptions import BadRequestError
from app.domain.knowbots.lifecycle import RevisionIn
from tests.knowbot_fakes import OWNER, all_clear, manifest, platform_draft, request_body, result
from tests.test_knowbot_test_data import token, world


async def changed_case():
    svc, data, repo, runtime, kb, _, draft, test = await world.__wrapped__()
    [initial] = await data.pending(OWNER, str(test.id), token)
    kb.fetched = True
    await data.confirm(OWNER, initial["question_id"], token)
    runtime.results[test.run_id] = result(test.run_id, "error")
    await svc.refresh(str(test.id))
    body = request_body()
    body["cases"][0]["input"]["question"] = "分析另一家公司 2020 年报"
    revision = RevisionIn(idea=body["idea"], cases=body["cases"], consent_test_data=True)
    rid = str(draft.request_id)
    new = await svc.revise(OWNER, rid, revision)
    await svc.accept(rid, new.version, all_clear(), "admin-test")
    revised_draft = await platform_draft(svc, rid, manifest(), new.version)
    await svc.review_rules(str(revised_draft.id), "admin-test")
    await svc.start_test(str(revised_draft.id), budget_limit="20", timeout_seconds=600)
    sent = runtime.started[-1][1].cases[0]
    assert sent.input.question == body["cases"][0]["input"]["question"]
    assert [p.material_id for p in sent.data.items] == ["m-2025", "m-2024"]


async def empty_case():
    svc, data, repo, runtime, _, _, draft, test = await world.__wrapped__()
    [initial] = await data.pending(OWNER, str(test.id), token)
    await data.decline(OWNER, initial["question_id"])
    assert runtime.answers[-1][1].answers[0].data.items == ()
    runtime.results[test.run_id] = result(test.run_id, "error")
    await svc.refresh(str(test.id))
    assert repo.test_sets[-1].cases["c1"] == {"items":[]}
    await svc.start_test(str(draft.id), budget_limit="20", timeout_seconds=600)
    assert runtime.started[-1][1].cases[0].data is None


async def partially_revised():
    _, data, _, _, _, _, _, test = await world.__wrapped__()
    [shown] = await data.pending(OWNER, str(test.id), token)
    first = shown["needs"][0]
    try:
        await data.confirm(OWNER, shown["question_id"], token, needs=[first],
                           picks={shown["items"][0]["ref"]:{"material_id":"outdated","version_no":1}})
    except BadRequestError:
        pass
    else:
        raise AssertionError("Expected the unavailable material choice to be refused")
    [after] = await data.pending(OWNER, str(test.id), token)
    assert len(after["needs"]) == 2 and len(after["items"]) == 1
    assert after["items"][0]["need_key"] == first["key"]


if __name__ == "__main__":
    for case in (changed_case, empty_case, partially_revised):
        asyncio.run(case())
        print(case.__name__, "OK")
