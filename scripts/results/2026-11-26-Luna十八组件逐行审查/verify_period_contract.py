"""Compare the schema consumed by planners with actual period expansion."""
import json
from datetime import date

from jsonschema import Draft202012Validator, ValidationError as SchemaError
from pydantic import ValidationError as ModelError
from app.domain.user_data import UserDataError
from test_data_request_contract import SCHEMA
from app.domain.user_resolution import TaskParams, expand, need_from
from app.interfaces.schemas.data_request import DataRequest


def test_schema_conforming_period_cannot_silently_drop_dates():
    payload = {
        "key": "annual", "name": "Annual report", "doc_type": "annual_report",
        "formats": ["pdf"],
        "period": {"kind": "none", "start": "2024-01-01", "end": "2024-12-31"},
    }
    try:
        Draft202012Validator(json.loads(SCHEMA.read_text())).validate(payload)
        request = DataRequest.model_validate(payload)
        need = need_from(request.model_dump(mode="json")).checked()
        selected, = expand(need, TaskParams(date(2026, 1, 1)))
    except (SchemaError, ModelError, UserDataError):
        return  # Rejecting the contradictory request also preserves the constraint.
    assert selected.key.period_start == date(2024, 1, 1)
    assert selected.key.period_end == date(2024, 12, 31)
