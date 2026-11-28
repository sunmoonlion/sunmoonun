"""验证本次能力选择在修订回执到达时是否保留后来输入的用途。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
tests = app / "tests/component"
setup = (tests / "capabilities.test.tsx").read_text().split("it('displays and approves",1)[0]
case = """
it('discards purpose edits made while the previous revision is being saved', async () => {
  const gate = Promise.withResolvers<void>()
  const normal = globalThis.fetch
  let pending = false
  vi.stubGlobal('fetch', async (input: string, init: RequestInit = {}) => {
    if (input.endsWith('/capabilities') && init.method === 'PUT') {
      pending = true
      await gate.promise
    }
    return normal(input,init)
  })
  page(<CapabilityPanel sessionId={selection.session_id} />)
  fireEvent.click(screen.getByRole('button', {name: zh.capabilities.thisRun}))
  const box = await screen.findByLabelText(zh.capabilities.purpose)
  fireEvent.change(box, {target:{value:'第一版用途'}})
  fireEvent.click(screen.getByRole('button',{name: zh.capabilities.saveSelection}))
  await waitFor(() => expect(pending).toBe(true))
  expect(box).toBeEnabled()
  fireEvent.change(box, {target:{value:'随后改定的用途'}})
  expect(box).toHaveValue('随后改定的用途')
  gate.resolve()
  await waitFor(() => expect(screen.getByLabelText(zh.capabilities.purpose)).toHaveValue('第一版用途'))
  expect(writes.map(w => w.body.purpose)).toEqual(['第一版用途'])
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as target:
    target.write(setup + case)
    target.flush()
    subprocess.run(["node_modules/.bin/vitest","run",target.name],cwd=app,check=True)
