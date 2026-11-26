"""用同一组对象验证作者前端、KnowLab 和 KnowBench 的正式试跑边界。"""
import os
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory

web = Path('knowlab-app/knowlab-web-frontend/app').resolve()
js = """
import { expect, it } from 'vitest'
import { writeFileSync } from 'node:fs'
import { formalSuiteInputSchema } from '@/contracts/formal-method-execution'
it('checks the sample cases at the author boundary', () => {
  const sample = {case_id:'a', input:{values:{}}, repetitions:1, minimum_passes:1,
                  expected:{outcome:'succeeded',assertions:[{kind:'equals',pointer:'/a',value:1}]}}
  const suite = (cases) => formalSuiteInputSchema.parse({suite_id:'25d62fcd-b0f8-4905-9435-0b3d079ffb16',version:1,cases})
  const array = [{...sample,input:{values:{a:Array(22000).fill(1)}}}]
  const chinese = Array.from({length:10},(_,i)=>({...sample,case_id:'c'+i,input:{values:{a:'甲'.repeat(19000)}}}))
  const values = [suite(array),suite(chinese)]
  expect(values).toHaveLength(2)
  writeFileSync(process.env.LUNA_CASES!,JSON.stringify(values))
})
"""
py = """
import importlib,json,sys
from pydantic import ValidationError
mod = importlib.import_module(sys.argv[1])
cases = json.load(open(sys.argv[2]))
for case, reason in zip(cases, ['64000 bytes','1000000 bytes'], strict=True):
    try:
        mod.FormalTestSuiteDraft.model_validate(case).freeze()
    except ValidationError as exc:
        assert reason in str(exc), str(exc)
    else:
        raise AssertionError('Expected limit rejection')
a=mod.ApproxAssertion(kind='approx',pointer='/n',value=2**53,absolute_tolerance=0)
assert mod.check_output_assertions((a,),{'n':2**53+1})[0].passed
assert not mod.check_output_assertions((a,),{'n':2**53+2})[0].passed
print(sys.argv[1], 'confirmed both limit differences and a false positive at zero tolerance')
"""
with TemporaryDirectory() as d, NamedTemporaryFile(dir=web/'tests/component',mode='w',suffix='.test.tsx') as f:
    out = str(Path(d)/'accepted.json')
    f.write(js)
    f.flush()
    subprocess.run(['node_modules/.bin/vitest','run',f.name],cwd=web,env={**os.environ,'LUNA_CASES':out},check=True)
    for product, module in [('knowlab','knowbots.formal_method_execution'),('knowbench','workbench.formal_method_execution_generated')]:
        app = Path(f'{product}-app/{product}-backend/app').resolve()
        subprocess.run([app/'.venv/bin/python','-c',py,'app.domain.'+module,out],cwd=app,check=True)
