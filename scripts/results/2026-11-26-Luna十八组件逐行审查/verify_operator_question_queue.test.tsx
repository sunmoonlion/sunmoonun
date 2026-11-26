import { readFileSync } from 'node:fs'
import { expect, it } from 'vitest'
import { questionsSchema } from '@/contracts/knowbots'

it('a waiting data question invalidates the complete operator response', () => {
  const body = JSON.parse(readFileSync(process.env.LUNA_QUEUE_RESPONSE!, 'utf8'))
  const result = questionsSchema.safeParse(body)
  expect(result.success).toBe(false)
  if (result.success) throw new Error('unexpected valid question list')
  const index = body.questions.findIndex((q: {kind: string}) => q.kind === 'data')
  expect(result.error.issues.map(issue => issue.path)).toEqual([['questions', index, 'kind']])
  const rest = body.questions.filter((q: {kind: string}) => q.kind !== 'data')
  expect(questionsSchema.parse({...body, questions: rest}).questions).toHaveLength(3)
})

import { fireEvent, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'
import { OpenQuestions } from '@/components/knowbots/open-questions'
import { answerQuestion } from '@/lib/knowbots/client'
import { renderWith } from './knowbot-fixtures'

vi.mock('@/lib/knowbots/client', () => ({answerQuestion: vi.fn()}))

it('the operator sees identical feedback when forwarding succeeds and when it is pending', async () => {
  const body = JSON.parse(readFileSync(process.env.LUNA_QUEUE_RESPONSE!, 'utf8'))
  const rows = questionsSchema.parse({...body, questions: body.questions.filter(
    (row: {kind: string}) => row.kind === 'tool_approval'
  )}).questions
  const views: string[] = []
  for (const sent of [false, true]) {
    vi.mocked(answerQuestion).mockClear().mockResolvedValue(sent)
    const view = renderWith(<OpenQuestions csrfToken="test" questions={rows} />)
    const approve = screen.getAllByRole('button')[0]!
    fireEvent.click(approve)
    await waitFor(() => expect(answerQuestion).toHaveBeenCalledOnce())
    await waitFor(() => expect(approve).toBeEnabled())
    views.push(view.container.textContent ?? '')
    view.unmount()
  }
  expect(views[0]).toBe(views[1])
})
