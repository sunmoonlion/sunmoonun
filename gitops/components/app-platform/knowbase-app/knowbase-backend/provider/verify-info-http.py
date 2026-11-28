"""Use KnowFeed's production token + HTTPS ingest URL.

KnowFeed 已封闭旧分发链路并删除 KnowbaseAppClient / get_knowbase_app_client
（见 knowfeed-backend d1a10a5），验收改为同仓仍保留的 ServiceTokenProvider 与
knowbase_app_ingest_url，不伪造 Principal、不借操作员令牌。
"""
import asyncio,json,logging,sys
import httpx
from core.config import get_settings
from app.infrastructure.external.knowbase_app import (
    KnowbaseAppNotConfiguredError,
    ServiceTokenProvider,
)
logging.basicConfig(level=logging.CRITICAL)
x=json.load(sys.stdin)

async def ingest(http, url, token, payload):
    response=await http.post(
        url,
        json=payload,
        headers={"Authorization":"Bearer "+token,"Accept":"application/json"},
    )
    try:
        body=response.json()
    except ValueError:
        body=response.text
    return {"status_code":response.status_code,"body":body}

async def run():
    settings=get_settings()
    if not settings.knowbase_app_ingest_enabled or not settings.knowbase_app_ingest_url:
        raise KnowbaseAppNotConfiguredError(
            "Knowledge service client credentials or ingest URL are not configured"
        )
    tokens=ServiceTokenProvider(settings)
    ref={k:v for k,v in x['artifact'].items() if k not in ('bucket','key')}
    payload={
        'contract_version':1,
        'operation':'upsert',
        'distribution_id':x['distribution_id'],
        'source_app':'knowfeed-app',
        'source_document_id':x['document_id'],
        'source_document_version_id':x['version_id'],
        'artifact':ref,
        'dataset_key':'default',
        'idempotency_key':'sunmoon-provider-acceptance:'+x['version_id'],
        'correlation_id':x['correlation_id'],
        'document':{
            'title':'中文潮汐知识部署验收',
            'canonical_url':'https://knowfeed.sunmoonai.com:30443/acceptance/'+x['document_id'],
            'content_hash':ref['sha256'],
            'metadata':{},
        },
    }
    token=await tokens.get_token()
    assert token==await tokens.get_token(),'Short-lived in-memory token was not reused'
    checks={}
    url=settings.knowbase_app_ingest_url
    async with httpx.AsyncClient(timeout=settings.knowbase_app_timeout_seconds,follow_redirects=False) as http:
        for label,auth in [('missing_bearer_denied',{}),('tampered_bearer_denied',{'Authorization':'Bearer '+token[:-12]+'invalidtoken'})]:
            response=await http.post(url,json=payload,headers=auth)
            assert response.status_code==401,(label,response.status_code)
            checks[label]=True
        wrong=await http.post(url.replace('/ingestions','/retrievals'),json={},headers={'Authorization':'Bearer '+token})
        assert wrong.status_code==401,('ingest_identity_retrieve_denied',wrong.status_code)
        checks['ingest_identity_retrieve_denied']=True
        first=await ingest(http,url,token,payload)
        again=await ingest(http,url,token,payload)
        assert first['status_code']==202 and again['status_code']==202 and first['body']['id']==again['body']['id']
        checks.update({'actual_info_https_client_accepted':True,'same_http_intent_same_job':True,'short_lived_memory_token_reused':True})
        conflict=dict(payload,document=dict(payload['document'],title='conflicting intent'))
        response=await http.post(url,json=conflict,headers={'Authorization':'Bearer '+token})
        assert response.status_code==409,('conflicting_http_intent',response.status_code)
        checks['conflicting_http_intent_denied']=True
    print(json.dumps({
        'job_id':first['body']['id'],
        'http_checks':checks,
        'expected_subject':'admin/'+settings.knowbase_app_service_application,
        'expected_audience':settings.knowbase_app_service_client_id,
    }))

try:asyncio.run(run())
except Exception as error:
    print(json.dumps({'passed':False,'error_class':type(error).__name__}))
    sys.exit(1)
