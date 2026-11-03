"""Synthetic probe of proposed formula rules; not an accepted expert or financial test."""
import json
from pathlib import Path
from app.application.workbench.acceptance_numbers import _computed
from app.domain.workbench.packs import AcceptanceRule

rules = json.loads(Path(__file__).with_name("reconcile-proposed-formula-rules.json").read_text())["rules"]
results = []
for raw in rules:
    rule = AcceptanceRule.model_validate(raw)
    row = {"value": 0, "compute_id": "synthetic"}
    cases = [
        ("original_formula", {"expression": rule.expression, "value": "0"}, True),
        ("substituted_total_comparison", {"expression": "A-TOTAL", "value": "0"}, False),
        ("reported_zero_but_nonzero_record", {"expression": rule.expression, "value": "2"}, False),
    ]
    for name, record, expected in cases:
        failures = _computed(rule, [row], {"synthetic": record})
        actual = not failures
        assert actual == expected, (rule.path, name, failures)
        results.append({"path": rule.path, "case": name, "accepted": actual})
print(json.dumps({"synthetic": True, "checks": len(results), "results": results,
                  "limits": "Formula and recorded value only; no claim of coverage, operand semantics, classification or live expert acceptance."}, ensure_ascii=False))
