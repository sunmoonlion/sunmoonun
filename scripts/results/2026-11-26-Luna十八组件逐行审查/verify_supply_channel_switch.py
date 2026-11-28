"""用既有渠道样例和管理页面核验切换对象后提交的审核原因。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowfeed-app/knowfeed-admin-frontend/app").resolve()
tests = app / "tests/component"
fixture = (tests / "supply-panels.test.tsx").read_text().split("describe('来源目录'", 1)[0]
case = """
it('carries the first channel review reason into a decision on another channel', async () => {
  const detail = (channel: typeof cninfo) => Response.json({ channel, trials: [], events: [] })
  serve({
    'GET /api/admin/v1/supply/channels': () => Response.json(list),
    'GET /api/admin/v1/supply/channels/sse': () => detail(sse),
    'GET /api/admin/v1/supply/channels/cninfo': () => detail(cninfo),
    'POST /api/admin/v1/supply/channels/sse/review': () => Response.json(sse),
  })
  show(<ChannelsPanel csrfToken={'a'.repeat(32)} />)
  const select = async (name: string) => {
    fireEvent.click(await screen.findByRole('button', { name }))
    return within(await screen.findByRole('region', { name }))
  }
  await select(sse.name)
  const first = await select(cninfo.name)
  fireEvent.change(first.getByLabelText('凭什么'), {target:{value:'仅适用于巨潮的原因'}})
  const second = await select(sse.name)
  expect(second.getByLabelText('凭什么')).toHaveValue('仅适用于巨潮的原因')
  fireEvent.click(second.getByRole('button', {name:'审不过'}))
  await vi.waitFor(() => expect(calls.find(c => c.method === 'POST')).toMatchObject({
    url: '/api/admin/v1/supply/channels/sse/review',
    body: {decision:'reject', reason:'仅适用于巨潮的原因'},
  }))
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as probe:
    probe.write(fixture + case)
    probe.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", probe.name], cwd=app, check=True)
