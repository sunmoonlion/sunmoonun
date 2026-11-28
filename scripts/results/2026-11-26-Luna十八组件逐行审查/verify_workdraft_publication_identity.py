"""Exercise the author's normal routes with two tabs and a replayed publication."""
import uuid

from tests.test_knowbot_workdraft_routes import (
    CELLS, OWNER, WEB, WEB_SID, _mine, client, wired,
)


async def test_publish_corresponds_to_reviewed_preview(wired):
    service, repo = wired
    request = await _mine(service)
    base = f"/api/web/v1/knowbot-requests/{request.id}/workdraft"
    async with client() as browser:
        browser.cookies.set(WEB_SID, "member")
        first = await browser.post(base + "/cells", headers=WEB,
                                   json={"revision": 0, "cells": CELLS})
        assert first.status_code == 200
        preview = (await browser.get(base + "/preview")).json()["manifest"]
        changed = await browser.post(base + "/cells", headers=WEB, json={
            "revision": 1, "cells": [{"path": "name", "value": "另一窗口修改的名称"}]})
        assert changed.status_code == 200
        result = await browser.post(base + "/publish", headers=WEB)
        if result.status_code == 409:
            return
        assert result.status_code == 201
        actual = repo.drafts[uuid.UUID(result.json()["draft_id"])].manifest
        assert actual == preview, (actual["name"], preview["name"])


async def test_replayed_publication_has_one_draft(wired):
    service, repo = wired
    request = await _mine(service, OWNER)
    base = f"/api/web/v1/knowbot-requests/{request.id}/workdraft"
    async with client() as browser:
        browser.cookies.set(WEB_SID, "member")
        saved = await browser.post(base + "/cells", headers=WEB,
                                   json={"revision": 0, "cells": CELLS})
        assert saved.status_code == 200
        first = await browser.post(base + "/publish", headers=WEB)
        second = await browser.post(base + "/publish", headers=WEB)
        assert first.status_code == 201
        assert len(repo.drafts) == 1, (first.json(), second.json())


async def test_replacing_seed_preserves_selected_method_template(wired):
    from app.domain.knowbots.drafts import KnowbotRequestIn
    from tests.knowbot_fakes import request_body

    service, _ = wired
    form = request_body()
    form["idea"]["method_template"] = "checked_delivery/v1"
    request = await service.submit(OWNER, KnowbotRequestIn.model_validate(form))
    base = f"/api/web/v1/knowbot-requests/{request.id}/workdraft"
    async with client() as browser:
        browser.cookies.set(WEB_SID, "member")
        before = (await browser.get(base)).json()
        assert before["preferred_template"] == "checked_delivery/v1"
        result = await browser.post(base + "/seed-skill", headers=WEB,
                                    json={"skill": "逐项核对两期余额。"})
        assert result.status_code == 201
        after = (await browser.get(base)).json()
        assert after.get("preferred_template") == before["preferred_template"]


async def test_library_picks_respect_confirmed_brief():
    import copy
    import pytest
    from app.application.errors.exceptions import BadRequestError
    from app.application.services.knowbot_library import KnowbotLibraryService
    from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
    from tests.knowbot_fakes import FakeLibrary, MATERIAL, shelf_entry
    from tests.test_delivery_template import BINDING
    from tests.test_formal_method_execution import prepared
    from tests.test_knowbot_library import token

    repo, _, _, _, old = await prepared()
    works = KnowbotWorkdraftService(repo)
    rid = str(old.request_id)
    _, original = await works.get(OWNER, rid)
    method = copy.deepcopy(original.body["formal_method"])
    await works.save(OWNER, rid, revision=2, edits=[("formal_method", None)])
    await works.save(OWNER, rid, revision=3, edits=[("method_template", BINDING)])
    definition = method["definition"]
    definition["capability_declaration"]["purpose"] = BINDING["goal"]
    definition["capability_declaration"]["promises"]["template_delivery"] = BINDING["deliverable"]
    definition["how_to_validate"].append(dict(promise_id="template_delivery",
        outputs=["result"], check=BINDING["check"], evidence=BINDING["evidence"], on_failure="fail"))
    await works.save(OWNER, rid, revision=4, edits=[("formal_method", method)], confirm_brief=True)
    library = KnowbotLibraryService(repo, FakeLibrary([shelf_entry()]))
    with pytest.raises(BadRequestError, match="Withdraw"):
        await library.pick(OWNER, rid, revision=5, picks=[MATERIAL], user_token=token)
