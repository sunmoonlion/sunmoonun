"""对同一批事件分别调用工作台的服务端用量汇总及网页统计。"""
import json
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

backend = Path("knowbench-app/knowbench-backend/app").resolve()
frontend = Path("knowbench-app/knowbench-web-frontend/app").resolve()
tokens = dict(input=12, cached_input=0, cache_write=0, output=0, total=12)
def event(i, currency):
    payload = {"turnId": f"t{i}", "tokenUsage": {"last": {"inputTokens": 12}}}
    if currency:
        payload["cost"] = dict(currency=currency, model="test", priced=True,
                               call="1.00", turn="1.00", call_tokens=tokens,
                               turn_tokens=tokens, estimated=True)
    return {"type": "thread/tokenUsage/updated", "payload": payload}

events = [event(1,"USD"), event(2,"CNY"), event(3,None)]
script = """
import json, sys
from app.domain.workbench.pricing import conversation_usage, DEFAULT_PRICES
events = json.load(sys.stdin)
mix = conversation_usage(events[:2], DEFAULT_PRICES)
assert (mix['cost'], mix['price']['currency']) == ('2.00','CNY'), mix
partial = conversation_usage(events, DEFAULT_PRICES)
assert (partial['calls'], partial['tokens']['total'], partial['cost']) == (3,36,None), partial
"""
subprocess.run([backend/".venv/bin/python", "-c", script], cwd=backend,
               input=json.dumps(events), text=True, check=True)
test = """
import {it,expect} from 'vitest'
import {spent} from '@/features/usage/model/spent'
import type {ConversationEvent} from '@/contracts/workbench-v2'
const events = EVENTS as unknown as ConversationEvent[]
it('adds different currencies and skips the whole older unpriced event', () => {
  const projected = {currency:'CNY',calls:2,micros:2000000,tokens:24}
  expect(spent(events.slice(0,2))).toEqual(projected)
  expect(spent(events)).toEqual(projected)
})
"""
with NamedTemporaryFile(dir=frontend/"tests/unit", suffix=".test.ts",mode="w") as f:
    f.write(test.replace("EVENTS",json.dumps(events)))
    f.flush()
    subprocess.run(["node_modules/.bin/vitest","run",f.name],cwd=frontend,check=True)
