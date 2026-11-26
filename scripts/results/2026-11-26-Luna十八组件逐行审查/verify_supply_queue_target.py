"""用 KnowFeed 既有队列样例复现筛选变更后的操作对象；在仓库根目录运行。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowfeed-app/knowfeed-admin-frontend/app").resolve()
tests = app / "tests/component"
original = (tests / "supply-panels.test.tsx").read_text()
case = original[original.index("describe('队列监控'"):original.index("describe('登记表'")]
marker = "      'GET /api/admin/v1/supply/jobs/j-1':"
assert case.count(marker) == 1
case = case.replace(marker, "      'GET /api/admin/v1/supply/jobs?status=failed': () => Response.json({ items: [] }),\n" + marker)
marker = "    fireEvent.click(await screen.findByRole('button', { name: '马上再排' }))"
assert case.count(marker) == 1
case = case.replace(marker, """    await screen.findByRole('button', { name: '马上再排' })
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'failed' } })
    await screen.findByText('没有这种状态的作业。')
    expect(screen.queryByRole('button', { name: /600519.SH/ })).toBeNull()
""" + marker)
marker = "    expect(await screen.findByText('已再排。')).toBeInTheDocument()"
assert case.count(marker) == 1
case = case.replace(marker, marker + """
    expect(calls.some(c => c.method === 'POST' && c.url.endsWith('/jobs/j-1/requeue'))).toBe(true)""")
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as probe:
    probe.write(original[:original.index("describe('来源目录'")] + case)
    probe.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", probe.name], cwd=app, check=True)
