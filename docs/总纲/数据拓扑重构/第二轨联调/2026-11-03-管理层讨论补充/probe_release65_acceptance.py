"""Pure in-process release probe; no DB, model calls, file writes or task changes.

Run with the knowbench backend's Python environment, or pass this file on stdin
to a deployed knowbench container. A successful probe is not business acceptance.
"""

import json

from app.application.workbench.acceptance import judge
from app.application.workbench.acceptance_numbers import _computed, _covers
from app.application.workbench.advisor import Advisor
from app.domain.workbench.packs import AcceptanceRule, StepContract


def main():
    results = []

    def record(name, passed):
        results.append({"check": name, "passed": bool(passed)})

    advice = AcceptanceRule(kind="no_positioning_advice")
    declaration = (
        "本文只描述数据，不评价好坏；不给买卖建议、评级、目标价，结论留给用户。"
    )
    content = {"report": declaration}
    result = judge(json.dumps(content, ensure_ascii=False), (advice,))
    record("negative_declaration_preserved", result.ok and result.parsed == content)
    for name, text in [
        ("actual_target_rejected", declaration + "目标价100元。"),
        ("actual_advice_rejected", declaration + "建议买入。"),
        ("ambiguous_negation_rejected", "不提供目标价，但可参考100元。"),
    ]:
        record(name, not judge(json.dumps({"report": text}), (advice,)).ok)
    record(
        "separate_field_not_exempt",
        not judge(
            json.dumps({"report": declaration, "other": "目标价100元"}), (advice,)
        ).ok,
    )
    syntax = AcceptanceRule(kind="json_object")
    malformed = judge('{"comparisons":[]', (syntax,))
    record(
        "missing_brace_rejected_with_diagnostic",
        not malformed.ok
        and malformed.parsed is None
        and "expected closing delimiters: }" in malformed.failures[0],
    )
    wrapped = judge('说明\n{"quote":"literal } and {"}\n结束', (syntax,))
    record(
        "braces_inside_quotes",
        wrapped.ok and wrapped.parsed == {"quote": "literal } and {"},
    )

    metric = AcceptanceRule(
        kind="each_has", path="rows", field="metric", values=("a", "b")
    )
    coverage = AcceptanceRule(
        kind="covers", path="comparisons", field="conclusion", source="up.claims"
    )
    computed = AcceptanceRule(kind="computed", path="rows", tolerance=0.005)
    rules = (syntax, metric, coverage, computed)
    step = StepContract(
        step_id="probe",
        title="Probe",
        method_text="Synthetic only",
        output_artifact="probe",
        acceptance=rules,
    )
    prompt = Advisor.compose(step, {}, {}, 0)
    marker = "## Acceptance rules for this frozen step\n"
    exposed = []
    if marker in prompt:
        encoded = prompt.split(marker, 1)[1].splitlines()[-1]
        exposed = [AcceptanceRule.model_validate(r) for r in json.loads(encoded)]
    record("first_attempt_receives_exact_rules", tuple(exposed) == rules)
    retry = Advisor.compose(step, {}, {}, 1, rework_failures=malformed.failures)
    record("retry_receives_specific_error", "expected closing delimiters: }" in retry)
    record(
        "altered_conclusion_still_rejected",
        bool(
            _covers(
                coverage,
                {"comparisons": [{"conclusion": "changed"}]},
                {"up": {"claims": ["original"]}},
            )
        ),
    )
    records = {"c1": {"value": "123.4567"}}
    record(
        "rounded_amount_accepted",
        not _computed(computed, [{"value": 123.46, "compute_id": "c1"}], records),
    )
    record(
        "wrong_amount_rejected",
        bool(_computed(computed, [{"value": 123.47, "compute_id": "c1"}], records)),
    )
    exact = "0.9154029126035511584400534399"
    precise_rule = AcceptanceRule(kind="computed", path="rows")
    decoded = judge(
        '{"rows":[{"value":' + exact + ',"compute_id":"c1"}]}', (precise_rule,)
    )
    record(
        "decimal_evidence_preserved",
        not _computed(precise_rule, decoded.parsed["rows"], {"c1": {"value": exact}}),
    )
    ok = all(row["passed"] for row in results)
    print(
        json.dumps(
            {
                "synthetic_only": True,
                "business_acceptance": False,
                "ok": ok,
                "checks": results,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
