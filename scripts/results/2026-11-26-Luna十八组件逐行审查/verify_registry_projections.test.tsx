// Append to KnowBench tests/component/registry.test.tsx to share the real providers.
it('安装列表显示修订3时，详情把修订4的入口列在旧标识下', async () => {
  vi.spyOn(registry, 'methodSkillCenterInventory').mockResolvedValue({
    installed: [asset], formal: methods, native: [],
  })
  vi.spyOn(registry, 'methodSkillCenterInstallation').mockResolvedValue({
    path: 'installed', asset_id, revision: 4, status: 'active',
    entries: [{ kind: 'mcp', entry: 'revision-four-only', tool_key: null }],
  })
  renderPage()
  fireEvent.click(screen.getByRole('button', { name: zh.methodSkillCenter.installed }))
  fireEvent.click(await screen.findByRole('button', { name: '查看安装入口' }))
  const article = (await screen.findByText('revision-four-only')).closest('article')!
  expect(article.textContent).toContain(zh.capabilities.revision.replace('{revision}', '3'))
})

it('清单请求失败时能切到最近记录页签，但没有读取活动服务', async () => {
  vi.spyOn(registry, 'methodSkillCenterInventory').mockRejectedValue(new Error('inventory offline'))
  const activity = vi.spyOn(registry, 'methodSkillCenterActivity').mockResolvedValue([])
  renderPage()
  fireEvent.click(screen.getByRole('button', { name: zh.methodSkillCenter.activity }))
  await screen.findByRole('alert')
  expect(activity).not.toHaveBeenCalled()
})

it('按问题找到确切专家后，请这版只携带版本，未交接检索所用的问题', async () => {
  const { reference, title } = methods[0]
  const question = '核对当前季度与去年同期的收入'
  vi.spyOn(registry, 'methodSkillCenterPlanningMethods').mockImplementation(async (_, basis) => ({
    items: basis.stage === 'directory' ? [] : [{
      method_id: reference.method_id, latest_version: reference.version,
      digest: reference.digest, method_kind: 'expert', title, summary: '核对季度数据',
    }], next: null,
  }))
  renderPage(<PlanningMethods />)
  fireEvent.change(screen.getByRole('textbox'), { target: { value: question } })
  fireEvent.click(screen.getByRole('button', { name: zh.methodSkillCenter.searchExperts }))
  const link = await screen.findByRole('link', { name: zh.methodSkillCenter.askVersion })
  const params = new URL(link.getAttribute('href')!, 'https://example.test').searchParams
  expect(JSON.parse(params.get('formalReference')!)).toEqual(reference)
  expect([...params.keys()].sort()).toEqual(['formalReference', 'mode'])
})
