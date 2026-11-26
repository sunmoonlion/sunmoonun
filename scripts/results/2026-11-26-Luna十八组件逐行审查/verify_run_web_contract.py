"""从 tpl-backend/app 用该项目 Python 执行；测试文件和 HTTP 响应仅暂存本机。"""

import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application.errors.exceptions import ConcurrencyConflictError
from app.application.services.web_interaction import _citation, _initial_snapshot
from app.interfaces.errors.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)


@app.get("/sample")
def conflict():
    raise ConcurrencyConflictError()


web = Path("../../tpl-web-frontend/app").resolve()
spec = """
import {readFileSync} from 'node:fs'
import {it, expect} from 'vitest'
import {fetchRunSnapshot, submitRunAction} from '@/lib/interaction/client'
import {runSnapshotSchema} from '@/contracts/interaction'
import {applyRunEvent,createRunProjection} from '@/lib/interaction/projection'
const {snapshot, error, citation} = JSON.parse(readFileSync(process.env.RUN_FIXTURE!, 'utf8'))
const respond = (body, status) => async () => Response.json(body, {status})
it('keeps the real backend error code', async () => {
  await expect(fetchRunSnapshot(snapshot.run_id, respond(error,409))).rejects.toMatchObject({code:'cursor_expired'})
})
it.each(['get','action'])('matches the %s response to the requested run', async (op) => {
  const id = crypto.randomUUID(), fetch = respond(snapshot,200)
  const result = op === 'get' ? fetchRunSnapshot(id, fetch) : submitRunAction(id, {contract_version:1,action_id:crypto.randomUUID(),value:'confirm'},'fixture',fetch)
  await expect(result).rejects.toMatchObject({code:'contract_invalid'})
})
it('can read its own projection after a full page of citations', () => {
  let p = createRunProjection(snapshot)
  for(let i=0;i<51;i++) {
    const id=crypto.randomUUID()
    p=applyRunEvent(p,{contract_version:1,run_id:snapshot.run_id,event_id:crypto.randomUUID(),occurred_at:snapshot.updated_at,sequence_no:i+2,type:'citation',data:{citation:{...citation,evidence_id:id,source_href:'/api/web/v1/citations/'+id+'/source'}}}).projection
  }
  expect(runSnapshotSchema.safeParse(p.snapshot).success).toBe(true)
})
"""
with TemporaryDirectory() as folder, NamedTemporaryFile(
    mode="w", dir=web / "tests/unit", suffix=".test.ts"
) as test:
    fixture = Path(folder) / "fixture.json"
    result = TestClient(app).get("/sample")
    assert result.status_code == 409
    fixture.write_text(json.dumps(dict(error=result.json(), snapshot=_initial_snapshot().model_dump(mode="json"), citation=_citation().model_dump(mode="json"))))
    test.write(spec)
    test.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", test.name, "tests/unit/interaction-client.test.ts", "tests/unit/run-projection.test.ts"], cwd=web, env={**os.environ,"RUN_FIXTURE":str(fixture)}, check=True)
