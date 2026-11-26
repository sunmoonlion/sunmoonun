import { screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { DeliveryView } from '@/components/knowbots/delivery-view'
import { fetchCategories, fetchDelivery, fetchDetail } from '@/lib/knowbots/client'
import messages from '@/messages/zh-CN.json'
import { CSRF, delivery, deliveryItem, renderWith } from './knowbot-fixtures'

vi.mock('@/lib/knowbots/client', () => ({
  fetchDetail: vi.fn(), fetchDelivery: vi.fn(), fetchCategories: vi.fn(),
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
