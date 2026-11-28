"""分别在 KnowLab 和 KnowBench 后端虚拟环境运行，核对同一原件的两种读法。"""
import sys
from importlib import import_module

domain = {"bench": "workbench", "lab": "knowbots"}[sys.argv[1]]
request = import_module(f"app.domain.{domain}.data_request").DataRequest
plan = import_module(f"app.domain.{domain}.data_plan").plan
needs = []
items = []
for name in ("pages", "table"):
    needs.append(request.model_validate(dict(
        key=name, name=name, reading=name, period={"kind": "none"},
        doc_type="other", formats=["pdf"],
    )))
    items.append(dict(
        need_key=name, status="resolved", key={"doc_type": "other"},
        chosen=[dict(material_id="m", version_no=1, sha256="a" * 64,
                     rendition_kind=name, rendition_no=1,
                     rendition_sha256=("b" if name == "pages" else "c") * 64)],
    ))
for order in (items, items[::-1]):
    result = plan({"items": order}, needs)
    surviving = [pin["rendition_kind"] for pin in result.pins]
    print(domain, [item["need_key"] for item in order], surviving)
    assert surviving == [order[0]["need_key"]] and not result.missing and not result.problems
