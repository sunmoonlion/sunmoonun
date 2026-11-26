// 在 KnowMart Web 的 Vitest 环境运行。替换登录依赖以记录未登录时交给登录页的 next。
import { expect, it, vi } from 'vitest'
import ExpertPage from '@/app/[locale]/(dashboard)/knowbots/[id]/page'
import KnowledgePage from '@/app/[locale]/(dashboard)/knowledge/[id]/page'
import { nextPath } from '@/lib/auth/next-path'

const log = vi.hoisted(() => ({ targets: [] as string[] }))
vi.mock('@/lib/server/auth-session', () => ({
  requireBrowserSession: async (_locale: string, target: string) => {
    log.targets.push(target)
    throw new Error('login')
  },
}))
vi.mock('next-intl/server', () => ({ getTranslations: vi.fn() }))
vi.mock('@/components/knowbots/expert-detail', () => ({ ExpertDetail: vi.fn() }))
vi.mock('@/components/market/knowledge-market', () => ({ KnowledgeDetail: vi.fn() }))

it('drops the selected knowledge demand and exact expert before sending the visitor to login', async () => {
  const locale = 'zh-CN'
  const id = 'ba17e908-0dd6-413c-8c79-a1ad06cf599b'
  const params = Promise.resolve({ locale, id })
  const wanted = '/' + locale + '/knowledge/' + id + '?demand=chosen-demand'
  expect(nextPath(locale, wanted, '/')).toEqual(wanted)
  await expect(KnowledgePage({params, searchParams: Promise.resolve({demand:'chosen-demand'})}))
    .rejects.toThrow('login')
  await expect(ExpertPage({params})).rejects.toThrow('login')
  expect(log.targets).toEqual(['/' + locale + '/knowledge/' + id, '/' + locale + '/knowbots'])
})
