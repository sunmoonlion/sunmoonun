"""真实上传组件，本地合成文件与网络替身。复核权限声明、组织标识、报告年度和补交新版本。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowbase-app/knowbase-web-frontend/app").resolve()
tests = app / "tests/component"
src = (tests / "library.test.tsx").read_text()
fixture = src[:src.index("describe('LibraryWorkspace'")] + src[src.index("  const recognition ="):src.index("  it('recognises first")]
cases = """
it('sends the replacement file under the first file’s sale attestation', async () => {
  const requests: Array<{url:string; body:unknown}> = []
  vi.stubGlobal('fetch', routes((url, init) => {
    if (url.includes('/recognitions')) return json(recognition)
    if (url.includes('/library/materials?')) {
      requests.push({ url, body:init?.body })
      return json(ENTRIES[0])
    }
  }))
  const {container} = page(<UploadPanel csrfToken={'c'.repeat(32)} />)
  const input = container.querySelector('input[type=file]')!
  fireEvent.change(input,{target:{files:[new File(['a'],'a.pdf')]}})
  await screen.findByDisplayValue('中信证券')
  fireEvent.click(screen.getByLabelText('可以出售'))
  fireEvent.click(screen.getByLabelText('我有权让这份资料「可以出售」。'))
  fireEvent.click(screen.getByLabelText(/描述无误，我确认/))
  const b = new File(['b'],'b.pdf')
  fireEvent.change(input,{target:{files:[b]}})
  await waitFor(() => expect(input).toBeEnabled())
  fireEvent.click(screen.getByRole('button',{name:'上传'}))
  await waitFor(() => expect(requests).toHaveLength(1))
  expect(requests[0].body).toBe(b)
  expect(Object.fromEntries(new URL(requests[0].url,'http://local').searchParams))
    .toMatchObject({name:'b.pdf',license:'sale',attest:'true',confirm:'true'})
})

it('loses a typed year digit and loses the source context on direct version upload', async () => {
  search = new URLSearchParams('from=knowbench&ref=t:9&doc_type=annual_report')
  const urls: string[] = []
  const found = { ...recognition, description: {...recognition.description, disclosed_on:null} }
  vi.stubGlobal('fetch', routes((url, init) => {
    if (url.includes('/cross-app/origin'))
      return json({app:'knowbench',ref:'t:9',return_url:'https://knowbench.example/back'})
    if (url.includes('/recognitions')) return json(found)
    if (url.includes('/versions?') && init?.method === 'POST') {
      urls.push(url); return json(ENTRIES[0])
    }
  }))
  const {container} = page(<UploadPanel csrfToken={'c'.repeat(32)} />)
  await screen.findByText('knowbench 缺这一样资料，采不来，请在这里上传')
  fireEvent.change(container.querySelector('input[type=file]')!,{
    target:{files:[new File(['v2'],'我的年报.pdf')]},
  })
  const year = await screen.findByPlaceholderText('2025')
  await waitFor(() => expect(year).toBeEnabled())
  fireEvent.change(year,{target:{value:'2'}})
  expect(year).toHaveValue('')
  fireEvent.change(year,{target:{value:'2025'}})
  fireEvent.click(await screen.findByRole('radio',{name:/我的年报.pdf/}))
  fireEvent.click(screen.getByRole('button',{name:'上传'}))
  await waitFor(() => expect(leave).toHaveBeenCalled())
  const dest = new URL(urls[0],'http://local')
  expect(dest.pathname).toContain('/materials/m-up/versions')
  expect(dest.searchParams.has('from')).toBe(false)
  expect(dest.searchParams.has('ref')).toBe(false)
})

it('uppercases an organization identifier in both editor and upload requests', () => {
  const draft = {...EMPTY_DRAFT,subject:'org:kb-stats-bureau'}
  expect(descriptionBody(draft,undefined,true).subject).toBe('ORG:KB-STATS-BUREAU')
  expect(uploadQuery(draft,undefined,{
    name:'sample.pdf',confirm:true,license:'self',attest:false,process:false
  }).get('subject')).toBe('ORG:KB-STATS-BUREAU')
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as probe:
    probe.write("import {EMPTY_DRAFT,descriptionBody,uploadQuery} from '@/features/library/model/library'\n" + fixture + cases)
    probe.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", probe.name], cwd=app, check=True)
