"""让工作台网页处理真实 facts 定义，再将编辑后的 wire JSON 交给服务端。"""
import json
import os
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory, NamedTemporaryFile

from app.application.workbench.expert_data import _revised
from app.domain.workbench.data_request import parse_need
from app.domain.workbench.errors import DataChoiceInvalid

facts = dict(kind="facts", key="profit", name="利润", subject="000858.SZ",
             start="2025-01-01", end="2025-12-31", codes=["IS.REVENUE"])
source = parse_need(facts).model_dump(mode="json")
app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
test = """
import fs from 'node:fs'
import {expect,it} from 'vitest'
import {taskDataSchema} from '@/contracts/workbench-v2'
import {confirmBody,noChanges} from '@/lib/workbench/task-data'
it('add one document to a pending facts request', () => {
  const snap = taskDataSchema.parse({listed:true,requests:[{id:'r1',labels:['利润'],status:'pending',needs:[FACTS]}]})
  const body = confirmBody(snap.requests[0],{...noChanges,
    added:[{doc_type:'annual_report',from:2025,to:2025,subject:null}]})
  expect(body.needs).toHaveLength(2)
  fs.writeFileSync(process.env.ROUNDTRIP_OUTPUT!,JSON.stringify(body.needs))
})
"""
with TemporaryDirectory() as directory, NamedTemporaryFile(mode="w",dir=app/"tests/unit",suffix=".test.ts") as f:
    output = Path(directory)/"needs.json"
    f.write(test.replace("FACTS", json.dumps(source)))
    f.flush()
    run(["node_modules/.bin/vitest","run",f.name],cwd=app,
        env=dict(os.environ,ROUNDTRIP_OUTPUT=str(output)),check=True)
    needs = json.loads(output.read_text())
    try:
        _revised(needs,"r1")
    except DataChoiceInvalid as exc:
        assert "reading" in str(exc)
    else:
        raise AssertionError("expected a rejected wire contract")
    assert needs[0].pop("reading") == "original"
    assert len(_revised(needs,"r1")) == 2
