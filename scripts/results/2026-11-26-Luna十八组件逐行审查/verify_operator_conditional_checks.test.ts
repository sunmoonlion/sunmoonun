import { expect, it } from 'vitest'
import { bodySchema } from '@/contracts/workdraft'
import { toProposals } from '@/lib/knowbots/proposals'
import { newStep } from '@/lib/knowbots/workdraft'

it('editing one check proposes removing the other check’s input condition', () => {
  const step = { ...newStep('report'), uses: ['review'], input_required: { review: false },
    checks: [
      { template: 'list_min', params: { path: 'rows', min: 1 } },
      { template: 'non_empty', params: { path: 'findings' }, when_input_present: 'review' },
    ] }
  const saved = bodySchema.parse({ name: '汇总', tagline: '', scope: {does:'',does_not:'',elsewhere:''},
    steps: [newStep('review'),step], data_picks: [] })
  const local = structuredClone(saved)
  local.steps[1].checks[0].params.min = 2
  const { proposals } = toProposals(saved,local,'要求至少两行')
  expect(proposals).toHaveLength(1)
  expect(proposals[0].path).toBe('steps/report/checks')
  expect(proposals[0].value).toEqual([
    { template: 'list_min', params: { path: 'rows', min: 2 } },
    { template: 'non_empty', params: { path: 'findings' } },
  ])
})
