"""Offline author review material. Never publishes, freezes assets, or writes DB.

Run with knowlab-backend/app's Python environment and PYTHONPATH. The source is
the recorded 2.8 manifest; the accepted content hash must remain stable when regenerating.
"""

import hashlib
import json
from pathlib import Path

from app.domain.knowbots.compile import compile_manifest, decompile, pack_problems
from app.domain.knowbots.workdraft import WorkdraftBody

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "2026-11-03-勾稽原式修复/published-manifest.json"


def prepare():
    source = json.loads(BASE.read_text())
    original, notes = decompile(source)
    if notes:
        raise ValueError(f"base import is lossy: {notes}")
    doc = original.model_dump(mode="json")
    doc["name"] = "财务分析与预测（动态候选）"
    doc["tagline"] = "按问题选择作者已确定的方法，交付可追溯的财务分析与预测"
    doc["scope"] = {
        "does": "分析一家上市公司的已披露年度或季度财务表现、财务指标与走势；员工人数口径可确立时计算年度人均创收；明确要求预测时，按季节性同比方法回测并预测营收、归母净利润。",
        "does_not": "不做估值、评级、目标价或买卖建议；不承诺未配置的预测算法、审计结论或任意行业研究。数据不足时说明和提出数据需求，不编数字。",
        "elsewhere": "问题超出这些能力时说明缺口，由用户选择其他专家、通用回答或孵化。",
    }
    conditions = {
        "scope": "每次受理都执行，明确问题主体、期间、口径和是否预测。",
        "inventory": "每次受理都执行，只盘点本题及已选方法需要的数据。",
        "reconcile": "使用报表数进行本题分析时执行，保持原四条恒等式和1元阈值。",
        "series": "问题涉及季度分析，或已选择季度预测与回测时执行；仅年度走势或年度人均创收不选。",
        "indicators": "每次受理都执行，计算本题所需指标并交回分析结论。",
        "official": "每次交回分析结论都执行，按作者既定管理层讨论规则逐条对照。",
        "forecast": "只有用户明确要求未来预测，且落在本专家已声明的季节性同比能力时选择。",
        "writeup": "每次受理都执行，只汇总实际选中且验收有效的方法成果并写Markdown。",
    }
    steps = {step["id"]: step for step in doc["steps"]}
    for key, step in steps.items():
        step["selection"] = {"applies_when": conditions[key], "required": key not in {"series", "forecast"}, "max_calls": 1}
    steps["indicators"]["uses"] = ["inventory", "reconcile", "series"]
    steps["indicators"]["input_required"] = {"inventory": True, "reconcile": True, "series": False}
    steps["writeup"]["input_required"] = {key: key not in {"series", "forecast"} for key in steps["writeup"]["uses"]}
    additions = {
        "inventory": "本题未选季度分析或预测时，不为未选方法索要季度数据、回测样本或未来期间。盘点已有授权数据；缺少数据走既有数据确认流程，查询Wind、加工已有原文和外部采集分别按真实状态处理。",
        "indicators": "年度分析直接消费inventory与reconcile；series是作者允许的可选输入，任务未选时明确说明本题不做单季换算，不当作缺数据，也不编造单季结果。问题要求人均创收时，只在营业收入与员工人数期间及统计范围相符后计算，明确期末人数或平均人数口径。",
        "writeup": "仅汇总本次计划实际绑定的有效成果。未选series或forecast时写本题未要求，不生成虚构预测表或把未选误报为数据缺失；选中的方法成果必须进入报告。",
    }
    for key, text in additions.items():
        steps[key]["rules"].append({"id": "dynamic_scope", "text": text})
    continuity = (
        "第四条只核同一存量科目的本期期初余额与上期期末余额，"
        "例如现金流量表期初现金与上期年末现金、资产负债表年初余额与上年年末余额。"
        "两端必须是同一时点、同一合并范围和同一可比口径；保留各自报告及页码。"
        "营业收入、归母净利润等期间流量不存在本条所指的期初余额；"
        "同一年度流量在两份报告中的原值与重述值比较属于版本差异，不能放入continuity清单。"
        "最新报告没有下一年报告不等于衔接未核验：读取本期报告的年初数与上一年度期末数。"
        "重述差异单独解释，按明确的可比来源链核本条，不能把原版与重述版的差额直接当作会计不平。"
    )
    for key in ("inventory", "reconcile"):
        steps[key]["rules"].append({"id": "opening_balance_continuity", "text": continuity})
    for key in ("reconcile", "series", "indicators", "forecast"):
        steps[key]["rules"].append({"id": "batch_compute", "text": "独立或可按顺序引用的计算优先使用compute的batch接口，按工具上限分批，每项仍保留原compute_id、原公式、真实输入和原验收精度。批量不改变方法、不放宽缺项与勾稽规则。"})
    capabilities = [
        ("annual_analysis", "年度财务走势、毛利率等已配置指标分析及管理层讨论核对", ["indicators", "official"], [{"method": "indicators", "field": "annual_metrics"}, {"method": "official", "field": "comparisons"}]),
        ("employee_revenue", "年度人均创收（营业收入除以同口径员工人数），说明期末或平均人数口径", ["indicators", "official"], [{"method": "indicators", "field": "amount_calculations"}, {"method": "official", "field": "comparisons"}]),
        ("quarter_analysis", "从累计披露还原利润表、现金流单季并分析季度走势", ["series", "indicators", "official"], [{"method": "series", "field": "single_quarters"}, {"method": "indicators", "field": "calculations"}]),
        ("seasonal_forecast", "营收和归母净利润的季节性同比区间预测，并先回测最近四个已披露单季", ["forecast"], [{"method": "forecast", "field": "forecast_rows"}, {"method": "forecast", "field": "backtest_rows"}]),
    ]
    doc["public_capabilities"] = [{"id": key, "statement": text, "conditions": ["上市公司披露报表口径；任务明确主体和分析期间，歧义先澄清", "预测限已声明的季节性同比方法，人均创收须说明人数统计口径"], "exclusions": ["不提供买卖建议、评级和目标价"], "delivers": ["带出处、计算依据和局限的Markdown报告"]} for key, text, _, _ in capabilities]
    doc["planning"] = {
        "method_text": "先根据用户问题与专家公开能力核范围；模型只选本专家已冻结的方法。必要方法与依赖不可省；年度题不选series/forecast，季度题选择series，明确要求预测才选forecast。实际选中上游必须绑定；未选可选输入标not_selected；写明每项未选原因。数据缺失不等于方法不支持，走既有数据确认流程，不擅自替换专家或算法。",
        "final_units": ["writeup"], "max_steps": 8, "max_replans": 2, "reserve": "0.05", "input_max_chars": 20000,
        "capability_bindings": {key: {"required_units": units, "evidence_outputs": outputs} for key, _, units, outputs in capabilities},
    }
    body = WorkdraftBody.model_validate(doc)
    manifest, problems = compile_manifest(body, {}, pack_id="financial-dynamic-candidate", version="1", runtime="knowbench", fallback_name=doc["name"])
    structural = pack_problems(manifest["pack"])
    if structural:
        raise ValueError(structural)
    def save(name, value):
        (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    accepted_file = HERE / "author-acceptance.json"
    accepted = json.loads(accepted_file.read_text()) if accepted_file.exists() else None
    body_hash = hashlib.sha256(json.dumps(body.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if accepted and accepted["accepted_workdraft_sha256"] != body_hash:
        raise ValueError("candidate changed after author acceptance; preserve accepted files")
    state = "author_accepted_pending_formal_creation" if accepted else "pending_author_acceptance"
    save("financial-workdraft-candidate.json", body.model_dump(mode="json"))
    save("financial-manifest-preview.json", manifest)
    save("financial-candidate-status.json", {"status": state, **({"author_acceptance": "author-acceptance.json"} if accepted else {}), "source_manifest_sha256": hashlib.sha256(json.dumps(source, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest(), "warnings": [{"path": p.path, "message": p.message} for p in problems], "structural_problems": [], "independent_method_ids": [], "published": False, "real_model_tested": False, "fixed_test11_semantic_issue": "continuity must mean opening balance versus previous closing balance, not comparisons between disclosure versions; actual forecast eligibility still requires review"})
    print(json.dumps({"status": state, "methods": len(body.steps), "capabilities": len(body.public_capabilities or ()), "warnings": len(problems)}))


if __name__ == "__main__":
    prepare()
