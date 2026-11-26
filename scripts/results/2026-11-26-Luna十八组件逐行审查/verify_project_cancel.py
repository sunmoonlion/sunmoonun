"""复用项目组件测试的本机代理夹具，延迟建目录回执并点取消。"""
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
suite = app / "tests/component/new-project-dialog.test.tsx"
probe = """
it('点击取消后迟到的目录回执仍触发登记和跳转', async () => {
  const original = globalThis.fetch
  let release!: () => void
  const gate = new Promise<void>(resolve => { release = resolve })
  const entered = vi.fn()
  vi.stubGlobal('fetch', async (...args: Parameters<typeof fetch>) => {
    if (String(args[0]).endsWith('/local/v1/projects/folder')) {
      entered()
      await gate
    }
    return original(...args)
  })
  const navigate = dialog()
  const submit = await screen.findByRole('button', { name: t.submit })
  await waitFor(() => expect(submit).toBeEnabled())
  fireEvent.click(submit)
  await waitFor(() => expect(entered).toHaveBeenCalledOnce())
  fireEvent.click(screen.getByRole('button', { name: t.cancel }))
  release()
  await waitFor(() => expect(navigate).toHaveBeenCalledWith(PROJECT))
  expect(posts().at(-1)?.url).toBe('http://testserver/api/workbench/projects')
})
"""
with NamedTemporaryFile(mode="w", dir=suite.parent, suffix=".test.tsx") as tmp:
    tmp.write(suite.read_text() + probe)
    tmp.flush()
    run(["node_modules/.bin/vitest", "run", tmp.name], cwd=app, check=True)
