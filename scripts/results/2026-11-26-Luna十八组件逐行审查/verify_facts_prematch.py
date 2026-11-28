"""从 Luna 根目录运行，两端使用相同的事实资料请求。"""
import json
import subprocess
from pathlib import Path

key = {"kind": "facts", "subject": "000858.SZ", "period_end": "2025-12-31",
       "codes": ["revenue"], "duration": "year"}
cases = {
    "knowfeed": """
import json,sys
from app.interfaces.http.internal.supply import DemandItemModel,item_in
from app.domain.supply.models import check_demand
item=item_in(DemandItemModel(confirmation_item="c1",readings=["table"],key=json.loads(sys.argv[1])))
check_demand("author","user","facts-demo-001",[item])
assert item.key.facts.codes==("revenue",)
""",
    "knowbench": """
import json,sys
from app.domain.workbench.supply_prematch import request_items
item={"ref":"c1","need_key":"financials","status":"to_confirm","key":json.loads(sys.argv[1])}
assert request_items([item],[])==[]
item["key"]={"subject":"000858.SZ","doc_type":"annual_report","period_end":"2025-12-31"}
assert len(request_items([item],[]))==1
""",
}
for service, code in cases.items():
    base = Path(f"{service}-app/{service}-backend/app").resolve()
    subprocess.run([base/".venv/bin/python", "-c", code, json.dumps(key)], cwd=base, check=True)
