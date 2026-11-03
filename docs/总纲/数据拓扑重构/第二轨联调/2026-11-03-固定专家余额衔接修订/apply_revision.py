"""Authorized repair via deployed application services; no SQL writes or model runs.

stdin: {before, revision}. Run as a one-off owner-delegated operation in the
already deployed knowlab environment. Output is the immutable draft receipt.
"""
import asyncio
import hashlib
import json
import sys
from uuid import UUID
from datetime import datetime, UTC

from app.infrastructure.storage.postgres import get_postgres
from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
from app.domain.knowbots.workdraft import canonical


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


async def main(payload):
    before, revision = payload['before'], payload['revision']
    rid = UUID(before['request_id'])
    owner = before['owner_subject']
    expected = sha(revision['body'])
    pg = get_postgres()
    await pg.init()
    async with pg.session_factory() as session:
        repo = SqlKnowlabRepository(session)
        svc = KnowbotWorkdraftService(repo)
        async with repo.transaction():
            await repo.lock_request(rid)
            request, current = await svc.get(owner, str(rid))
            assert request.owner_subject == owner and current is not None
            tests = await repo.list_tests(request_ids=[rid])
            assert not any(t.status in ('queued', 'running', 'waiting') for t in tests), 'active test'
            assert any(str(t.id)=='c55e8af8-99ac-49d2-b06f-0514bc3766a1' and t.status=='passed' for t in tests), 'baseline changed'
            if sha(current.body) != expected:
                assert current.revision == revision['base_revision'], 'workdraft revision changed'
                assert sha(current.body) == revision['base_body_sha256'], 'workdraft content changed'
                current = await svc.save(owner, str(rid), revision=current.revision, edits=[tuple(x) for x in revision['edits']])
                assert sha(current.body) == expected
            existing = [d for d in await repo.list_drafts(request_id=rid) if int(d.version)==3 and d.manifest.get('tagline')==revision['body']['tagline']]
            if existing:
                assert len(existing)==1
                draft=existing[0]
            else:
                preview, problems, version = await svc.preview(owner, str(rid))
                assert not problems, str(problems)
                assert version=='3', 'expert version changed'
                draft=await svc.publish(owner, str(rid))
                assert draft.manifest==preview
            assert draft.status=='pending_test'
            assert not any(t.draft_id==draft.id for t in tests)
        print(json.dumps({'checked_at':datetime.now(UTC).isoformat(), 'owner_subject':owner,
            'request_id':str(rid),'workdraft_revision':current.revision,'body_sha256':expected,
            'draft_id':str(draft.id),'version':draft.version,'revision':draft.revision,
            'manifest_sha256':sha(draft.manifest),'status':draft.status,
            'model_tests_started':0,'listed':False,
            'authorization':'Owner: 修后上架; 增加人工特批发布，修复后按特批上架',
            'next':'Deploy audited exception API, request and approve exact digest, then normal delivery.'},ensure_ascii=False,indent=2))


if __name__=='__main__':
    asyncio.run(main(json.load(sys.stdin)))
