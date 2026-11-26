// 在 KnowLab Web 的 tests/component 下运行。
import { it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { Overview } from '@/components/knowbots/overview'
import { fetchApplications, fetchExperts, fetchInbox } from '@/lib/knowbots/client'
import { expert, renderWith, REQUEST, EXPERT } from './knowbot-fixtures'

vi.mock('@/lib/knowbots/client', () => ({
  fetchApplications: vi.fn(), fetchExperts: vi.fn(), fetchInbox: vi.fn(),
}))
vi.mock('@/i18n/navigation', async () => (await import('./knowbot-fixtures')).linkMock())

it('首页会把明确没有重测的人工放行版本描述成测试通过', async () => {
  vi.mocked(fetchApplications).mockResolvedValue([])
  vi.mocked(fetchExperts).mockResolvedValue([])
  vi.mocked(fetchInbox).mockResolvedValue({
    contract_version: 1, answered: [],
    items: [{
      ...expert({stage:'awaiting_user',test_id:null,test_number:null,test_mode:null,
        manual_release:{release_id:EXPERT,manifest_sha256:'a'.repeat(64),retested:false}}),
      request_id:REQUEST, title:'未重测版本', type:'expert', state:'todo',
    }],
  })
  renderWith(<Overview />)
  expect(await screen.findByRole('status')).toHaveTextContent('未重测版本」测试通过了')
})
