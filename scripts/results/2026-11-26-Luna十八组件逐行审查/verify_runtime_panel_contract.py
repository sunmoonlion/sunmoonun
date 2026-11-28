"""Check operator instructions against the assembled local ASGI API."""
from pathlib import Path

from app.main import app


def test_advertised_session_routes_absent():
    panel = (Path.cwd().parents[1] / "knowbench-admin-frontend/app/components/research/research-runtime-panel.tsx").read_text()
    routes = {route.path for route in app.routes}
    for tail in ("", "/{id}/runs", "/{id}/stream"):
        advertised = "/api/agent/sessions" + tail
        assert advertised in panel.replace("&#123;", "{").replace("&#125;", "}")
        assert advertised not in routes
    assert "/api/workbench/sessions" in routes


def test_package_operations_have_duplicate_identifiers():
    paths = app.openapi()["paths"]
    for path in ("/api/workbench/agent/package", "/api/agent-install/{credential}/package"):
        assert paths[path]["head"]["operationId"] == paths[path]["get"]["operationId"]
