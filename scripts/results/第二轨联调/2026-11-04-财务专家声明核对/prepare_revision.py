"""Prepare an author-authorized scope/answerability revision, without model calls."""
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / '2026-11-03-固定专家余额衔接修订'


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def table(name, fields):
    return {'name': name, 'type': 'table', 'items': [{'name': x, 'type': 'text'} for x in fields]}


def check(template, **params):
    return {'template': template, 'params': params}


def prepare():
    previous = json.loads((BASE/'revision.json').read_text())['body']
    identity = json.loads((BASE/'before.json').read_text())
    before = {**identity, 'revision': 38, 'body': previous}
    body = copy.deepcopy(previous)
    declaration = json.loads((HERE/'declaration-review.json').read_text())['proposed']
    body['scope'] = declaration['scope']
    # Pending revision must not claim it has already received a new release exception.
    body['tagline'] = '单家公司财报指标计算、披露核对与固定方法季度预测'
    steps = {x['id']: x for x in body['steps']}
    scope = steps['scope']
    scope['why'] = '核对问题所需结果和方法是否在本专家范围内，避免答非所问'
    scope['does'] = '逐项列出本题要交付的结果、指定方法与口径；超出范围或不明确时先交用户决定，不擅自改题'
    scope['rules'] = [
        {'id':'scope_requirements','text':'保留原问题。将用户要求的每项结果、主体、期间、明确指定的方法列为request_items，每项给稳定id、原题原文question_quote、requested_result、requested_method（未指定写未指定）、scope_reason。不得因只有一位免费专家、曾经被AI请回、或可读到相关数据就视为适用。不得删除明确要求或把DCF换成营收预测、把原因识别换成几个比率。相同话题不代表相同方法。'},
        {'id':'scope_decision','text':'逐项按本专家公开scope/does与scope/does_not判断。必要要求超范围或口径不明确时，使用运行器的out_of_scope回复，在用户明确接受具体缩小后的问题前不继续；没有可行子问题就说明停止并建议其他专家、通用模型或提交创意。无回答、取消、过期都不视为接受。用户明确接受范围调整时，request_items只列本次明确接受的交付要求，excluded_requests逐条保留未承接的原要求和授权说明；否则不得删减原要求。仅当本次每项都在方法范围内才将status写covered；不以假设伪造覆盖。'},
        {'id':'scope_data','text':'in_data只描述本次已授权数据的实际情况。能力适用性与数据是否已经齐备分开判断：方法适用但缺数据时按既有request_data及本人确认流程处理，不能把空授权清单说成公司不存在。同科目有合并/母公司等口径冲突时问用户，不能自行补定口径。未取齐不承诺已能算出。'},
    ]
    scope['outputs'] += [table('request_items', ['id','question_quote','requested_result','requested_method','scope_reason','status']), {'name':'excluded_requests','type':'list','items':None}]
    scope['checks'] += [
        check('list_min',path='request_items',min=1),
        check('each_has',path='request_items',keys=['id','question_quote','requested_result','requested_method','scope_reason','status'],non_empty_keys=['id','question_quote','requested_result','requested_method','scope_reason'],unique_by=['id']),
        check('all_equal',path='request_items',field='status',equals='covered'),
    ]
    report=steps['writeup']
    report['outputs'] += [table('request_results',['request_id','status','answer','basis']), {'name':'unanswered_requests','type':'list','items':None}]
    report['rules'].append({'id':'answer_original_request','text':'先逐项回答scope.request_items，request_results中每个request_id恰好对应一项，不能漏、重、增或改id。answer写该要求的直接答案，basis写实际已验收的上游交回项及原有数据/计算证据；status只有completed或unanswered。没有所要求结果、用了不同方法/期间/主体、只有相关数据或一句缺数说明，都不是completed：写unanswered并在unanswered_requests列明原因。report正文必须包含这些逐项答案与未完成说明，明确列出scope.excluded_requests和用户已接受的范围，不宣称解决被排除的原要求。允许如实交回有缺口的稿，但验收不能把它记作完整完成；不能为了过验收编数、空填答案、把缺口换成已完成。'})
    report['checks'] += [
        check('non_empty',path='report'),
        check('list_min',path='request_results',min=1),
        check('each_has',path='request_results',keys=['request_id','status','answer','basis'],non_empty_keys=['request_id','answer','basis'],unique_by=['request_id']),
        check('each_has',path='request_results',field='status',values=['completed','unanswered']),
        check('covers',path='request_results',field='request_id',source_step='scope',source_path='request_items',source_field='id'),
        check('all_equal',path='request_results',field='status',equals='completed'),
        check('list_empty',path='unanswered_requests'),
    ]
    # Financial formulas and evidence checks are not changed by this revision.
    for old in previous['steps']:
        if old['id'] not in ('scope','writeup'): assert old==steps[old['id']]
    edits=[['scope',body['scope']],['tagline',body['tagline']],['steps/scope',scope],['steps/writeup',report]]
    return before, {'base_revision':38,'base_body_sha256':sha(previous),'body':body,'edits':edits,'verification_limit':'Structural checks detect missing or explicitly unanswered requirements; they do not prove semantic completeness of model-created requirements or answers.'}


if __name__=='__main__':
    before, revision=prepare()
    for name,value in [('before',before),('revision',revision)]:
        (HERE/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'base_revision':revision['base_revision'],'edits':len(revision['edits']),'body_sha256':sha(revision['body'])}))
