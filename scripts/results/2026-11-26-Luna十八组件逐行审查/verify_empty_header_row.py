"""在 KnowBase 后端 app 以 PYTHONPATH=.:tests 运行；同一本普通稀疏工作簿的两个视图。"""
from test_table_format import MAIN, XLSX, workbook
from app.domain.table_format import table_formats, column_status

sheet = (
    '<worksheet xmlns="' + MAIN[1:-1] + '"><sheetData>'
    '<row r="2"><c r="A2" t="inlineStr"><is><t>项目甲</t></is></c></row>'
    '</sheetData></worksheet>'
)
content = workbook(sheet=sheet)
summary = table_formats(XLSX, content)
probe = table_formats(XLSX, content, header_sheet="A & B")
assert summary[0].columns == ("项目甲",) and summary[0].rows == ()
assert probe[0].columns == ()
assert column_status(probe, "A & B", "项目甲") == "unknown"
