"""从 KnowFeed 用户工作台提交合成表单，核对显示的数据归属与重试回执。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowfeed-app/knowfeed-web-frontend/app").resolve()
tests = app / "tests/component"
fixture = (tests / "supply-panels.test.tsx").read_text().split("describe('提需求'", 1)[0]
cases = """
it('shows a new item after retry even when the response contains no demand', async () => {
  serve({
    'GET /api/web/v1/supply/demands': () => Response.json([demand]),
    'POST /api/web/v1/supply/items/i-2/retry': () =>
      Response.json({demand:null, replayed:false, already_ready:['c1']}),
  })
  show(<MyDemandsPanel csrfToken={CSRF} />)
  fireEvent.click(await screen.findByRole('button', {name:'再试一次'}))
  expect(await screen.findByText('已再试一次，新的一项在列表里。')).toBeInTheDocument()
})

it('retains the old material availability after changing the subject', async () => {
  serve({
    'GET /api/web/v1/supply/options': () => Response.json(options),
    'POST /api/web/v1/supply/prematch': () =>
      Response.json({contract:'test', items:[{ref:'c1',status:'available'}]}),
  })
  show(<NewDemandPanel csrfToken={CSRF} />)
  const subject = screen.getByLabelText('主体')
  fireEvent.change(subject, {target:{value:'600519.SH'}})
  fireEvent.click(screen.getByRole('button', {name:'先看能不能取'}))
  await screen.findByRole('list', {name:'预切合结果'})
  fireEvent.change(subject, {target:{value:'000858.SZ'}})
  expect(screen.getByRole('list', {name:'预切合结果'})).toHaveTextContent('能取')
  const checks = calls.filter(c => c.url.endsWith('/prematch'))
  expect(checks).toHaveLength(1)
  expect(checks[0].body).toMatchObject({items:[{key:{subject:'600519.SH'}}]})
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as probe:
    probe.write(fixture + cases)
    probe.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", probe.name], cwd=app, check=True)
