"""核对测试历史行显示的是哪一版题目。使用仓库的 TestsColumn 和真实版本结构。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path('knowlab-app/knowlab-web-frontend/app').resolve()
tests = app / 'tests/component'
fixture = (tests / 'lab-columns.test.tsx').read_text().split("describe('孵化栏'", 1)[0]
case = """
it('shows the revised question beside the old passing result', async () => {
  const life = detail()
  life.drafts[0].request_version = 1
  life.drafts[0].status = 'passed'
  life.drafts[0].label = '1.1'
  life.tests[0].label = '1.1'
  life.versions.forEach(v => {
    v.cases = [{case_id:'c1', input:{question:v.version === 1 ? '旧题原文' : '新版问题'}}]
  })
  vi.mocked(fetchApplications).mockResolvedValue([application()])
  vi.mocked(fetchDetail).mockResolvedValue(life)
  renderWith(<TestsColumn csrfToken={CSRF} picked={REQUEST} />)
  const history = await screen.findByTestId('test-history')
  expect(history).toHaveTextContent('新版问题')
  expect(history).not.toHaveTextContent('旧题原文')
})
"""
with NamedTemporaryFile(dir=tests, suffix='.test.tsx', mode='w') as f:
    f.write(fixture + case)
    f.flush()
    subprocess.run(['node_modules/.bin/vitest', 'run', f.name], cwd=app, check=True)
