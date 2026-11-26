"""在模板测试环境运行。MockTransport 返回带租户参数的正常发现文档。"""

from urllib.parse import parse_qs, urlsplit

import pytest
from test_oidc_security import client, exchanging

from app.application.errors.exceptions import ServiceUnavailableError


@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["login", "logout"])
async def test_navigation_preserves_provider_query(surface):
    field = "authorization_endpoint" if surface == "login" else "end_session_endpoint"
    endpoint = f"https://identity.example.test/{surface}?tenant=sample"
    oidc = client("web", "", None, {field: endpoint})
    if surface == "login":
        url = await oidc.build_authorization_url(state="s", nonce="n", code_challenge="c")
        required = "response_type"
    else:
        url = await oidc.end_session_url(post_logout_redirect_uri="https://web.example.test", state="s")
        required = "client_id"
    query = parse_qs(urlsplit(url).query)
    assert query["tenant"] == ["sample"] and required in query


@pytest.mark.asyncio
async def test_provider_outage_is_reported_as_unavailable():
    oidc = exchanging(503, {"error": "temporarily_unavailable"}, {})
    with pytest.raises(ServiceUnavailableError):
        await oidc.exchange_authorization_code_tokens(code="c", code_verifier="v", nonce="n")
