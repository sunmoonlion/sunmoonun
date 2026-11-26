"""捕获正式试跑组件的请求，并模拟刷新不存在的试跑。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path('knowlab-app/knowlab-web-frontend/app').resolve()
tests = app/'tests/component'
fixture = (tests/'formal-method-execution.test.tsx').read_text().split("it('starts a real suite",1)[0]
case = """
it('changes both the typed integer input and expected integer during submission', async () => {
  const numeric = structuredClone(draft)
  if(numeric.definition.procedure.kind !== 'direct') throw Error()
  const slot = {...numeric.definition.procedure.outputs.ok,schema:{type:'integer'}}
  numeric.definition.procedure.inputs = {n:slot}
  numeric.definition.procedure.outputs = {ok:slot}
  page(false,['host'],numeric)
  await fill()
  fireEvent.change(screen.getByLabelText(t.values),{target:{value:'{"n":9007199254740993}'}})
  fireEvent.change(screen.getByLabelText(t.assertions,{exact:false}),
    {target:{value:'[{"kind":"equals","pointer":"/ok","value":9007199254740993}]'}})
  fireEvent.click(screen.getByRole('button',{name:t.start}))
  await waitFor(() => expect(posts).toHaveLength(1))
  const sent = posts[0].body.execution.suite.cases[0]
  expect(String(sent.input.values.n)).toBe('9007199254740992')
  expect(String(sent.expected.assertions[0].value)).toBe('9007199254740992')
})
it('keeps the active lock on a missing restored run and cannot open an editable suite', async () => {
  fetcher.mockImplementation(async () => Response.json({}, {status:404}))
  const {onActiveChange} = page(true)
  await screen.findByRole('alert')
  expect(onActiveChange).toHaveBeenLastCalledWith(true)
  expect(screen.queryByRole('button',{name:t.retry})).toBeNull()
  expect(screen.queryByRole('button',{name:t.nextVersion})).toBeNull()
  expect(screen.queryByLabelText(t.caseId)).toBeNull()
})
"""
with NamedTemporaryFile(dir=tests, suffix='.test.tsx', mode='w') as f:
    f.write(fixture+case)
    f.flush()
    subprocess.run(['node_modules/.bin/vitest','run',f.name],cwd=app,check=True)
