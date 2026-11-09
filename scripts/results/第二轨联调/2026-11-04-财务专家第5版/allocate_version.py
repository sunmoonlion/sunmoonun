"""One-off, owner-requested forward allocation of financial expert version 5.

Only the version allocator is specialized. The deployed workdraft service still
checks ownership, compiles sources and checks the package before creating a NEW
draft. Existing drafts, tests, approvals and market versions are never modified.
This is an explicit maintenance operation, not a new web/API capability.
stdin: {"source_manifest": ..., "apply": false|true}
"""
import asyncio
import copy
import hashlib
import json
import sys
from datetime import UTC, datetime
from uuid import UUID

from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
from app.domain.knowbots.workdraft import canonical
from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
from app.infrastructure.storage.postgres import get_postgres

REQUEST_ID = UUID('5814331f-b555-4de9-bee6-f01e4e84e909')
SOURCE_ID = UUID('1ecbfa23-3bef-47b2-8e1a-4061f0de9a52')
SOURCE_SHA = '3941621048aece760481bf71bd620d4fec82b0bbb74737a9d3ec856339d041a9'
BODY_SHA = '428e462f87790ff0a0bf46b604a592315fc14ee3985eefb83499344c705de26d'


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class AuthorizedVersionFive(KnowbotWorkdraftService):
    async def _next(self, request):
        assert request.id == REQUEST_ID, 'wrong expert'
        default, revision = await super()._next(request)
        assert int(default) <= 5, 'version 5 is behind the current allocation'
        experts = await self.repo.list_experts([request.id])
        assert not any(e.version >= 5 for e in experts), 'version already issued'
        drafts = await self.repo.list_drafts(request_id=request.id)
        assert not any(int(d.version) >= 5 for d in drafts), 'version already reserved'
        return '5', revision


async def main(payload):
    assert sha(payload['source_manifest']) == SOURCE_SHA
    expected = copy.deepcopy(payload['source_manifest'])
    expected['version'] = expected['pack']['version'] = '5'
    pg = get_postgres()
    await pg.init()
    async with pg.session_factory() as session:
        repo = SqlKnowlabRepository(session)
        async with repo.transaction():
            await repo.lock_request(REQUEST_ID)
            request = await repo.get_request(REQUEST_ID)
            assert request is not None
            svc = AuthorizedVersionFive(repo)
            _, current = await svc.get(request.owner_subject, str(REQUEST_ID))
            assert current is not None and current.revision == 40
            assert sha(current.body) == BODY_SHA, 'workdraft changed'
            source = await repo.get_draft(SOURCE_ID)
            assert source is not None and sha(source.manifest) == SOURCE_SHA
            tests = await repo.list_tests(request_ids=[REQUEST_ID])
            assert not any(t.status in ('queued', 'running', 'waiting') for t in tests)
            prior = [d for d in await repo.list_drafts(request_id=REQUEST_ID) if d.version == '5']
            draft = None
            if prior:
                assert len(prior) == 1 and prior[0].manifest == expected
                draft = prior[0]
                assert draft.status == 'pending_test'
            else:
                preview, problems, version = await svc.preview(request.owner_subject, str(REQUEST_ID))
                assert not problems and version == '5', str(problems)
                assert preview == expected, 'changes beyond the two version fields'
                if payload.get('apply') is True:
                    draft = await svc.publish(request.owner_subject, str(REQUEST_ID))
                    assert draft.manifest == expected and draft.status == 'pending_test'
            # Fresh repository reads: the frozen source and working copy stay intact.
            saved_source = await repo.get_draft(SOURCE_ID)
            assert saved_source is not None and sha(saved_source.manifest) == SOURCE_SHA
            saved_body = await repo.get_workdraft(REQUEST_ID)
            assert saved_body is not None and sha(saved_body.body) == BODY_SHA
            if draft is not None:
                assert not any(t.draft_id == draft.id for t in tests)
        print(json.dumps({
            'receipt': {
                'checked_at': datetime.now(UTC).isoformat(),
                'request_id': str(REQUEST_ID),
                'source_draft_id': str(SOURCE_ID),
                'source_manifest_sha256': SOURCE_SHA,
                'draft_id': str(draft.id) if draft else None,
                'version': '5',
                'revision': draft.revision if draft else None,
                'manifest_sha256': sha(expected),
                'status': draft.status if draft else 'preview_only',
                'only_version_fields_changed': True,
                'source_preserved': True,
                'model_tests_started': 0,
                'authorization': 'Owner explicitly requested version 5; forward allocation only, no test or release approval.',
            },
            'manifest': expected,
        }, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main(json.load(sys.stdin)))
