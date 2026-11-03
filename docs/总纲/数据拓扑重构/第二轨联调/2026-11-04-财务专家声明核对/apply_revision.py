"""Save/freeze the authorized revision through deployed services; no release or tests.

stdin contains before/revision. Exact base guards prevent replacing concurrent work.
"""
import asyncio
import hashlib
import json
import sys
from datetime import UTC, datetime
from uuid import UUID

from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
from app.domain.knowbots.workdraft import canonical
from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
from app.infrastructure.storage.postgres import get_postgres


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


async def main(payload):
    before, revision = payload['before'], payload['revision']
    rid=UUID(before['request_id']); owner=before['owner_subject']
    expected=sha(revision['body'])
    pg=get_postgres(); await pg.init()
    async with pg.session_factory() as session:
        repo=SqlKnowlabRepository(session); svc=KnowbotWorkdraftService(repo)
        async with repo.transaction():
            await repo.lock_request(rid)
            request,current=await svc.get(owner,str(rid))
            assert request.owner_subject==owner and current is not None
            tests=await repo.list_tests(request_ids=[rid])
            assert not any(t.status in ('queued','running','waiting') for t in tests),'active test'
            if sha(current.body)!=expected:
                assert current.revision==revision['base_revision'],'workdraft revision changed'
                assert sha(current.body)==revision['base_body_sha256'],'workdraft content changed'
                current=await svc.save(owner,str(rid),revision=current.revision,edits=[tuple(x) for x in revision['edits']])
                assert sha(current.body)==expected
            previous=[d for d in await repo.list_drafts(request_id=rid) if str(d.version)=='4' and d.manifest.get('pack',{}).get('scope')==revision['body']['scope']]
            if previous:
                assert len(previous)==1
                draft=previous[0]
            else:
                preview,problems,version=await svc.preview(owner,str(rid))
                assert not problems,str(problems)
                assert version=='4','expert version changed'
                draft=await svc.publish(owner,str(rid));assert draft.manifest==preview
            assert draft.status=='pending_test'
            assert not any(t.draft_id==draft.id for t in tests)
        print(json.dumps({'receipt':{'checked_at':datetime.now(UTC).isoformat(),'request_id':str(rid),'draft_id':str(draft.id),'version':draft.version,'revision':draft.revision,'workdraft_revision':current.revision,'body_sha256':expected,'manifest_sha256':sha(draft.manifest),'status':draft.status,'listed':False,'model_tests_started':0,'authorization':'Owner asked to implement declaration, matching, scope review and answer coverage after reviewing proposal.'},'manifest':draft.manifest},ensure_ascii=False))


if __name__=='__main__':
    asyncio.run(main(json.load(sys.stdin)))
