"""The published contract should include the actual typed internal request models."""
import json

from fastapi.routing import APIRoute
from pydantic import BaseModel
from test_user_library_contract import SCHEMA
from app.interfaces.endpoints import user_resolution_routes, user_run_routes


def test_typed_body_models_in_published_schema():
    definitions = json.loads(SCHEMA.read_text())["$defs"]
    missing = set()
    for router in (user_resolution_routes.router, user_run_routes.router):
        for route in router.routes:
            if isinstance(route, APIRoute) and route.body_field:
                model = route.body_field.field_info.annotation
                if isinstance(model, type) and issubclass(model, BaseModel):
                    if model.__name__ not in definitions:
                        missing.add(model.__name__)
    assert not missing, sorted(missing)
