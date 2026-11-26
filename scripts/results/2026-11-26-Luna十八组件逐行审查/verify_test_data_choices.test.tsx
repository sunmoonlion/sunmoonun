import { expect, it, vi } from 'vitest'
import { choiceOf } from '@/components/knowbots/self-test'
import { testDataRequestSchema } from '@/contracts/knowbots'
vi.mock('@/i18n/navigation', async () => (await import('@/tests/component/knowbot-fixtures')).linkMock())

const request = testDataRequestSchema.parse({
  question_id:'11111111-1111-4111-8111-111111111111',case_id:'c1',status:'proposed',
  missing:[], incomplete:[],
  needs:[{key:'annual', name:'两期年报', doc_type:'annual_report', required:true,
    period:{kind:'fixed',start:'2024-01-01',end:'2025-12-31'}}],
  items:[2024,2025].map(year=>({ref:'annual:'+year,need_key:'annual',
    key:{period_start:year+'-01-01',period_end:year+'-12-31'},
    status:'resolved', chosen:[{material_id:'m'+year,version_no:1}],candidates:[]})),
})
const added = [{doc_type:'semiannual_report',subject:null,from:2025,to:2025}]
it('adding an unrelated need and dropping one annual period removes both periods',()=>{
  const choice = choiceOf(request,{picks:{},edits:{}, dropped:['annual:2024'],added})
  expect(choice.needs?.map(n=>n.doc_type)).toEqual(['semiannual_report'])
  expect(choice.dropped).toBeUndefined()
})
it('adding an unrelated need loses the exact material choice for an unchanged need',()=>{
  const picks = {'annual:2025':{material_id:'m2025',version_no:1}}
  expect(choiceOf(request,{picks,edits:{},dropped:[],added:[]}).picks).toEqual(picks)
  expect(choiceOf(request,{picks,edits:{},dropped:[],added}).picks).toBeUndefined()
})
