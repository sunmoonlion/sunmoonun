import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, expect, it, vi } from 'vitest'
import { MethodSkillCenterSources } from '@/features/methods/ui/method-skill-center-sources'
import { WorkbenchProvider } from '@/lib/workbench/context'
import * as api from '@/lib/workbench/method-skill-center'
import zh from '@/messages/zh-CN.json'

afterEach(() => vi.restoreAllMocks())

it.each([1, 87382])('records the source submitted and the retry operation for %i Chinese characters', async (size) => {
  const list = vi.spyOn(api, 'listSources').mockResolvedValue([])
  const save = vi.spyOn(api, 'saveSource').mockRejectedValue(new Error('temporarily unavailable'))
  const client = new QueryClient({defaultOptions:{queries:{retry:false}}})
  render(<NextIntlClientProvider locale="zh-CN" messages={zh} timeZone="Asia/Shanghai">
    <QueryClientProvider client={client}><WorkbenchProvider csrfToken="fixture" locale="zh-CN">
      <MethodSkillCenterSources />
    </WorkbenchProvider></QueryClientProvider>
  </NextIntlClientProvider>)
  await screen.findByText(zh.directRegistry.empty)
  fireEvent.click(screen.getByRole('button', {name:zh.directRegistry.create}))
  fireEvent.change(screen.getByLabelText(zh.directRegistry.name), {target:{value:'核对'}})
  fireEvent.change(screen.getByLabelText(zh.directRegistry.content), {target:{value:'甲'.repeat(size)}})
  fireEvent.click(screen.getByRole('button', {name:zh.directRegistry.save.replace('{version}', '1')}))
  const alert = await screen.findByRole('alert')
  expect(save).toHaveBeenCalledTimes(1)
  expect(save.mock.calls[0][2].content).toHaveLength(size)
  const reads = list.mock.calls.length
  fireEvent.click(within(alert).getByRole('button', {name:zh.requestFailure.retry}))
  await waitFor(() => expect(list.mock.calls.length).toBeGreaterThan(reads))
  expect(save).toHaveBeenCalledTimes(1)
  expect(alert).toBeVisible()
})
