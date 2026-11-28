"""在真实工作稿组件中控制保存失败、建议回包和卸载的先后顺序。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path('knowlab-app/knowlab-web-frontend/app').resolve()
tests = app / 'tests/component'
setup = (tests / 'workdraft-ai.test.tsx').read_text().split("describe('发起一轮'", 1)[0]
cases = """
it('submits the budgeted round after the edited draft failed to save', async () => {
  vi.mocked(saveWorkdraftCells).mockRejectedValue(refused('unavailable', 503))
  vi.mocked(startRound).mockResolvedValue(round({status:'queued'}))
  renderWith(<WorkdraftView requestId={REQUEST} csrfToken={CSRF} saveDelay={60000} />)
  fireEvent.change(await screen.findByLabelText(w.expert.name),{target:{value:'修改后的范围'}})
  fireEvent.click(screen.getByRole('button',{name:w.toolbar.aiDraft}))
  const dialog = within(await screen.findByRole('dialog',{name:a.draftTitle}))
  await waitFor(() => expect(dialog.getByLabelText(a.computer)).toHaveValue(OTHER))
  fireEvent.click(dialog.getByRole('button',{name:a.start}))
  await waitFor(() => expect(startRound).toHaveBeenCalledOnce())
  expect(saveWorkdraftCells).toHaveBeenCalledOnce()
  expect(startRound).toHaveBeenCalledWith(REQUEST,expect.objectContaining({budget_limit:'20'}),CSRF)
})

it('replaces text typed while a suggestion decision is pending', async () => {
  withRound(round({suggestions:[suggestion()]}))
  let finish!: (v: Awaited<ReturnType<typeof decideSuggestion>>) => void
  vi.mocked(decideSuggestion).mockImplementation(() => new Promise(resolve => {finish=resolve}))
  renderWith(<WorkdraftView requestId={REQUEST} csrfToken={CSRF} saveDelay={60000} />)
  const s = within(await screen.findByTestId('suggestion-s1'))
  fireEvent.click(s.getByRole('button',{name:a.accept}))
  await waitFor(() => expect(decideSuggestion).toHaveBeenCalledOnce())
  const name = screen.getByLabelText(w.expert.name)
  fireEvent.change(name,{target:{value:'刚输入的名称'}})
  expect(name).toHaveValue('刚输入的名称')
  finish({workdraft:workdraft({revision:3}),round:round()})
  await waitFor(() => expect(name).toHaveValue(''))
  expect(saveWorkdraftCells).not.toHaveBeenCalled()
})
"""
with NamedTemporaryFile(dir=tests, suffix='.test.tsx', mode='w') as f:
    f.write(setup + cases)
    f.flush()
    subprocess.run(['node_modules/.bin/vitest','run',f.name],cwd=app,check=True)

save_fixture = (tests / 'workdraft.test.tsx').read_text().split("describe('工作稿：",1)[0]
save_cases = """
it('submits publish with the saved outputs while an invalid local output remains visible', async () => {
  server = workdraft({ body: { ...emptyBody(), planning:dynamicPlanning, steps:[step('s1')] } })
  vi.mocked(publishWorkdraft).mockRejectedValue(refused('workdraft_invalid'))
  page()
  fireEvent.click(await screen.findByRole('button',{name:w.step.addOutput}))
  expect(screen.getByText(w.step.notSaved)).toBeVisible()
  fireEvent.click(screen.getByRole('button',{name:w.toolbar.publish}))
  await waitFor(() => expect(publishWorkdraft).toHaveBeenCalledWith(REQUEST,CSRF))
  expect(server.body.steps[0].outputs).toHaveLength(0)
})

it('unmount sends the last edit on the same revision as an outstanding save', async () => {
  let finish!: () => void
  vi.mocked(saveWorkdraftCells).mockImplementationOnce(async (_, {cells}) => {
    await new Promise<void>(r => {finish=r})
    server = stored(server,cells)
    return server
  }).mockImplementationOnce(async () => {throw conflict()})
  const view = page()
  const name = await screen.findByLabelText(w.expert.name)
  fireEvent.change(name,{target:{value:'第一稿'}})
  await waitFor(() => expect(saveWorkdraftCells).toHaveBeenCalledTimes(1))
  fireEvent.change(name,{target:{value:'最后一稿'}})
  view.unmount()
  expect(saveWorkdraftCells.mock.calls.map(call => call[1].revision)).toEqual([0,0])
  finish()
  await waitFor(() => expect(server.body.name).toBe('第一稿'))
})
"""
with NamedTemporaryFile(dir=tests, suffix='.test.tsx', mode='w') as f:
    f.write(save_fixture + save_cases)
    f.flush()
    subprocess.run(['node_modules/.bin/vitest','run',f.name],cwd=app,check=True)
