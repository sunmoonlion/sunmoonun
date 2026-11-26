"""Exercise author mode changes against the real services with an in-memory repository."""
from app.application.services.knowbot_platform import KnowbotPlatformService
from app.application.services.knowbot_service import KnowbotCreationService
from tests.knowbot_fakes import OWNER, FakeRuntime, MemoryKnowlab, accepted_request, all_clear
from tests.test_knowbot_platform import Clock, _revision


async def test_next_application_remembers_author_take_back():
    repo, clock = MemoryKnowlab(), Clock()
    creation = KnowbotCreationService(repo, FakeRuntime(), now=clock)
    request = await accepted_request(creation)
    await KnowbotPlatformService(repo, now=clock).take_back(OWNER, str(request.id))
    assert (await repo.get_request(request.id)).incubation_mode == "self"
    assert await creation.default_mode(OWNER) == "self"


async def test_declined_revision_returns_to_author():
    repo = MemoryKnowlab()
    creation = KnowbotCreationService(repo, FakeRuntime(), now=Clock())
    request = await accepted_request(creation)
    await creation.revise(OWNER, str(request.id), _revision())
    rejection = all_clear(accepted=False, reason="本版缺少交付依据")
    decision = await creation.accept(str(request.id), 2, rejection, "admin-1")
    assert not decision.accepted
    [grant] = await repo.list_grants([request.id])
    state = (grant.status, (await repo.get_request(request.id)).incubation_mode)
    assert state == ("declined", "self")
