"""Replay an unedited M02 model selection against pinned sources and fresh inputs.

Run with the KnowBench backend environment and its app directory on PYTHONPATH.
The catalog directory contains the author's Q01..Q04/S01-frozen.json receipts.
"""

import argparse
import hashlib
import json
import random
import sys
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

from app.domain.workbench.formal_method_compiler_generated import FrozenMethod
from app.domain.workbench.formal_method_generated import (
    FormalMethodDefinition,
    MethodRef,
)
from app.domain.workbench.formal_method_plan_generated import (
    bind_step_inputs,
    expand_unique_plan,
    export_outputs,
    validate_step_outputs,
)
from app.domain.workbench.incubation_selection import (
    Selection,
    expand,
    verify_selection_graph,
)
from app.domain.workbench.planning_capabilities import host_capabilities

ROOT = Path(__file__).resolve().parents[2]
MATERIALS = ROOT / "docs/总纲/专家方案设计/专家孵化方案/luna/M02验收样表/工具实现"
sys.path.insert(0, str(MATERIALS))
from author_cases import target, unique  # noqa: E402
from prepare import local_call, source  # noqa: E402

ROLES = {
    "opening_balance": ("Q01", ("B01", "B02", "B03")),
    "closing_balance": ("Q01", ("B04", "B05", "B06")),
    "profit": ("Q02", ("P01", "P02", "P03")),
    "cash": ("Q03", ("C03", "C01", "C02")),
    "inventory": ("Q04", ("I01", "I02")),
}
METHODS = ("Q01", "Q02", "Q03", "Q04", "S01")
TARGET = UUID("d0af395b-20aa-472b-b1c8-040a950e7789")


def replay(catalog, selection, seed, trials):
    flags = host_capabilities(True, True, True)
    pins, implementations = {}, {}
    for i, name in enumerate(METHODS, 1):
        row = json.loads((catalog / f"{name}-frozen.json").read_text())["version"]
        definition = FormalMethodDefinition.model_validate(row["definition"])
        pin = MethodRef.model_validate(
            {k: row[k] for k in ("method_id", "version", "digest")}
        )
        code = (
            (MATERIALS / "collect_checks.py").read_text()
            if name == "S01"
            else source(name)
        )
        assert definition.digest() == pin.digest
        assert (
            "sha256:" + hashlib.sha256(code.encode()).hexdigest()
            == definition.procedure.implementation.digest
        )
        implementations[pin] = code
        pins[f"m{i}"] = FrozenMethod(pin, definition)
    draft, roles = expand(selection, pins, None, flags["patterns"], required_cases={})
    definition = draft.definition
    resolved = {(f.reference.method_id, f.reference.version): f for f in pins.values()}
    verify_selection_graph(TARGET, definition, resolved, flags, roles)
    assert len(expand_unique_plan(TARGET, definition, resolved).leaf_nodes) == 6
    workers = {step.id: step for step in definition.procedure.steps}
    collector = definition.procedure.steps[-1]
    assert set(collector.inputs) == set(ROLES)
    rng = random.Random(seed)
    samples = []
    with TemporaryDirectory() as tmp:
        programs = {}
        for i, (pin, code) in enumerate(implementations.items()):
            path = Path(tmp) / f"tool{i}.py"
            path.write_text(code)
            programs[pin] = path
        for index in range(trials):
            values, rows, expected = {}, [], {}
            missing_role = rng.choice(list(ROLES)) if index % 3 == 2 else None
            for role, (name, ids) in ROLES.items():
                worker = workers[collector.inputs[role].binding.step]
                assert worker.candidates == (
                    pins[f"m{METHODS.index(name) + 1}"].reference,
                )
                metadata = {**target(name), "项目键": role}
                if name == "Q01":
                    metadata["时点"] = "期初" if role == "opening_balance" else "期末"
                port = worker.inputs["target"].binding.name
                if port in values and values[port] != metadata:
                    raise ValueError(f"{role}: plan conflates different caller targets")
                values[port] = metadata
                # Generate the expected difference first, then construct suitable source facts.
                delta = Decimal(rng.choice([-201, -100, 0, 100, 275])) / 100
                tail = [Decimal(rng.randrange(100, 90000)) / 100 for _ in ids[1:]]
                amounts = [sum(tail, delta), *tail]
                for j, (identity, amount) in enumerate(zip(ids, amounts, strict=True)):
                    if role != missing_role or j != len(ids) - 1:
                        rows.append(
                            {
                                **unique[identity],
                                "原单位": "元",
                                "披露精度": "0.01",
                                "原始金额": f"{amount:.2f}",
                            }
                        )
                expected[role] = (
                    None if role == missing_role else delta,
                    list(ids[:-1] if role == missing_role else ids),
                )
            rng.shuffle(rows)
            for role in ROLES:
                step = workers[collector.inputs[role].binding.step]
                port = step.inputs["rows"].binding.name
                assert port not in values or values[port] == rows
                values[port] = rows
            accepted = {}
            for step in definition.procedure.steps:
                args = bind_step_inputs(step, values, accepted)
                accepted[step.id] = validate_step_outputs(
                    step, local_call(programs[step.candidates[0]], args)
                )
            report = export_outputs(definition, accepted)["report"]
            assert report["应核"] == 5 and report["实核"] == (4 if missing_role else 5)
            for row in report["明细"]:
                delta, ids = expected.pop(row["项目键"])
                assert [r["证据编号"] for r in row["证据"]] == ids
                assert (
                    None if row["差额元"] is None else Decimal(row["差额元"])
                ) == delta
                assert row["状态"] == (
                    "未核验"
                    if delta is None
                    else "不平"
                    if abs(delta) > 1
                    else "阈值内"
                )
            assert not expected
            samples.append({k: report[k] for k in ("实核", "不平", "阈值内", "未核验")})
    return {
        "seed": seed,
        "trial_count": trials,
        "leaf_calls": 6 * trials,
        "reports": samples,
    }


if __name__ == "__main__":
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("catalog", type=Path)
    args.add_argument("selection", type=Path, help="An unmodified Selection JSON")
    args.add_argument("--seed", type=int, default=241124)
    args.add_argument("--trials", type=int, default=12)
    opts = args.parse_args()
    print(
        json.dumps(
            replay(
                opts.catalog,
                Selection.model_validate_json(opts.selection.read_text()),
                opts.seed,
                opts.trials,
            ),
            ensure_ascii=False,
            indent=2,
        )
    )
