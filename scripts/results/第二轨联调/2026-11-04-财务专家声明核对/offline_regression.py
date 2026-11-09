"""Synthetic output checks through the real judge; no semantic/model claims."""
import copy
import json
from pathlib import Path

from app.application.workbench.acceptance import judge
from app.application.workbench.acceptance_numbers import _covers
from app.domain.workbench.packs import ExpertPack

HERE=Path(__file__).resolve().parent
pack=ExpertPack.model_validate({**json.loads((HERE/'draft-manifest.json').read_text())['pack'], 'profile_id':'SYNTHETIC_SCOPE_REVISION'})
scope=pack.workflow[0]
report=pack.workflow[-1]
requests=[{'id':str(i),'question_quote':q,'requested_result':q,'requested_method':'未指定','scope_reason':'已列明的指标计算','status':'covered'} for i,q in enumerate(['计算营业收入','计算营收CAGR'],1)]
scoped={'company':'合成公司','in_data':'合成数据','request_items':requests,'excluded_requests':[]}
good={'report':'合成验证用，不是财务报告','request_results':[{'request_id':r['id'],'status':'completed','answer':'合成结果','basis':'synthetic:indicators'} for r in requests],'unanswered_requests':[]}

def accepted(output):
    result=judge(json.dumps(output,ensure_ascii=False),report.acceptance)
    return result.ok and not any(_covers(rule,result.parsed,{'scope':scoped}) for rule in report.acceptance if rule.kind=='covers')

checks={'complete':accepted(good),'scope_complete':judge(json.dumps(scoped),scope.acceptance).ok}
for name,mutate in [
 ('missing',lambda d:d['request_results'].pop()),
 ('duplicate',lambda d:d['request_results'].append(copy.deepcopy(d['request_results'][0]))),
 ('different_requirement',lambda d:d['request_results'][0].update(request_id='DCF')),
 ('unanswered',lambda d:d['request_results'][0].update(status='unanswered')),
 ('explicit_gap',lambda d:d['unanswered_requests'].append('CAGR没有算出')),
 ('blank_answer',lambda d:d['request_results'][0].update(answer=' ')),
 ('blank_basis',lambda d:d['request_results'][0].update(basis='')),
 ('blank_report',lambda d:d.update(report='')),
]:
    bad=copy.deepcopy(good);mutate(bad);checks[name]=not accepted(bad)
bad=copy.deepcopy(scoped);bad['request_items'][0]['status']='uncovered'
checks['scope_uncovered']=not judge(json.dumps(bad),scope.acceptance).ok
bad=copy.deepcopy(scoped);bad['request_items']=[]
checks['scope_empty']=not judge(json.dumps(bad),scope.acceptance).ok
assert all(checks.values()),checks
result={'synthetic_only':True,'checks':checks,'passed':sum(checks.values()),'model_calls':0,'limitations':'不能独立证明模型拆题和语义判断正确，不能当作本专家已完成实战复测。'}
(HERE/'offline-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
