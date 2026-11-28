"""在工作台真实组件中核对确认可见范围、分期编辑与拒绝后的草稿。"""
from pathlib import Path
from subprocess import run
from tempfile import NamedTemporaryFile

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
suite = app / "tests/component/task-data-panel.test.tsx"
examples = """
it('两张待确认采单只展示第一张，确认没有绑定请求或清单修订', async () => {
  const data = structuredClone(proposed)
  const extra = structuredClone(data.requests[0])
  extra.id = 'r2'
  extra.needs[0].name = '第二批独立核验资料'
  data.requests.push(extra)
  wrap(<TaskDataPanel task={TASK} data={data} />)
  expect(screen.queryByText('第二批独立核验资料')).toBeNull()
  fireEvent.click(screen.getByRole('button',{name:'确认使用这些数据'}))
  await waitFor(() => expect(calls[0]?.body).toEqual({}))
})
it('只改主体，原固定季度随确认变成全年', async () => {
  const data = structuredClone(proposed)
  const req = data.requests[0]
  req.needs[0].period = {kind:'fixed',start:'2025-04-01',end:'2025-06-30'}
  Object.assign(req.items[0].key,{period_start:'2025-04-01', period_end:'2025-06-30'})
  wrap(<TaskDataPanel task={TASK} data={data} />)
  fireEvent.click(screen.getAllByRole('button',{name:'改'})[0])
  fireEvent.change(screen.getByRole('textbox',{name:'主体'}),{target:{value:'000858.SZ'}})
  fireEvent.click(screen.getByRole('button',{name:'好'}))
  fireEvent.click(screen.getByRole('button',{name:'确认使用这些数据'}))
  await waitFor(() => expect(calls[0]?.body.needs[0].period).toEqual(
    {kind:'fixed',start:'2025-01-01',end:'2025-12-31'}))
})
it('去掉一个期间并添加新资料时，同需求的另一期一并消失', async () => {
  const data = structuredClone(proposed)
  const req = data.requests[0]
  req.items[1].need_key = req.items[0].need_key
  req.needs = req.needs.slice(0,1)
  wrap(<TaskDataPanel task={TASK} data={data} />)
  fireEvent.click(screen.getAllByRole('button',{name:'不要这一样'})[1])
  fireEvent.click(screen.getByRole('button',{name:messages.expert.data.add}))
  fireEvent.click(screen.getByRole('button',{name:messages.expert.data.addDone}))
  fireEvent.click(screen.getByRole('button',{name:'确认使用这些数据'}))
  await waitFor(() => expect(calls[0]?.body.needs).toHaveLength(1))
  expect(calls[0].body.needs[0].key).toBeUndefined()
})
"""
with NamedTemporaryFile(mode="w", dir=suite.parent, suffix=".test.tsx") as f:
    f.write(suite.read_text() + examples)
    f.flush()
    run(["node_modules/.bin/vitest","run",f.name,"tests/unit/task-data.test.ts",
         "tests/component/task-data-refresh.test.tsx"],cwd=app,check=True)
