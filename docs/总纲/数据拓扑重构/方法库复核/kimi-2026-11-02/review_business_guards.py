"""Independent regression expectations; run against the actual knowbench judge."""
import json
import os
from pathlib import Path

import pytest

from app.application.workbench.acceptance import judge
from app.application.workbench.acceptance_numbers import judge_numbers
from app.domain.workbench.method_catalog import ReferencedMethodCatalog

MANIFEST = Path(os.environ.get('METHOD_REVIEW_MANIFEST', '/home/zymun/worktrees/kimi/knowlab-app/knowlab-backend/app/tests/fixtures/financial-expert-manifest.json'))
CATALOG = ReferencedMethodCatalog.model_validate(json.loads(MANIFEST.read_text())['pack'])

class Repo:
    def __init__(self, events=(), artifacts=()):
        self.events = events
        self.artifacts = artifacts
    async def list_task_events(self, task_id, **kwargs):
        return self.events
    async def list_artifacts_with_content(self, task_id):
        return self.artifacts

def event(cursor, value, expression):
    return {'cursor': cursor, 'payload': {'value': str(value), 'expression': expression}}

async def verdict(name, output, repo=None):
    unit = next(u for u in CATALOG.method_units if u.contract.step_id == name)
    result = await judge_numbers(judge(json.dumps(output), unit.contract.acceptance), unit.contract.acceptance, repo=repo or Repo(), task={'id': 'review-task'})
    print(json.dumps({'method':name,'ok':result.ok,'failures':result.failures},ensure_ascii=False))
    return result

@pytest.mark.asyncio
async def test_m02_two_equal_nonzero_differences_must_not_be_balanced():
    events = [event(1,999999,'abs(total_assets - (total_liabilities + equity))'),event(2,999999,'abs(opening_assets - (opening_liabilities + opening_equity))')]
    output = {'reconciliation_status':'平衡', 'balance_sheet_balance_diff':{'value':999999,'compute_id':'c1','left_id':'c1','right_id':'c2'},'audit_reconciliations':[
        {'check_name':name,'passed':True,'diff':999999}
        for name in ['期末资产=负债+权益','期初资产=负债+权益','净利润与未分配利润勾稽','现金流量净额勾稽','期初数与上年期末数一致']
    ]}
    result = await verdict('accounting_statement_reconciliation',output,Repo(events))
    assert not result.ok, '999999 元差额被判平衡；比较两个差额相等不等于差额接近零'

@pytest.mark.asyncio
async def test_m18_other_kam_title_without_quotes_or_valid_page_must_fail():
    output = {'audit_opinion_type':'无保留意见','kam_topics_count':1,'kam_matters':[{'matter':'商誉减值','audit_response':'执行审计程序','page':0,'quotes':[]}],'external_guarantee_ratio':0,'contingent_liability_risk_verdict':'低'}
    result = await verdict('kam_contingent_liability_audit',output)
    assert not result.ok, '非固定标题 KAM 无引文、page=0 仍通过，审计意见亦无引文'

@pytest.mark.asyncio
async def test_m13_empty_forecasts_cannot_satisfy_two_quarters_three_scenarios():
    output = {'forecast_income_statement':[],'forecast_balance_sheet':[],'forecast_cashflow_statement':[],'balance_sheet_plug_zero':{'value':999999,'left_id':'c1','right_id':'c1'}}
    result = await verdict('three_statement_linked_forecasting',output,Repo([event(1,999999,'assets - liabilities - equity')]))
    assert not result.ok, '三张预测表全空且残差非零仍通过'

@pytest.mark.asyncio
async def test_m04_accepted_output_must_feed_m20_successfully():
    factors={'tax_burden':0.8,'interest_burden':0.9,'ebit_margin':0.2,'asset_turnover':0.75,'equity_multiplier':1.0}
    evidence=[{'metric':name,'value':value,'compute_id':'c1'} for name,value in factors.items()]+[{'metric':'roe','value':0.108,'compute_id':'c1'}]
    m04={'roe':{'value':0.108,'compute_id':'c1'},'dupont_chain_product':{'value':0.108,'left_id':'c1','right_id':'c2'},**factors,'dupont_evidence_items':evidence}
    events=[event(1,0.108,'tax_burden * interest_burden * ebit_margin * asset_turnover * equity_multiplier'),event(2,0.1082,'net_profit / equity')]
    assert (await verdict('dupont_five_way_decomposition',m04,Repo(events))).ok
    m20={'structured_dossier':'研究底稿','executive_summary':'摘要','risk_factors':[{'text':'风险'+str(i),'source':'source'+str(i)} for i in range(3)],'evidence_audit_trail':[{'metric':x['metric']} for x in evidence]}
    artifacts=[{'kind':'step','name':'dupont_five_way_decomposition','content':m04}]
    result=await verdict('comprehensive_dossier_formatting',m20,Repo(artifacts=artifacts))
    assert result.ok, 'candidate M04 positive output is incompatible with its own M20 coverage'

@pytest.mark.asyncio
async def test_m20_blank_risks_are_not_three_sourced_risk_factors():
    output={'structured_dossier':'研究底稿','executive_summary':'摘要','risk_factors':[{'text':'','source':''} for _ in range(3)],'evidence_audit_trail':[{'metric':'roe'}]}
    artifacts=[{'kind':'step','name':'dupont_five_way_decomposition','content':{'dupont_evidence_items':['roe']}}]
    result=await verdict('comprehensive_dossier_formatting',output,Repo(artifacts=artifacts))
    assert not result.ok, '仅三个空对象字段不构成三条带来源风险'
