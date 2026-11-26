import { readFileSync } from 'node:fs'
import { expect, it } from 'vitest'
import { detailSchema } from '@/contracts/knowbots'

it('the operator can parse the name before material confirmation and fails afterwards', () => {
  const [before, after] = JSON.parse(readFileSync(process.env.LUNA_COMPLETED_DETAIL!, 'utf8'))
  expect(detailSchema.parse(before).answered).toEqual([])
  const seen = detailSchema.safeParse(after)
  expect(seen.success).toBe(false)
  if (seen.success) throw new Error('expected detail reader to reject the material response')
  expect(seen.error.issues.map(issue => issue.path)).toEqual([
    ['answered', 0, 'kind'], ['answered', 0, 'answer', 'data'],
  ])
})
