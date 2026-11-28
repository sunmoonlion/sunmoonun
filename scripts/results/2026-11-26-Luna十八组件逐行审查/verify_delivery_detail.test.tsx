import { fireEvent, screen, waitFor } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { DeliveryView } from '@/components/knowbots/delivery-view'
import { IncubationView } from '@/components/knowbots/incubation-view'
import { fetchIncubation, returnExpert, fetchCategories, fetchDelivery, fetchDetail } from '@/lib/knowbots/client'
import messages from '@/messages/zh-CN.json'
import { CSRF, REQUEST, detail, delivery, deliveryItem, renderWith } from './knowbot-fixtures'

vi.mock('@/lib/knowbots/client', () => ({
  fetchIncubation: vi.fn(), returnExpert: vi.fn(), fetchDetail: vi.fn(), fetchDelivery: vi.fn(), fetchCategories: vi.fn(),
}))
vi.mock('@/i18n/navigation', async () => (await import('./knowbot-fixtures')).linkMock())

it('测试详情和分类查询失败时仍报告没有测试记录，公开审核没有类目也没有错误反馈', async () => {
  const d = delivery({needs_rerun:false})
  const item = deliveryItem({deliveries:[d]})
  expect(item.test_id).toBeTruthy()
  vi.mocked(fetchDelivery).mockResolvedValue([item])
  vi.mocked(fetchDetail).mockRejectedValue(new Error('详情未能加载'))
  vi.mocked(fetchCategories).mockRejectedValue(new Error('分类未能加载'))
  renderWith(<DeliveryView csrfToken={CSRF}/>)
  const k = messages.knowbots.delivery
  expect(await screen.findByText(k.noTestRecord)).toBeVisible()
  await vi.waitFor(() => expect(fetchCategories).toHaveBeenCalled())
  expect(screen.getByRole('combobox',{name:k.category}).querySelectorAll('option')).toHaveLength(1)
  expect(screen.getByRole('button',{name:k.approve})).toBeDisabled()
  expect(screen.queryByText(messages.knowbots.loadFailed)).toBeNull()
  expect(screen.queryByRole('alert')).toBeNull()
})

it('指定记录已消失的交付链接，自动切换到另一条可交付的记录', async () => {
  const actual = deliveryItem()
  vi.mocked(fetchDelivery).mockResolvedValue([actual])
  vi.mocked(fetchDetail).mockResolvedValue(detail())
  renderWith(<DeliveryView picked="missing-expert" csrfToken={CSRF}/>)
  const act = await screen.findByRole('button',{name:messages.knowbots.delivery.return})
  fireEvent.click(act)
  await waitFor(() => expect(returnExpert).toHaveBeenCalledWith(actual.expert_id, CSRF))
})
it('选择孵化旧版创意，预览正确切换，工作稿入口始终相同', async () => {
  const d = detail()
  vi.mocked(fetchIncubation).mockResolvedValue([{request_id:REQUEST,title:d.title,owner_subject:d.owner_subject,
    latest_version:2,latest_accepted:2,category:'todo',draft:null}])
  vi.mocked(fetchDetail).mockResolvedValue(d)
  renderWith(<IncubationView csrfToken={CSRF}/>)
  const hatch = messages.knowbots.hatch
  const selector = await screen.findByLabelText(hatch.pick)
  const editor = () => screen.getByRole('link',{name:hatch.openEditor}).getAttribute('href')
  const latest = editor()
  fireEvent.change(selector,{target:{value:'1'}})
  expect(screen.getByText('# 我的方法')).toBeVisible()
  expect(editor()).toBe(latest)
  expect(editor()).toBe('/names/' + REQUEST + '/workdraft')
})
