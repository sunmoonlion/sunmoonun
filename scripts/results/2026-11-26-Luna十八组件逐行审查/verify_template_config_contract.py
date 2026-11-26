"""在模板后端运行；仅验证配置构造及方言建参，不建立连接。"""

import json

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import make_url
from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg

from app.domain.cross_app import APP, clean_origin, parse_sources, return_url
from core.config import Settings


def test_expanded_origin_fits_web_contract():
    template = "https://example.test/" + "a" * 800 + "?ref={ref}"
    sources = parse_sources(json.dumps({"knowbench": {"return_url": template}}))
    origin = clean_origin("knowbench", ":" * 128, known_apps=set(sources))
    assert len(return_url(sources["knowbench"], origin)) <= 1024


def test_template_web_profile_accepts_ipv6_loopback():
    settings = Settings(_env_file=None, web_frontend_base_url="http://[::1]:3000")
    assert settings.browser_profile("web").frontend_origins == ("http://[::1]:3000",)


def test_accepted_app_name_can_identify_a_cross_app_origin():
    try:
        settings = Settings(_env_file=None, app_slug="1lab")
    except ValidationError:
        return
    assert APP.fullmatch(settings.app_slug)


def test_ambiguous_service_bindings_rejected():
    settings = Settings(
        _env_file=None,
        service_auth_subject_bindings_json='{"alpha":["view"]," alpha ":["list"]}',
    )
    with pytest.raises(ValueError):
        _ = settings.service_auth_subject_bindings


def test_explicit_database_transport_policy_reaches_driver():
    settings = Settings(_env_file=None, migration_database_url="postgresql://localhost/sample?sslmode=require")
    _, arguments = PGDialect_asyncpg().create_connect_args(make_url(settings.migration_url))
    assert arguments.get("ssl") == "require"
