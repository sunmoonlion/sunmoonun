"""以正常完成、部分失败、删除后重建等事件核对工作台对用户展示的记录。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
tests = app / "tests/unit"
cases = r"""
import { expect, it } from 'vitest'
import { splitArtifact, byFile } from '@/lib/workbench/timeline'
import { changeStep, commandStep, dataStep, relativeTo } from '@/lib/workbench/items'
it('drops the second line of a qualified delivery before a JSON block', () => {
  const result = splitArtifact('对齐金额。\n缺两行数据，仅供自查。\n{"total":100}')
  expect(result).toEqual({summary:'对齐金额。', raw:'{"total":100}'})
})
it('reports a restored file as deleted', () => {
  const file = {path:'report',added:0,removed:1,diff:'-old',how:'delete' as const}
  expect(byFile([file,{...file,added:1,removed:0,diff:'+new',how:'add'}])[0].how).toBe('delete')
})
it('ignores failed command status without exit code', () => {
  expect(commandStep({id:'c',status:'failed',exitCode:null},false).failed).toBe(false)
})
it('drops structured results and does not surface a tool-level error', () => {
  const result = dataStep({id:'r',status:'completed',result:{content:[],structuredContent:{reason:'missing'},isError:true}},false)
  expect(result).toMatchObject({failed:false,result:''})
})
it('undercounts actual edits starting with repeated signs inside a hunk', () => {
  const changed = changeStep({changes:[{path:'note',kind:{type:'update'},diff:'@@ -1 +1 @@\n---old\n+++new'}]},false)
  expect(changed.files[0]).toMatchObject({added:0,removed:0})
})
it('keeps a Windows child absolute when requested relative to its project', () => {
  expect(relativeTo('C:\\project','C:\\project\\report.md')).toBe('C:\\project\\report.md')
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.ts", mode="w") as target:
    target.write(cases)
    target.flush()
    subprocess.run(["node_modules/.bin/vitest","run",target.name],cwd=app,check=True)
