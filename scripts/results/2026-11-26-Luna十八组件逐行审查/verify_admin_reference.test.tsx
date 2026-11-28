import { fireEvent, render, screen, within } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { FeedbackProvider, SchemaForm } from '@/components/crud'
import { CrudReference } from '@/components/reference/crud-reference'

it('抽屉内外两个资源区被读为同一个名称', () => {
  render(<FeedbackProvider><CrudReference /></FeedbackProvider>)
  fireEvent.click(screen.getByRole('button',{name:'Open details drawer'}))
  const drawer = within(screen.getByRole('dialog'))
  expect(drawer.getByText('Drawer details')).toBeVisible()
  expect(drawer.getByRole('region',{name:'Resource details'})).toBeVisible()
})
it('参考页翻到第二页后仍显示原两行', () => {
  render(<FeedbackProvider><CrudReference /></FeedbackProvider>)
  const before = screen.getByRole('table').textContent
  fireEvent.click(screen.getByRole('button',{name:'Next'}))
  expect(screen.getByText('2 / 3')).toBeVisible()
  expect(screen.getByRole('table').textContent).toBe(before)
})
it('类型为 email 的字段明显格式错误时仍会提交', () => {
  const submit = vi.fn()
  render(<SchemaForm fields={[{name:'email', label:'Email', type:'email', required:true}]} submitLabel="Save" onSubmit={submit}/>)
  const input = screen.getByLabelText('Email') as HTMLInputElement
  fireEvent.change(input,{target:{value:'not-an-email'}})
  expect(input.validity.typeMismatch).toBe(true)
  fireEvent.click(screen.getByRole('button',{name:'Save'}))
  expect(submit).toHaveBeenCalledWith({email:'not-an-email'})
})
