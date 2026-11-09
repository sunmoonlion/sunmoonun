"""Repair only the approved continuity meaning; no model call or production write."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def prepare(before):
    body = copy.deepcopy(before['body'])
    steps = {s['id']: s for s in body['steps']}
    rule = {
        'id': 'opening_balance_continuity',
        'text': '第四条只核同一存量科目的本期期初余额与上期期末余额。现金及现金等价物读现金流量表期初/期末；资产、负债、权益等读资产负债表年初/上年年末。两端是同一时点、同一合并范围和可比口径，保留两份报告版本及页码。营业收入、营业成本、归母净利润是期间流量，不得列入continuity_plan或continuity_checks。同一年度在两份报告中的原值和重述值比较单独记restatement_differences，不得当作本条不平，也不得仅因重述差额剔除预测期间。最新报告没有下一年度报告不构成缺项：本期报告的年初余额与上年度期末余额即可比较；有追溯调整时分别交代原版、重述版及桥接原因，不能混口径凑平。真实余额衔接差额绝对值超过1元仍按原规则处理，确实缺少前期余额则明确未核验并走原补数流程。'
    }
    meta = ['account', 'balance_date', 'scope', 'opening_report', 'previous_report', 'account_kind', 'comparison_kind']
    for sid, path in [('inventory', 'continuity_plan'), ('reconcile', 'continuity_checks'), ('reconcile', 'continuity_missing')]:
        step=steps[sid]
        for output in step['outputs']:
            if output['name']==path:
                output['items'] += [{'name':k,'type':'text'} for k in meta]
        step['checks'] += [
            {'template':'each_has','params':{'path':path,'keys':meta,'non_empty_keys':meta}},
            {'template':'each_has','params':{'path':path,'field':'account_kind','values':['stock_balance']}},
            {'template':'each_has','params':{'path':path,'field':'comparison_kind','values':['opening_to_previous_closing']}},
        ]
    for sid in ('inventory','reconcile'):
        steps[sid]['rules'].append(copy.deepcopy(rule))
        steps[sid]['rules'].append({'id':'continuity_metadata','text':'continuity各行account_kind固定为stock_balance、comparison_kind为opening_to_previous_closing；account写真实存量科目，不得把流量改名冒充。balance_date写两端共同余额时点，scope写合并范围，opening_report与previous_report注明各自报告及版本。key及全部元数据由inventory清单逐字传递；continuity_missing同样带这些元数据，缺原件写明而非猜测。'})
    steps['reconcile']['checks'].append({'template':'quoted','params':{'path':'continuity_checks','field':'account_kind','equals':'stock_balance'}})
    steps['reconcile']['outputs'].append({'name':'restatement_differences','type':'list','items':None})
    steps['reconcile']['rules'].append({'id':'continuity_evidence','text':'每条continuity_checks的quotes必须分别包含两端余额原文及页码，不得引用利润表流量作为余额。计算仍用OPEN-PREV_CLOSE、实际差额和原compute_id。restatement_differences只解释版本间重述及可比来源链，无差异交空列表，不充当第五条恒等式。独立查询/计算可以批量，但不改变四式、1元阈值、期间与计算收据。'})
    for sid in ('series','forecast','writeup'):
        steps[sid]['rules'].append({'id':'continuity_and_restatement','text':'余额衔接只看reconcile中同一时点同一存量科目opening_to_previous_closing记录。restatement_differences是披露版本差异，不得称为会计不平或据此剔除期间；累计转单季仍固定可比来源链。不能因为没有更晚年度报告就标当前期间衔接未核验。真实四式不平、缺项、未核验继续按作者原规则处理，不降低原预测窗口与回测要求。成稿准确区分原式核验、重述说明和缺项，不宣称四式全通过。'})
    for r in steps['inventory']['rules']:
        if r['id'] not in ('opening_balance_continuity', 'continuity_metadata'):
            r['text'] = r['text'].replace('每项只交回 key；', '前三类每项交回key，continuity_plan另外交回下列余额元数据；')
    body['tagline'] = before['body']['tagline'] + '（人工特批，本修订未复测）'
    edits=[['tagline', body['tagline']]]
    old={s['id']:s for s in before['body']['steps']}
    for sid,step in steps.items():
        for field in ('rules','outputs','checks'):
            if old[sid][field]!=step[field]:edits.append([f'steps/{sid}/{field}',step[field]])
    assert all(steps[sid]==old[sid] for sid in ('scope','indicators','official'))
    return {'base_revision':before['revision'],'base_body_sha256':sha(before['body']),'body':body,'edits':edits,
            'limits':'Metadata allowlists and actual quotes reject the observed flow-comparison shape; mislabeled source semantics still require review. No claim of a new live test.'}


if __name__=='__main__':
    out=prepare(json.loads((HERE/'before.json').read_text()))
    (HERE/'revision.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'edits':len(out['edits']),'digest':sha(out['body'])}))
