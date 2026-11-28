"""用实际登记来源构造 agy 作者接口的 PATCH 请求。"""

import argparse
import json


def obj(**fields):
    return {
        "type": "object",
        "properties": fields,
        "required": list(fields),
        "additionalProperties": False,
    }


def array(item):
    return {"type": "array", "items": item}


text = {"type": "string", "minLength": 1, "pattern": r"\S"}
money = {"type": "string", "pattern": r"^(0|[1-9][0-9]{0,19})(\.[0-9]{1,6})?$"}
positive = {"type": "integer", "minimum": 1}
side = {"enum": ["customer", "supplier"]}
context = dict.fromkeys(("issuer", "period", "scope", "unit", "report"), text)
identity = {"anyOf": [obj(id=text, ref=text), {"type": "null"}]}
relation = {"anyOf": [obj(confirmed={"type": "boolean"}, ref=text), {"type": "null"}]}
row = obj(related=relation, rank=positive, amount=money, ref=text, identity=identity)
total = obj(metric={"enum": ["sales", "purchases"]}, amount=money, ref=text)
table = obj(**context, side=side, n=positive, ranked_rows=array(row), total=total)
fraction = {
    "anyOf": [{"type": "string", "pattern": "^[0-9]+/[1-9][0-9]*$"}, {"type": "null"}]
}
receipt = obj(
    related_amount=money,
    unknown_related_refs=array(text),
    disclosed_related_share=fraction,
    context=obj(**context),
    side=side,
    n=positive,
    metric=total["properties"]["metric"],
    count={"type": "integer", "minimum": 0},
    status={"enum": ["complete", "incomplete"]},
    sum=money,
    total=total,
    selected=array(row),
    disclosed_share=fraction,
    top_n_share=fraction,
)
ref_pair = obj(row_ref=text, identity_ref=text)
overlap = obj(
    customer=receipt,
    supplier=receipt,
    risk_rating={"const": "待定"},
    context=obj(**context),
    matches=array(obj(id=text, customer=ref_pair, supplier=ref_pair)),
    anonymous_refs=obj(customer=array(text), supplier=array(text)),
    coverage={"enum": ["complete", "partial"]},
)


def slot(schema, description):
    return {
        "description": description,
        "schema": schema,
        "required": True,
        "meaning": {"domain_id": "core.record.object"},
        "on_missing": "fail",
    }


rank_receipt = slot(receipt, "指定排名范围的集中度回执及有出处的披露明细")
tools = {
    "concentration": (
        "前 N 大交易对手集中度核算",
        "以同口径销售或采购总额核算对应排名的集中度",
        {"table": slot(table, "一个报告口径下已标注的客户或供应商排名表")},
        "receipt",
        rank_receipt,
        "分别核对原行、分母类型、覆盖数、精确分数与缺件状态",
    ),
    "overlap": (
        "前五大客户与供应商交叉复核",
        "交付两侧占比、已披露关联占比、双向身份依据及待定评级",
        {"customer": rank_receipt, "supplier": rank_receipt},
        "overlap",
        slot(overlap, "交叉命中及其两侧出处、未识别行与覆盖范围"),
        "逐项比对两侧的行和身份证据，匿名行单列，缺件时限制覆盖结论",
    ),
}


def permission(name):
    _, purpose, inputs, _, _, _ = tools[name]
    fields = list(inputs)
    return {
        "requirement_id": name,
        "capability_ref": "isolated-script",
        "version": "1",
        "operations": ["execute"],
        "resources": [],
        "data_transfer": {
            "destination": "https://sandbox-provisioner.sandbox-platform-dev.svc.cluster.local",
            "argument_fields": fields,
            "purpose": purpose,
        },
    }


def patch(name, source, revision):
    title, purpose, inputs, output, result, check = tools[name]
    fields = list(inputs)
    return {
        "revision": revision,
        "allowed_callers": ["host"],
        "source": source,
        "draft_contract": {
            "contract": "knowlab/method-draft/v2",
            "method_kind": "tool",
            "archetype_id": "S1",
            "title": title,
            "purpose": purpose,
            "applies_when": [
                "调用方提供同主体、同期间、同范围、同计量单位及同披露版本的结构化事实"
            ],
            "excludes": ["仅依据披露标注关联，风险等级待定，匿名序号仅在当表有效"],
            "expected_deliverables": [
                {
                    "promise_id": output,
                    "summary": result["description"],
                    "expected_domain_id": "core.record.object",
                    "expected_schema": result["schema"],
                }
            ],
            "access_ceiling": [permission(name)],
            "procedure": {
                "kind": "direct",
                "inputs": inputs,
                "outputs": {output: result},
                "instructions": purpose,
                "max_model_turns": 0,
                "stop_conditions": ["口径或证据不符时停止并返回原因"],
                "implementation": {
                    k: source[k]
                    for k in ("kind", "source", "version", "entry", "digest")
                }
                | {"requirement_ids": [name]},
            },
            "validation_rules": [
                {
                    "promise_id": output,
                    "outputs": [output],
                    "check": check,
                    "evidence": "独立期望与逐行披露出处",
                    "on_failure": "fail",
                }
            ],
            "approval_rules": [
                {
                    "requirement_id": name,
                    "operations": ["execute"],
                    "preview": fields,
                    "when": "每次执行前确认输入和报价",
                    "on_denied": "pause",
                }
            ],
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", choices=tools)
    parser.add_argument(
        "source",
        type=argparse.FileType("r"),
        help="该脚本在作者目录的 FormalMethodSource 回读 JSON",
    )
    parser.add_argument("revision", type=int)
    args = parser.parse_args()
    print(
        json.dumps(
            patch(args.name, json.load(args.source), args.revision),
            ensure_ascii=False,
            indent=2,
        )
    )
