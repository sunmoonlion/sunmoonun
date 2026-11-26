"""核对文件导入失败后的草稿及改换技能来源时的依赖。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
tests = app / "tests/component"
setup = (tests / "capabilities.test.tsx").read_text().split("it('displays and approves",1)[0]
case = """
it('clears the typed skill and blocks manual recovery after an unreadable upload', async () => {
  page(<CapabilitySettings kind="skill" />)
  fireEvent.click(await screen.findByRole('button',{name:zh.capabilities.installSkill}))
  fireEvent.click(screen.getByRole('button',{name:zh.capabilities.fromFile}))
  const content = screen.getByRole('textbox',{name:zh.capabilities.instructions})
  fireEvent.change(content, {target:{value:'已审核指令'}})
  fireEvent.change(screen.getByLabelText(zh.capabilities.importFile), {target:{
    files:[new File(['invalid'], 'unsupported.txt')]
  }})
  await screen.findByRole('alert')
  expect(content).toHaveValue('')
  fireEvent.change(content, {target:{value:'重新手填的指令'}})
  fireEvent.change(screen.getByLabelText(zh.capabilities.skillName),{target:{value:'valid-skill'}})
  fireEvent.change(screen.getByLabelText(zh.capabilities.description),{target:{value:'purpose'}})
  expect(screen.getByRole('button',{name:zh.capabilities.import})).toBeDisabled()
})
it('carries dependency selection from one repository to the next sole candidate', async () => {
  page(<CapabilitySettings kind="skill" />)
  fireEvent.click(await screen.findByRole('button',{name:zh.capabilities.installSkill}))
  const normal = globalThis.fetch
  vi.stubGlobal('fetch', async (path:string, init:RequestInit={}) => {
    const response = await normal(path,init)
    if (!path.endsWith('/preview') || !String(init.body).includes('/second')) return response
    const data = await response.json()
    return Response.json({...data, repository:'https://github.com/owner/second',commit:'f'.repeat(40),
      candidates:[{...data.candidates[0],name:'other-skill',path:'second-skill',digest:'e'.repeat(64)}]})
  })
  const url = screen.getByLabelText(zh.capabilities.repositoryUrl)
  fireEvent.change(url,{target:{value:'https://github.com/owner/first'}})
  fireEvent.click(screen.getByRole('button',{name:zh.capabilities.previewSource}))
  fireEvent.click(await screen.findByRole('checkbox',{name:/Office mail/}))
  fireEvent.change(url,{target:{value:'https://github.com/owner/second'}})
  fireEvent.click(screen.getByRole('button',{name:zh.capabilities.previewSource}))
  expect(await screen.findByRole('radio',{name:/other-skill/})).toBeChecked()
  expect(await screen.findByRole('checkbox',{name:/Office mail/})).toBeChecked()
  fireEvent.click(screen.getByRole('button',{name:zh.capabilities.installEnable}))
  await waitFor(() => expect(writes.at(-1)?.body.url).toBe('https://github.com/owner/second'))
  await waitFor(() => expect(writes.at(-1)?.body.tool_requirements).toHaveLength(1))
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as target:
    target.write(setup + case)
    target.flush()
    subprocess.run(["node_modules/.bin/vitest","run",target.name],cwd=app,check=True)
