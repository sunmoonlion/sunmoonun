"""在 KnowLab 后端 app 中用 PYTHONPATH=. 执行。"""
from app.application.errors.exceptions import BadRequestError
from app.application.services.knowbot_test_data import _revised

added = {"doc_type": "semiannual_report", "period": {"kind":"fixed","start":"2025-01-01","end":"2025-06-30"}}
existing = dict(added, key="u2", doc_type="annual_report")
assert _revised([existing], "case1")[0].key == "u2"
assert _revised([added], "case1")[0].key == "u1"
try:
    _revised([existing, added], "case1")
except BadRequestError as err:
    assert "each item needs its own key" in str(err)
else:
    raise AssertionError("expected generated key to collide with the existing key")
