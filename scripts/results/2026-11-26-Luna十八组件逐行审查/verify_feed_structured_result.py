"""同一份业务结果换载体后，适配器仍应作同样的判断。"""
import json

import httpx
import pytest
from pydantic import SecretStr

from app.domain.supply.models import SupplyError
from app.infrastructure.external.wind import HttpWind
from tests.test_wind_mcp import Server


async def call(result):
    client = HttpWind(SecretStr("synthetic-key"), transport=httpx.MockTransport(Server(result=result)))
    return await client.call("financial_docs", "get_company_announcements", {"question": "synthetic"})


async def test_structured_failure_is_returned_as_data():
    failure = {"mcp_tool_error_code": 5, "mcp_tool_error_msg": "积分不足"}
    with pytest.raises(SupplyError) as exc:
        await call({"content": [{"type": "text", "text": json.dumps(failure, ensure_ascii=False)}]})
    assert exc.value.code == "provider_quota_exhausted"
    structured = {"structuredContent": failure}
    assert await call(structured) == structured


async def test_display_message_masks_nonempty_structured_data():
    payload = {"content": [{"type": "text", "text": "暂无数据"}],
               "structuredContent": {"data": {"rows": [{"value": 12}]}}}
    with pytest.raises(SupplyError) as exc:
        await call(payload)
    assert exc.value.code == "provider_no_results"
