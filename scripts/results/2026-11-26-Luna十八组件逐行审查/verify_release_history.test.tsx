// 在 KnowLab Web 的 tests/component 下运行，使用项目的作者身份和详情夹具。
import { expect, it, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { ManualReleaseRequest } from '@/components/knowbots/manual-release'
import { fetchManualReleases } from '@/lib/knowbots/manual-release'
import { CSRF, DRAFT, EXPERT, detail, draft, renderWith, testRecord } from './knowbot-fixtures'
import messages from '@/messages/zh-CN.json'

vi.mock('@/lib/knowbots/manual-release', () => ({
  fetchManualReleases: vi.fn(),
  requestManualRelease: vi.fn(),
}))

it('冷启动时，目标稿开始测试后已驳回的放行申请无法从详情查看', () => {
  const life = detail({
    experts: [],
    drafts: [draft({ revision: 1 }), draft({ draft_id: EXPERT, revision: 2 })],
    tests: [
      testRecord({ draft_id: DRAFT, status: 'passed' }),
      testRecord({ draft_id: EXPERT, status: 'running' }),
    ],
  })
  vi.mocked(fetchManualReleases).mockResolvedValue([
    { request_id: life.request_id, draft_id: EXPERT, status: 'rejected', decision_reason: '需重测' },
  ] as Awaited<ReturnType<typeof fetchManualReleases>>)
  renderWith(<ManualReleaseRequest life={life} csrfToken={CSRF} />)
  expect(screen.queryByText(messages.knowbots.manualRelease.title)).toBeNull()
  expect(fetchManualReleases).not.toHaveBeenCalled()
})
