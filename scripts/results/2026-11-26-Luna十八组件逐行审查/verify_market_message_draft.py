"""在 KnowMart 组件中延后第一条留言的回执，观察第二条尚未发送的草稿。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowmart-app/knowmart-web-frontend/app").resolve()
tests = app / "tests/component"
fixture = (tests / "market.test.tsx").read_text().split("describe('供需市场'", 1)[0]
case = """
it('clears unsent edits when the earlier post finishes', async () => {
  let finish!: () => void
  vi.mocked(client.postMessage).mockImplementation(() => new Promise(resolve => {
    finish = () => resolve({message:{message_id:'m',body:'第一条',role:'buyer',mine:true,created_at:null}})
  }))
  page(<Thread csrfToken={CSRF} kind="demand" id="d" title="公开留言" />)
  const input = screen.getByRole('textbox')
  fireEvent.change(input,{target:{value:'第一条'}})
  fireEvent.click(screen.getByRole('button',{name:'发'}))
  await waitFor(() => expect(client.postMessage).toHaveBeenCalledWith(CSRF,'demand','d','第一条'))
  fireEvent.change(input,{target:{value:'第二条尚未发出'}})
  expect(input).toHaveValue('第二条尚未发出')
  finish()
  await waitFor(() => expect(input).toHaveValue(''))
  expect(client.postMessage).toHaveBeenCalledTimes(1)
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as probe:
    probe.write("import { Thread } from '@/components/market/demands'\n" + fixture + case)
    probe.flush()
    subprocess.run(["node_modules/.bin/vitest","run",probe.name],cwd=app,check=True)
