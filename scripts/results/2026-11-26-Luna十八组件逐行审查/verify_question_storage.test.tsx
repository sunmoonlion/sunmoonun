import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { NextIntlClientProvider } from 'next-intl'
import { expect, it, vi } from 'vitest'
import { AskExpertScreen } from '@/features/expert'
import { WorkbenchProvider } from '@/lib/workbench/context'
import messages from '@/messages/zh-CN.json'

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
  usePathname: () => '/zh-CN/workbench/expert',
}))

it('storage policy failure reaches the page even for a question from a conversation', () => {
  const storage = vi.spyOn(Storage.prototype, 'getItem').mockImplementation(key => {
    if (key === 'workbench.question') throw new DOMException('Storage denied', 'SecurityError')
    return null
  })
  try {
    expect(() => render(
      <NextIntlClientProvider locale="zh-CN" messages={messages} timeZone="Asia/Shanghai">
        <QueryClientProvider client={new QueryClient()}>
          <WorkbenchProvider locale="zh-CN" csrfToken="test">
            <AskExpertScreen project="project" from="conversation" />
          </WorkbenchProvider>
        </QueryClientProvider>
      </NextIntlClientProvider>
    )).toThrow('Storage denied')
  } finally {
    storage.mockRestore()
  }
})
