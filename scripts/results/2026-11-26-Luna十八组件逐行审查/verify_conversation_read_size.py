"""A page of ordinary Chinese messages must fit the registered read transport."""
from unittest.mock import AsyncMock

import pytest

from app.domain.workbench.native_functions import PROJECT_READ, project_read_revision
from app.domain.workbench.records import page_of, record_of
from app.interfaces.mcp import workbench_mcp


@pytest.mark.asyncio
async def test_page_is_retrievable(monkeypatch):
    revision = project_read_revision()
    events = [{"type": "turn/requested", "payload": {"text": "数" * 1000}} for _ in range(40)]
    records = AsyncMock()
    page = page_of(record_of(events), 1)
    assert page["page"] == page["pages"] == 1
    records.read_conversation.return_value = {
        "conversation": "c", "kind": "work", "title": "摘要", **page
    }
    monkeypatch.setattr(workbench_mcp, "registered_functions",
                        AsyncMock(return_value={PROJECT_READ: (revision, None)}))
    receipt = {"id": "audit", "detail": {"operation": {
        "registered_source": revision.model_dump(exclude={"contract"})
    }}}
    response, status = await workbench_mcp.dispatch(
        records, 1, PROJECT_READ, {"task": "t", "conversation": "c"}, None,
        function=revision, receipt=receipt,
    )
    assert status == "succeeded", response["result"]["content"]
