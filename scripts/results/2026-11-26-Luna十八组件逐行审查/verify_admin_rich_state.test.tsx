import { fireEvent, render, screen } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { LongPressButton } from '@/components/rich/behavior-tools'
import { MediaPlayer } from '@/components/rich/media-player'
import { MetricChart } from '@/components/rich/metric-chart'
import { MarkdownEditor } from '@/components/rich/markdown-editor'

it('fires a pending long press after the user leaves the page', () => {
  vi.useFakeTimers()
  try {
    const accepted = vi.fn()
    const panel = render(<LongPressButton label="执行" onLongPress={accepted} />)
    fireEvent.pointerDown(screen.getByRole('button'))
    panel.unmount()
    vi.advanceTimersByTime(610)
    expect(accepted).toHaveBeenCalledOnce()
  } finally {
    vi.useRealTimers()
  }
})
it('does not attempt the new media source after the preceding source failed', () => {
  const panel = render(<MediaPlayer type="audio" src="/media/a.mp3" label="录音" />)
  fireEvent.error(screen.getByLabelText('录音'))
  panel.rerender(<MediaPlayer type="audio" src="/media/b.mp3" label="录音" />)
  expect(panel.container.querySelector('audio')).toBeNull()
})
it('draws identical bars for zero and either negative magnitude', () => {
  const panel = render(<MetricChart title="变化" points={[
    { label: '甲', value: -100 }, { label: '乙', value: -1 }, { label: '丙', value: 0 },
  ]} />)
  expect([...panel.container.querySelectorAll('rect')].map(r => r.getAttribute('height'))).toEqual(['2','2','2'])
})
it('points the second editor label at the first editor', () => {
  const panel = render(<><MarkdownEditor label="甲" value="A" onChange={() => {}} />
                          <MarkdownEditor label="乙" value="B" onChange={() => {}} /></>)
  const labels = panel.container.querySelectorAll('label')
  expect(labels[1].control).toBe(panel.container.querySelectorAll('textarea')[0])
})
