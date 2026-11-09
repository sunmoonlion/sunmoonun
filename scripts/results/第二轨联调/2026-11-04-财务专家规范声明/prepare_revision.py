"""Render the agreed capability format into the existing scope/v1 fields.

The cards are authoring evidence, not a new platform contract. No model calls.
"""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


CARDS = [
    {
        'id': 'F1', 'name': '历史财报指标与走势',
        'goal': '计算并描述营业收入、归母净利润、营业成本及核心财务指标的历史走势。',
        'scope': '一家中国A股上市公司；明确历史期间及合并或母公司口径。',
        'method': '毛利率=(营收−营业成本)/营收；净利率=归母净利润/营收；ROE按平均归母净资产；经营现金流/归母净利润；同比；明确要求时计算CAGR。',
        'prerequisites': '授权报表与可核页码原文；同比需比较期，平均净资产需期初期末，CAGR需起止数和年数；重述版本分开。',
        'deliverables': '年度金额、指标、走势、计算依据、口径及出处，纳入Markdown报告。',
        'exclusions': '不承诺因果识别、经营诊断、审计鉴证、横向选股；人均创收等非标准指标须先确认作者方法与人数口径，不自动视为覆盖。',
        'insufficient': '主体、期间或口径不清先澄清；缺数走数据确认；分母不成立标不适用；原题要求缺失不能报完成。',
        'positive': '计算某A股公司2021至2024年的营收、归母净利润、毛利率与三年营收CAGR。',
        'negative': '证明利润下降的唯一原因并提出经营改造方案。',
    },
    {
        'id': 'F2', 'name': '累计报表转单季',
        'goal': '将利润表、现金流量表的累计金额还原为单季序列。',
        'scope': '一家中国A股上市公司的可比季度序列，作为本专家分析或预测的输入。',
        'method': 'Q1=一季报；Q2=半年报−Q1；Q3=三季报−半年报；Q4=年报−三季报；资产负债表时点数不差分。',
        'prerequisites': '同口径、同版本链的累计报表及相邻累计期；使用前核对原四条恒等式，差额超过1元为不平，缺项不冒充通过。',
        'deliverables': '单季序列、差分计算依据、来源与不可用期间，纳入Markdown报告。',
        'exclusions': '不把年度数平均分摊为季度，不推造缺失季度，不将重述前后数据直接混算。',
        'insufficient': '缺相邻累计期先提数据需求；仍缺则明确不可还原，不用估算填充实际值。',
        'positive': '用半年报和一季报还原第二季度营业收入。',
        'negative': '只有年报，拆出四个季度的真实收入。',
    },
    {
        'id': 'F3', 'name': '分析结论与管理层讨论对照',
        'goal': '逐条判断本专家上游分析结论是否得到管理层讨论原文支持。',
        'scope': '依赖本次上游结论及对应年报；只读按目录定位的管理层讨论章节。',
        'method': '保留每条结论原文；完整同口径支持才判支持；未提及、仅部分支持或口径不同判不支持并说明。',
        'prerequisites': '可读且有页码的年报原文、章节定位和本次上游结论。',
        'deliverables': '逐条结论、支持/不支持、原因及支持项原文引文和页码，纳入Markdown报告。',
        'exclusions': '不支持不等于计算错误；不以其他章节代替管理层讨论，不据此保证结论因果正确或无舞弊。',
        'insufficient': '找不到章节或无上游结论如实说明，不能编引文或把缺少材料判为已核对。',
        'positive': '将本次营收同比结论对照年报管理层讨论，并引用支持它的原文。',
        'negative': '根据管理层讨论证明公司不存在财务造假。',
    },
    {
        'id': 'F4', 'name': '固定方法的两季度预测',
        'goal': '测算营业收入、归母净利润未来两个季度的点预测和区间。',
        'scope': '一家中国A股上市公司；明确预测起点、两个目标季度及可比金额口径。',
        'method': '上年同季×(1+近4季同比中位数)；上下界用近8季同比最小/最大值；先回测最近4个单季。',
        'prerequisites': '单季还原、同比和各回测时点所需历史窗口；预测使用期通过原四式核验，差额阈值1元，缺项或不平期不冒充合格；披露时点与重述差异另列。',
        'deliverables': '两季度点值及上下界、最近4季回测、计算依据、出处与局限，纳入Markdown报告。',
        'exclusions': '不做DCF、股价/目标价、五年预测、三表联动或用户指定的其他模型；区间不是统计置信区间，不保证实际值落入。',
        'insufficient': '起点不明确先澄清；缺数据先确认补取；窗口或核验仍不足则说明无法完成，不缩短回测要求冒充交付。',
        'positive': '按季节性同比法预测未来两季度营收和归母净利润，并回测最近4季。',
        'negative': '用DCF给出合理股价，或预测未来五年的三张报表。',
    },
]


def prepare():
    before = json.loads((HERE / 'before.json').read_text())
    assert before['revision'] == 39 and not before['active_tests']
    body = copy.deepcopy(before['body'])
    scope = {
        'does': '共同前提：资料经本次授权；可查询/补取不代表已具备，也不保证能取到。按已有八步流程执行，不承诺任意方法组合或即时完成。报表先按原四条恒等式核对：资产=负债+权益；归母净利润+少数股东损益=净利润；期末现金=期初现金+净增加额；本期期初=上期期末。年度衔接比余额，重述差异另列。最终交付财务分析报告.md。\n\n',
        'does_not': '共同限制：不提供评级、目标价、买卖建议、收益承诺；未声明的能力不能默认存在。免费、唯一可选或数据可读均不证明适用。\n\n',
        'elsewhere': '原题的必要结果、主体、期间、明确方法逐项核对；不能因部分相关就直接承接。能力不足说明缺口，可选择其他专家、通用模型或通过“去knowlab提交创意”提出孵化申请。可承接的缩小问题须本人明确接受；无答复不算同意，不自动换题、加预算或确认数据。\n\n',
    }
    for card in CARDS:
        title = f"【{card['id']} {card['name']}】"
        scope['does'] += title + '\n' + '\n'.join(f'{label}：{card[key]}' for label, key in [('目标','goal'),('范围','scope'),('方法','method'),('数据前提','prerequisites'),('交付','deliverables')]) + '\n\n'
        scope['does_not'] += title + card['exclusions'] + '\n不适用例：' + card['negative'] + '\n\n'
        scope['elsewhere'] += title + '\n条件不足：' + card['insufficient'] + '\n适用例：' + card['positive'] + '\n\n'
    scope = {k:v.strip() for k,v in scope.items()}
    assert all(0 < len(v) <= 2000 for v in scope.values()), {k:len(v) for k,v in scope.items()}
    assert not any(word in ''.join(scope.values()) for word in ('未复测','人工特批','测试状态','测试通过'))
    body['scope'] = scope
    assert {k:v for k,v in body.items() if k != 'scope'} == {k:v for k,v in before['body'].items() if k != 'scope'}
    revision = {'base_revision':before['revision'], 'base_body_sha256':sha(before['body']), 'body':body, 'edits':[['scope',scope]]}
    for name, value in [('capability-cards',CARDS),('revision',revision)]:
        (HERE / (name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    return {'scope_lengths':{k:len(v) for k,v in scope.items()}, 'unchanged_steps':len(body['steps']), 'body_sha256':sha(body)}


if __name__ == '__main__':
    print(json.dumps(prepare(), ensure_ascii=False))
