// 复制到 KnowLab Web tests/component 下运行。
import { screen, fireEvent, waitFor } from '@testing-library/react'
import { it, expect, vi, beforeEach } from 'vitest'
import { ReviewView } from '@/components/knowbots/review-view'
import { fetchInbox, fetchDetail, reviewDraft } from '@/lib/knowbots/client'
import { detail, draft, expert, renderWith, REQUEST, EXPERT, CSRF, DRAFT } from './knowbot-fixtures'
import messages from '@/messages/zh-CN.json'

vi.mock('@/lib/knowbots/client', () => ({
  fetchInbox: vi.fn(), fetchDetail: vi.fn(), reviewDraft: vi.fn(),
}))
vi.mock('@/i18n/navigation', async () => (await import('./knowbot-fixtures')).linkMock())
beforeEach(() => vi.resetAllMocks())

it('已处理记录的链接会打开另一份仍可操作的审核表', async () => {
  vi.mocked(fetchDetail).mockResolvedValue(detail())
  vi.mocked(fetchInbox).mockResolvedValue({contract_version:1, answered:[], items:[
    {...draft(), request_id:REQUEST, title:'另一份待审稿',type:'draft',state:'todo'},
    {...expert(), request_id:REQUEST, title:'链接指定的已处理专家',type:'expert',state:'done'},
  ]})
  renderWith(<ReviewView picked={EXPERT} csrfToken={CSRF}/>)
  expect(await screen.findByRole('heading',{name:/另一份待审稿/})).toBeVisible()
  expect(screen.getByRole('button',{name:messages.knowbots.review.ok})).toBeEnabled()
})

it('作者的原始版本与验收用例未加载仍能提交同意', async () => {
  vi.mocked(fetchDetail).mockRejectedValue(new Error('读取申请详情失败'))
  vi.mocked(fetchInbox).mockResolvedValue({contract_version:1,answered:[],items:[
    {...draft(), request_id:REQUEST, title:'需要核对出处',type:'draft',state:'todo'},
  ]})
  renderWith(<ReviewView picked={DRAFT} csrfToken={CSRF}/>)
  const ok = await screen.findByRole('button',{name:messages.knowbots.review.ok})
  await waitFor(() => expect(fetchDetail).toHaveBeenCalled())
  expect(screen.queryByRole('alert')).toBeNull()
  fireEvent.click(ok)
  await waitFor(() => expect(reviewDraft).toHaveBeenCalledWith(DRAFT,{ok:true,note:''},CSRF))
})
