"""Run under knowbench's uv environment. Synthetic evidence, no model/data charge."""
import asyncio
import copy
import json
from decimal import Decimal
from pathlib import Path

from app.application.workbench.acceptance import judge
from app.application.workbench.acceptance_numbers import judge_numbers
from app.domain.workbench.packs import AcceptanceRule
from app.domain.workbench.compute import evaluate

HERE = Path(__file__).resolve().parent


class Evidence:
    def __init__(self):
        self.events = []
        self.inventory = {}
        self.pages = {('synthetic-current', 3): '2024年初现金及现金等价物余额100元',
                      ('synthetic-prior', 3): '2023年末现金及现金等价物余额100元'}

    def compute(self, expression, values):
        value = evaluate(expression, {k: Decimal(str(v)) for k, v in values.items()})
        cursor = len(self.events) + 1
        self.events.append({'cursor': cursor, 'payload': {'value': str(value),
            'expression': expression, 'inputs': [{'name': k, 'value': str(v), 'ref': f'fact:synthetic_{k}'} for k, v in values.items()]}})
        return dict(values, value=float(value), compute_id=f'c{cursor}')

    async def list_task_events(self, task_id, **kwargs):
        return self.events

    async def list_artifacts_with_content(self, task_id):
        return [{'kind': 'step', 'name': 'inventory', 'content': self.inventory}]

    async def quotes(self, repo, task, quotes):
        return [{'found': q['text'] in self.pages.get((q['material_id'], q['page']), '')} for q in quotes]


async def main():
    manifest = json.loads((HERE / 'draft-manifest.json').read_text())
    workflow = {s['step_id']: s for s in manifest['pack']['workflow']}
    rules = [AcceptanceRule.model_validate(r) for r in workflow['reconcile']['acceptance']]
    e = Evidence()
    out = {'checks': ['Synthetic fixture only'], 'restatement_differences': []}
    for name, expression, values in [
        ('balance', 'A-(L+E)', {'A': 300, 'L': 100, 'E': 200}),
        ('profit', 'NP-(P+M)', {'NP': 50, 'P': 40, 'M': 10}),
        ('cash', 'END-(BEGIN+CHANGE)', {'END': 120, 'BEGIN': 100, 'CHANGE': 20}),
        ('continuity', 'OPEN-PREV_CLOSE', {'OPEN': 100, 'PREV_CLOSE': 100}),
    ]:
        out[name + '_checks'] = [dict(e.compute(expression, values), key=name)]
        out[name + '_missing'] = []
        e.inventory[name + '_plan'] = [{'key': name}]
    meta = {'account': '现金及现金等价物', 'balance_date': '2023-12-31', 'scope': '合并',
            'opening_report': 'synthetic-current@1', 'previous_report': 'synthetic-prior@1',
            'account_kind': 'stock_balance', 'comparison_kind': 'opening_to_previous_closing'}
    out['continuity_checks'][0].update(meta, quotes=[{'material_id': mid, 'page': page, 'text': text} for (mid, page), text in e.pages.items()])
    e.inventory['continuity_plan'][0].update(meta)
    results = {}

    async def check(name, output, expected):
        verdict = await judge_numbers(judge(json.dumps(output, ensure_ascii=False), rules), rules, repo=e, task={'id': 'synthetic-only'}, reader=e)
        assert verdict.ok == expected, (name, verdict.failures)
        results[name] = {'passed': True, 'expected_acceptance': expected}

    await check('original_four_formulas_with_stock_continuity', out, True)
    bad = copy.deepcopy(out); bad['continuity_checks'][0]['account_kind'] = 'period_flow'
    await check('reject_flow_account_kind', bad, False)
    bad = copy.deepcopy(out); bad['continuity_checks'][0]['comparison_kind'] = 'same_period_restatement'
    await check('reject_restatement_as_fourth_identity', bad, False)
    bad = copy.deepcopy(out); bad['continuity_checks'][0]['value'] = 1
    await check('reject_forged_calculated_difference', bad, False)
    bad = copy.deepcopy(out); bad['continuity_checks'][0]['quotes'] = []
    await check('reject_missing_balance_quotes', bad, False)
    bad = copy.deepcopy(out); bad['continuity_checks'][0]['quotes'][0]['text'] = 'fabricated'
    await check('reject_unverifiable_quote', bad, False)
    bad = copy.deepcopy(out); bad['continuity_checks'] *= 2
    await check('reject_duplicate_balance_pair', bad, False)
    archived = json.loads((HERE/'previous-continuity.json').read_text())
    bad = copy.deepcopy(out); bad['continuity_checks'] = archived['continuity_checks']; bad['continuity_missing'] = archived['continuity_missing']
    e.inventory['continuity_plan'] = archived['inventory_continuity_plan']
    await check('reject_archived_c1_flow_restatement_rows', bad, False)
    original = json.loads((HERE / 'before.json').read_text())['body']
    revised = json.loads((HERE / 'revision.json').read_text())['body']
    for sid in ('scope', 'indicators', 'official'):
        assert next(s for s in original['steps'] if s['id']==sid) == next(s for s in revised['steps'] if s['id']==sid)
    print(json.dumps({'synthetic': True, 'model_calls': 0, 'checks': results,
        'unchanged_steps': ['scope','indicators','official'],
        'limitation': 'Metadata and quotes do not independently prove correct financial semantics when a model mislabels inputs. No live acceptance claim.'}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
