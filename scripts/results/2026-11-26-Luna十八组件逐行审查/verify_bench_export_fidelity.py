"""重开工作簿及 Word 压缩包，比较源文、存储值与可回查出处。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path("knowbench-app/knowbench-web-frontend/app").resolve()
tests = app / "tests/unit"
fixture = (tests / "deliverable-export.test.ts").read_text().split("const NOTE =", 1)[0]
cases = r"""
const source = { path: 'report.md', exportedAt: new Date(0), sheetSource: '出处', notes: '核查' }
it('rewrites identifiers and non-numeric cells in the delivered workbook', async () => {
  const markdown = '| 代码 | 凭证号 | 两项 | 原文 |\n|---|---|---|---|\n|000858|9007199254740993|1,2|3 4|'
  const book = new ExcelJS.Workbook()
  await book.xlsx.load(await bytes(await tablesToXlsx(tablesOf(parseMarkdown(markdown)), source)))
  expect(book.worksheets[0].getRow(2).values).toEqual([undefined,858,9007199254740992,12,34])
})
it.each(["History", "'利润表'"])('fails to export a valid Markdown heading %s', async (name) => {
  await expect(tablesToXlsx([{name,header:['x'],rows:[['1']]}], source)).rejects.toThrow()
})
it('loses the evidence URL of a reference-style link in Word', async () => {
  const doc = await markdownToDocx(parseMarkdown('见[核验原文][report]。\n\n[report]: https://example.org/annual'), 'test')
  const zip = await JSZip.loadAsync(await bytes(doc))
  expect(await zip.file('word/document.xml')!.async('string')).toContain('核验原文')
  expect(await zip.file('word/_rels/document.xml.rels')!.async('string')).not.toContain('example.org/annual')
})
it('exports completed and outstanding checklist items with identical body markup', async () => {
  const render = async (text: string) => {
    const zip = await JSZip.loadAsync(await bytes(await markdownToDocx(parseMarkdown(text),'test')))
    return (await zip.file('word/document.xml')!.async('string')).split('<w:body>')[1]
  }
  expect(await render('- [x] 核对余额')).toEqual(await render('- [ ] 核对余额'))
})
"""
with NamedTemporaryFile(dir=tests, suffix=".test.ts", mode="w") as target:
    target.write(fixture + cases)
    target.flush()
    subprocess.run(["node_modules/.bin/vitest", "run", target.name], cwd=app, check=True)
