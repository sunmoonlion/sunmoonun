"""验证筛选后全选状态与实际提交的资料编号。使用合成资料与本地 fetch 替身。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowbase-app/knowbase-web-frontend/app").resolve()
tests = app / "tests/component"
fixture = (tests / "library.test.tsx").read_text().split("describe('LibraryWorkspace'", 1)[0]
case = """
it('select-all appears checked for B while the bulk command still grants display of A', async () => {
  const materials = [entry('a', 'uploaded', 'A.pdf'), entry('b', 'uploaded', 'B.pdf')]
  materials[1].material.description.subject = '000858.SZ'
  const writes: unknown[] = []
  vi.stubGlobal('fetch', routes((url, init) => {
    if (url.endsWith('/library/materials')) return json(materials)
    if (url.endsWith('/uses/bulk')) {
      writes.push(JSON.parse(String(init?.body)))
      return json({})
    }
  }))
  page(<LibraryWorkspace csrfToken={'c'.repeat(32)} />)
  fireEvent.click(await screen.findByRole('checkbox', {name:'A.pdf'}))
  fireEvent.change(screen.getByPlaceholderText('主体'), {target:{value:'000858.SZ'}})
  expect(screen.queryByRole('checkbox', {name:'A.pdf'})).toBeNull()
  expect(screen.getByRole('checkbox', {name:'B.pdf'})).not.toBeChecked()
  expect(screen.getByRole('checkbox', {name:'全选'})).toBeChecked()
  fireEvent.click(screen.getByRole('button', {name:'展示给 knowbench'}))
  await waitFor(() => expect(writes).toEqual([{material_ids:['a'],use:'app:knowbench',on:true}]))
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as probe:
    probe.write(fixture + case)
    probe.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", probe.name], cwd=app, check=True)
