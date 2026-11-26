"""在真实聊天页延迟发送回执，并模拟选项目时清单读取失败。"""
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
tests = app / "tests/component"
setup = (tests / "chat-screen.test.tsx").read_text().split("describe('聊天页'", 1)[0]
cases = """
it('loses the unsent second draft when the first send is acknowledged', async () => {
  const original = vi.mocked(fetch).getMockImplementation()!
  const gate = Promise.withResolvers<void>()
  vi.stubGlobal('fetch', async (url: string, options: RequestInit = {}) => {
    if (url.endsWith('/turns')) await gate.promise
    return original(url, options)
  })
  page()
  await screen.findByText('片仔癀 2025 年的毛利率是多少？')
  const box = screen.getByRole('textbox', { name: '对它说' })
  fireEvent.change(box, {target: {value: 'first question'}})
  fireEvent.click(screen.getByRole('button', {name: '发送'}))
  fireEvent.change(box, {target: {value: 'second question'}})
  expect(box).toHaveValue('second question')
  await act(async () => gate.resolve())
  await waitFor(() => expect(box).toHaveValue(''))
  expect(calls.filter(c => c.path.endsWith('/turns')).map(c => c.body))
    .toEqual([{text: 'first question'}])
})

it('tells the user there are no projects after the projects service fails', async () => {
  const original = vi.mocked(fetch).getMockImplementation()!
  let failed = false
  vi.stubGlobal('fetch', async (url: string, options: RequestInit = {}) => {
    if (url.split('?')[0].endsWith('/projects')) {
      failed = true
      return answer({code:'unavailable'}, 503)
    }
    return original(url, options)
  })
  page()
  fireEvent.click(await screen.findByRole('button', {name:'放进项目'}))
  expect(await screen.findByText(messages.projectPicker.none)).toBeVisible()
  expect(failed).toBe(true)
})

it('ignores the project segment when resolving the conversation page', async () => {
  const { default: Page } = await import('@/app/[locale]/(dashboard)/workbench/projects/[project]/c/[conversation]/page')
  const open = (project: string) => Page({params: Promise.resolve({project, conversation: IN_PROJECT})})
  const [a,b] = await Promise.all([open('project-a'), open('project-b')])
  expect(a.type).toBe(b.type)
  expect(a.props.conversation).toBe(IN_PROJECT)
  expect(b.props.conversation).toBe(IN_PROJECT)
  expect(a.props.children.props).toEqual({conversation: IN_PROJECT})
  expect(b.props.children.props).toEqual(a.props.children.props)
})

it('expands a sibling POSIX root differing only in case', async () => {
  const { pathsToExpand, isUnder } = await import('@/lib/workbench/file-tree')
  expect(isUnder('/work/Q4/report', '/work/q4')).toBe(true)
  expect(pathsToExpand('/work/q4', '/work/Q4/report')).toEqual(['/work/q4/report'])
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.tsx", mode="w") as target:
    target.write(setup + cases)
    target.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", target.name], cwd=app, check=True)
