"""用本地组件和替身 API 核验模型设置成功后的关联刷新与草稿。"""
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
suite = app / "tests/component/settings-sections.test.tsx"
probe = """
it('撤销凭据后同页复核候选仍显示刚撤销的那条', async () => {
  const original = globalThis.fetch
  const id = '6f1c2b1e-3c5d-4a7e-9b8f-0d1e2f3a4b5d'
  let active = true
  let reads = 0
  vi.stubGlobal('fetch', async (path: string, init: RequestInit = {}) => {
    if (path.endsWith('/revoke')) {
      active = false
      return Response.json({status:'revoked'})
    }
    if (path.endsWith('/credentials'))
      return Response.json({credentials:[{id,provider:'kimi',hint:'9999',status:active?'active':'revoked'}]})
    if (path.endsWith('/prefs/reviewer')) {
      reads++
      return Response.json({preference:null,gap:null,producer:null,options:active?[{
        pin:{provider:'kimi',model:'reviewmodel',credential_id:id}, family:null,
        destination:'fixture',currency:'CNY',price_as_of:'2026-01-01',price_key:'x',quote:null
      }]:[]})
    }
    return original(path,init)
  })
  page(<SettingsScreen section="cloud" />)
  await screen.findByRole('option',{name:/reviewmodel/})
  fireEvent.click(screen.getByRole('button',{name:zh.workbench.settings.revoke}))
  await waitFor(() => expect(document.querySelector('[data-credential-status="revoked"]')).toBeTruthy())
  expect(screen.getByRole('option',{name:/reviewmodel/})).toBeEnabled()
  expect(reads).toBe(1)
})
it('第一条凭据登记的迟到回执抹去后续输入',async () => {
  const original = globalThis.fetch
  let release!: () => void
  const gate = new Promise<void>(r => { release = r })
  const sent = vi.fn()
  vi.stubGlobal('fetch', async (path:string,init:RequestInit={}) => {
    if (path.endsWith('/credentials') && init.method === 'POST') {
      sent()
      await gate
    }
    return original(path,init)
  })
  page(<SettingsScreen section="cloud" />)
  const input = await screen.findByLabelText(/API key/)
  fireEvent.change(input,{target:{value:'first-fixture'}})
  fireEvent.click(screen.getByRole('button',{name:zh.workbench.settings.submitKey}))
  await waitFor(() => expect(sent).toHaveBeenCalledOnce())
  fireEvent.change(input,{target:{value:'second-fixture'}})
  release()
  await waitFor(() => expect(input).toHaveValue(''))
})
"""
with NamedTemporaryFile(mode="w",dir=suite.parent,suffix=".test.tsx") as f:
    f.write(suite.read_text()+probe)
    f.flush()
    run(["node_modules/.bin/vitest","run",f.name],cwd=app,check=True)
