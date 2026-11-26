import {expect, it} from 'vitest'
import {outputsSchema} from '@/contracts/knowbots'

it('同一份返回的两项最终交付在当前端可见几项', () => {
  const id = '6b8a6c3e-1f2d-4c5b-9a7e-6d5c4b3a2f10'
  const final_outputs = ['cash','income'].map(method_id => ({method_id, instance_id:method_id,
    result:{id, version:2, digest:'a'.repeat(64)}, artifact:{amount:800}}))
  const raw = {contract_version:1,test_id:id,run_id:'run-0001',consent_needed:false,
    cases:[{case_id:'c1',fetched_at:'2026-11-26T00:00:00Z',note:null,outputs:{
      contract:'knowbot-test-run/v1',run_id:'run-0001',case_id:'c1',plan_version:2,final_outputs,
      steps:[{step_id:'s1',outcome:'accepted',current:false}],
    }}]}
  const parsed = outputsSchema.parse(raw).cases[0].outputs
  if (process.env.LUNA_AUDIT_SURFACE === 'web') {
    expect(parsed).toMatchObject({plan_version:2, final_outputs, steps:[{current:false}]})
  } else {
    expect(parsed).not.toHaveProperty('plan_version')
    expect(parsed).not.toHaveProperty('final_outputs')
    expect(parsed?.steps?.[0]).not.toHaveProperty('current')
  }
})
