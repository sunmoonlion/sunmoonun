"""复用 KnowBench 真实结果栏，只给它进入页面前已有的一条文件改动。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
tests = app / "tests/component"
setup = (tests / "file-tree.test.tsx").read_text().split("describe('右边栏", 1)[0]
case = """
it('opens the sidebar from unchanged historical changes', async () => {
  render(<NextIntlClientProvider locale="zh-CN" messages={messages}>
    <WorkSidePanel files={[{path:'report.md',how:'add',added:1,removed:0,diffs:[]}]}
      directory={null} live={true}/>
  </NextIntlClientProvider>)
  const panel = screen.getByRole('complementary')
  expect(panel.dataset.state).toBe('collapsed')
  expect(await screen.findByRole('button', {name:/^改动/,pressed:true}, {timeout:3500})).toBeVisible()
  expect(panel.dataset.state).toBe('open')
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as target:
    target.write(setup + case)
    target.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", target.name], cwd=app, check=True)
