import { afterEach, expect, it, vi } from 'vitest'
import { act, cleanup, renderHook, waitFor } from '@testing-library/react'
import { PlatformProviders } from '@/components/platform/providers'
import { useRunProjection } from '@/lib/interaction/use-run-projection'
import { applyRunEvent, createRunProjection } from '@/lib/interaction/projection'
import type { RunEvent, RunSnapshot } from '@/contracts/interaction'

const run = crypto.randomUUID()
const snapshot: RunSnapshot = {
  contract_version: 1, run_id: run, title: 'test', status: 'running', summary: null,
  last_sequence_no: 1, last_event_id: crypto.randomUUID(), citations: [],
  required_action: null, updated_at: new Date().toISOString(),
}
const event = (n: number, status: RunSnapshot['status']): RunEvent => ({
  contract_version: 1, run_id: run, event_id: crypto.randomUUID(), sequence_no: n,
  occurred_at: snapshot.updated_at, type: 'status', data: { status },
})
afterEach(() => { cleanup(); vi.unstubAllGlobals() })

it('状态事件取消了任务，投影仍保留待确认事项', () => {
  const action = {kind: 'confirmation' as const, action_id: crypto.randomUUID(), prompt: '确认'}
  const result = applyRunEvent(createRunProjection({...snapshot, status:'waiting_for_input', required_action: action}),
    event(2,'cancelled'))
  expect(result.projection.snapshot.status).toBe('cancelled')
  expect(result.projection.snapshot.required_action).toEqual(action)
})

it('序号跳跃后补读相同快照，旧连接已关闭且没有重新订阅', async () => {
  const connections: Stream[] = []
  class Stream extends EventTarget {
    closed = false
    constructor() { super(); connections.push(this) }
    close() { this.closed = true }
  }
  const fetch = vi.fn(async () => Response.json(snapshot))
  vi.stubGlobal('fetch', fetch)
  vi.stubGlobal('EventSource', Stream)
  const hook = renderHook(() => useRunProjection(run,'test'), {wrapper: PlatformProviders})
  await waitFor(() => expect(connections).toHaveLength(1))
  const gap = event(3,'running')
  await act(async () => {
    connections[0].dispatchEvent(new MessageEvent('run-event', {
      data: JSON.stringify(gap), lastEventId: gap.event_id,
    }))
  })
  await waitFor(() => expect(fetch).toHaveBeenCalledTimes(2))
  expect(hook.result.current.streamState).toBe('reconciling')
  expect(connections).toHaveLength(1)
  expect(connections[0].closed).toBe(true)
})
