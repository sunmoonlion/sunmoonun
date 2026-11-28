"""从小店的两个编辑按钮切换，核对实际保存的知识条目、标题和资料编号。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path('knowmart-app/knowmart-web-frontend/app').resolve()
tests = app / 'tests/component'
fixture = (tests/'market.test.tsx').read_text().split("describe('供需市场'",1)[0]
case = """
it('sends the first listing’s form to the second listing after switching edit targets', async () => {
  const rows = ['A','B'].map(id => ({...LISTING,listing_id:id,title:id,status:'draft',
    items:[{item_id:'file-'+id,name:id,media_type:'application/pdf',size_bytes:10}]}))
  vi.mocked(client.fetchMyExperts).mockResolvedValue({items:[]})
  vi.mocked(client.fetchMyListings).mockResolvedValue({items:rows})
  vi.mocked(client.fetchMyMaterials).mockResolvedValue({items:[]})
  vi.mocked(client.updateListing).mockResolvedValue({listing:rows[1]})
  page(<MyShopScreen account={null} csrfToken={CSRF} />)
  fireEvent.click(screen.getByRole('tab',{name:messages.marketUi.myShop.knowledge}))
  const buttons = await screen.findAllByRole('button',{name:messages.marketUi.edit})
  fireEvent.click(buttons[0])
  fireEvent.click(buttons[1])
  expect(screen.getByLabelText(messages.marketUi.mine.listingTitle)).toHaveValue('A')
  fireEvent.click(screen.getByRole('button',{name:messages.marketUi.save}))
  await waitFor(() => expect(client.updateListing).toHaveBeenCalledWith(CSRF,'B',
    expect.objectContaining({title:'A',items:[{item_id:'file-A'}]})))
})
"""
with NamedTemporaryFile(dir=tests,suffix='.test.tsx',mode='w') as f:
    f.write(fixture+case)
    f.flush()
    subprocess.run(['node_modules/.bin/vitest','run',f.name],cwd=app,check=True)
