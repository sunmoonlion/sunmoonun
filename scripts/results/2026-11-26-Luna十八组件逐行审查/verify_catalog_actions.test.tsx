// Append to tests/component/expert-catalog.test.tsx to reuse its isolated navigation fixtures.
it.each(['tool', 'expert'] as const)('正式 %s 方法从目录可见，但无取得动作', async (kind) => {
  nav.search = 'kind=' + kind + '&from=knowbench&ref=expert'
  origin.data = { app: 'knowbench', ref: 'expert', return_url: 'https://knowbench.example' }
  vi.mocked(fetchExperts).mockResolvedValue({
    ...list,
    items: [{
      listing_id: ID, reference: { method_id: ID, version: 3, digest: 'sha256:' + 'a'.repeat(64) },
      method_kind: kind, name: '核对样本', tagline: '返回逐行差额', category,
      updated_at: '2026-10-18T00:00:00Z',
    }],
  })
  page(<ExpertCatalog csrfToken={CSRF} account={null} />)
  const card = (await screen.findByRole('heading', { name: '核对样本' })).closest('article')!
  expect(card.querySelector('details code')).toHaveTextContent(ID)
  expect(card.querySelector('a, button, form')).toBeNull()
})

it('移除关键词后再次回车会恢复刚移除的筛选', async () => {
  nav.search = 'q=预测'
  page(<ExpertCatalog csrfToken={CSRF} account={null} />)
  await screen.findByText('财务分析与预测')
  fireEvent.click(screen.getByRole('button', { name: '去掉「预测」' }))
  expect(nav.replace).toHaveBeenLastCalledWith('/zh-CN/knowbots')
  nav.search = ''
  fireEvent.submit(screen.getByRole('search'))
  expect(screen.getByRole('searchbox')).toHaveValue('预测')
  expect(nav.replace).toHaveBeenLastCalledWith('/zh-CN/knowbots?q=%E9%A2%84%E6%B5%8B')
})

it('运行端暂时不可用时专家详情却提示不存在', async () => {
  vi.mocked(fetchExpert).mockRejectedValue(new TypeError('Failed to fetch'))
  page(<ExpertDetail knowbotId={ID} csrfToken={CSRF} account={null} />)
  expect(await screen.findByRole('alert')).toHaveTextContent(messages.experts.notFound)
})

it('主人可调用的待处理版在版本记录中没有停用操作', async () => {
  vi.mocked(fetchExpert).mockResolvedValue({
    ...detail, summonable: true,
    versions: [{ ...detail.versions[0], status: 'held', held_reason: 'binding_deleted' }],
  })
  page(<ExpertDetail knowbotId={ID} csrfToken={CSRF} account={null} />)
  fireEvent.click(await screen.findByRole('tab', { name: '版本记录' }))
  expect(screen.getByRole('tabpanel')).toHaveTextContent(messages.experts.held)
  expect(screen.queryByRole('button', { name: '停用' })).toBeNull()
})

it('从结果打开专家再按详情的返回链接时遗失筛选与原页码', async () => {
  nav.search = 'from=knowbench&ref=expert&category=finance&q=季报&page=2'
  const view = page(<ExpertCatalog csrfToken={CSRF} account={null} />)
  const link = await screen.findByRole('link', { name: '财务分析与预测' })
  const href = link.getAttribute('href')!
  expect(href).not.toContain('category=')
  view.unmount()
  nav.search = href.split('?')[1]
  page(<ExpertDetail knowbotId={ID} csrfToken={CSRF} account={null} />)
  expect(await screen.findByRole('link', { name: messages.experts.back })).toHaveAttribute(
    'href', '/zh-CN/knowbots?from=knowbench&ref=expert',
  )
})
