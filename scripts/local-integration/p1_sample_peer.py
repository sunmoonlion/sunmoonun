"""Synthetic KnowBase sample for the P1 author integration, on a disposable test DB."""

import asyncio
import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

BASE = Path(__file__).resolve().parents[3] / "knowbase-app/knowbase-backend/app"


async def serve():
    sys.path[:0] = [str(BASE), str(BASE / "tests")]
    from test_durable_delivery_db import db
    from test_user_library_http import api, BASE as prefix
    from app.domain.user_data import Owner

    schema = db.__wrapped__()
    sessions = await anext(schema)
    client, state = api.__wrapped__(sessions)
    try:
        state["owner"] = Owner("author", "knowlab")
        row = await client.post(
            prefix + "/materials",
            params={"name": "builds.csv"},
            content=b"component,release\nsandbox-provisioner,synthetic",
        )
        row.raise_for_status()
        mid = row.json()["material"]["material_id"]
        (
            await client.post(
                f"{prefix}/materials/{mid}/uses", json={"use": "app:knowlab"}
            )
        ).raise_for_status()
        print("ready", flush=True)
        for line in sys.stdin:
            request = json.loads(line)
            assert request["headers"]["authorization"] == "Bearer local-author-sample"
            reply = await client.request(**request)
            print(json.dumps([reply.status_code, reply.text]), flush=True)
    finally:
        await client.aclose()
        await schema.aclose()


@asynccontextmanager
async def author_sample(app, sessions):
    import httpx
    from app.application.services.knowbot_library import KnowbotLibraryService
    from app.infrastructure.external.knowbase_library import KnowbaseLibrary
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.interfaces.endpoints import knowbot_routes as routes

    peer = await asyncio.create_subprocess_exec(
        str(BASE / ".venv/bin/python"),
        __file__,
        cwd=BASE,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    gate = asyncio.Lock()

    async def forward(request):
        message = {
            "method": request.method,
            "url": request.url.path,
            "headers": dict(request.headers),
            "content": request.content.decode(),
        }
        async with gate:
            peer.stdin.write((json.dumps(message) + "\n").encode())
            await peer.stdin.drain()
            status, text = json.loads(
                await asyncio.wait_for(peer.stdout.readline(), 30)
            )
        return httpx.Response(status, content=text)

    async def library():
        async with sessions() as session:
            yield KnowbotLibraryService(
                SqlKnowlabRepository(session),
                KnowbaseLibrary(
                    {"KNOWBASE_INTERNAL_URL": "https://sample.test"},
                    transport=httpx.MockTransport(forward),
                ),
            )

    async def token():
        return "local-author-sample"

    try:
        assert await asyncio.wait_for(peer.stdout.readline(), 40) == b"ready\n"
        app.dependency_overrides[routes.library_service] = library
        app.dependency_overrides[routes.get_web_knowbase_token_provider] = lambda: token
        yield
    finally:
        app.dependency_overrides.pop(routes.library_service, None)
        app.dependency_overrides.pop(routes.get_web_knowbase_token_provider, None)
        peer.stdin.close()
        await asyncio.wait_for(peer.wait(), 30)


if __name__ == "__main__":
    asyncio.run(serve())
