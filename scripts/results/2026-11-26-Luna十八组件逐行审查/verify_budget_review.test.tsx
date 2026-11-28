import { fireEvent, render, screen } from '@testing-library/react'
import { NextIntlClientProvider } from 'next-intl'
import { expect, it, vi } from 'vitest'
import { reviewSchema } from '@/contracts/workbench-v2'
import { ReviewPanel } from '@/features/expert/ui/review-panel'
import messages from '@/messages/zh-CN.json'
import example from '@/preview/fixtures/full/0202.json'

it('点击追加，检查实际交给运行页的答复', () => {
  const original = example.interaction
  const review = reviewSchema.parse({
    ...example,
    interaction: {
      ...original, kind: 'resource', status: 'pending',
      pending: { ...original.pending, options: [
        { id: 'topup', label: '追加', consequence: '增加本次预算', needs_amount: true },
      ] },
    },
  }).interaction
  const send = vi.fn()
  render(<NextIntlClientProvider locale="zh-CN" messages={messages} timeZone="Asia/Shanghai">
    <ReviewPanel review={review} token="test" answering={false} failed={false} onAnswer={send} />
  </NextIntlClientProvider>)
  expect(screen.queryByRole('spinbutton')).toBeNull()
  expect(screen.queryByRole('textbox')).toBeNull()
  fireEvent.click(screen.getByRole('button', { name: '追加' }))
  expect(send).toHaveBeenCalledWith({ decision: 'topup' })
})
