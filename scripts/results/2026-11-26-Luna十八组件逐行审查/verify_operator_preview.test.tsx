import { act, fireEvent, screen } from '@testing-library/react'
import { useQueryClient, type QueryClient } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { OperatorWorkdraft } from '@/components/knowbots/operator-workdraft'
import { KEY } from '@/components/knowbots/shared'
import { fetchOperatorWorkdraft, fetchOperatorRounds, previewOperator } from '@/lib/knowbots/client'
import { useState } from 'react'
import { Checks } from '@/components/knowbots/workdraft-checks'
import { newStep } from '@/lib/knowbots/workdraft'
import { numberParser } from '@/components/knowbots/workdraft-cells'
import type { Workdraft } from '@/contracts/workdraft'
import messages from '@/messages/zh-CN.json'
import { renderWith, REQUEST, CSRF } from './knowbot-fixtures'

vi.mock('@/lib/knowbots/client', () => ({
  fetchOperatorWorkdraft: vi.fn(), fetchOperatorRounds: vi.fn(), previewOperator: vi.fn(),
  propose: vi.fn(), publishOperator: vi.fn(), startOperatorRound: vi.fn(), withdrawProposal: vi.fn(),
}))
vi.mock('@/i18n/navigation', async () => (await import('./knowbot-fixtures')).linkMock())

const saved: Workdraft = {
  contract_version: 1, revision: 2, request_id: REQUEST, title: '核验',
  body: { name: '核验', tagline: '', scope: { does: '', does_not: '', elsewhere: '' }, data_picks: [], steps: [] },
  sources: {}, origins: {}, updated_at: null, proposals: [],
}
const labels = messages.operatorWorkdraft
beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(fetchOperatorWorkdraft).mockResolvedValue(saved)
  vi.mocked(fetchOperatorRounds).mockResolvedValue([])
})
it('预检尚未返回时，页面先报告就绪并启用出一版', async () => {
  let finish!: (v: Awaited<ReturnType<typeof previewOperator>>) => void
  vi.mocked(previewOperator).mockReturnValue(new Promise(resolve => { finish = resolve }))
  renderWith(<OperatorWorkdraft requestId={REQUEST} csrfToken={CSRF} />)
  expect(await screen.findByText(labels.publish.ready)).toBeVisible()
  expect(screen.getByRole('button', {name: labels.publish.submit})).toBeEnabled()
  await act(async () => finish({ contract_version: 1, version: '1', manifest: {}, problems: [{path: 'name', message: '名称依据不足'}] }))
  expect(await screen.findByTestId('problem-name')).toBeVisible()
  expect(screen.getByRole('button', {name: labels.publish.submit})).toBeDisabled()
})
it('刷新时作者改了另一个字段，运营未提交的名称及理由消失', async () => {
  vi.mocked(previewOperator).mockResolvedValue({contract_version: 1, version: '1', manifest: {}, problems: []})
  let client!: QueryClient
  function Page() {
    client = useQueryClient()
    return <OperatorWorkdraft requestId={REQUEST} csrfToken={CSRF} />
  }
  renderWith(<Page />)
  const name = messages.workdraft.expert.name
  fireEvent.change(await screen.findByLabelText(name), {target: {value: '运营想提议的名称'}})
  fireEvent.change(screen.getByLabelText(labels.send.reason), {target: {value: '补全核验范围'}})
  expect(screen.getByRole('button', {name: labels.send.submit})).toBeEnabled()
  vi.mocked(fetchOperatorWorkdraft).mockResolvedValue({...saved, revision: 3, body: {...saved.body, tagline: '作者的新说明'}})
  await act(async () => { await client.invalidateQueries({queryKey: [...KEY, 'operator-workdraft', REQUEST]}) })
  expect(await screen.findByDisplayValue('作者的新说明')).toBeVisible()
  expect(screen.getByLabelText(name)).toHaveValue(saved.body.name)
  expect(screen.getByLabelText(labels.send.reason)).toHaveValue('')
})

it('数值等于与容差接受超出浮点范围的十进制输入，JSON 发送时变为 null', () => {
  for (const options of [{}, {min: 0}]) {
    const parsed = numberParser(options)('9'.repeat(310))
    expect(parsed).toEqual({ok: true, value: Infinity})
    expect(JSON.stringify(parsed)).toBe('{"ok":true,"value":null}')
  }
})

it('输出改名后，勾选新名称仍在必需清单里保留无法取消的旧名称', () => {
  function RenamedOutput() {
    const [step, update] = useState(() => {
      const step = newStep('s1')
      step.outputs = [{name: 'new_key', type: 'number', items: null}]
      step.checks = [{template: 'required', params: {keys: ['old_key']}}]
      return step
    })
    return <><Checks step={step} earlier={[]} base="steps/s1" onChange={checks => update({...step, checks})} />
      <output data-testid="retained-keys">{JSON.stringify(step.checks[0].params.keys)}</output></>
  }
  renderWith(<RenamedOutput />)
  expect(screen.queryByRole('checkbox', {name: 'old_key'})).toBeNull()
  fireEvent.click(screen.getByRole('checkbox', {name:'new_key'}))
  expect(screen.getByTestId('retained-keys')).toHaveTextContent('["old_key","new_key"]')
})
