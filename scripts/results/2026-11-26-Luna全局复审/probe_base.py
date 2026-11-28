"""Check the material-read boundary using an owner's genuine grants in a test database."""

from datetime import timedelta
from uuid import uuid4

import pytest
from test_registered_data_functions import db as db, world as world

from app.domain.method_reads import MethodParentRequest
from app.domain.user_data import UserDataError


@pytest.mark.asyncio
@pytest.mark.parametrize("length", [16000, 16001])
async def test_text_boundary_after_authorized_preparation(world, length):
    material, version = await world.lib.upload("alice", "report.txt", b"x" * length)
    await world.lib.show("alice", material.id, "app:knowbench")
    request = MethodParentRequest.model_validate(
        {
            "read": {
                "task_id": str(uuid4()),
                "material_id": material.id,
                "version_no": 1,
                "purpose": "Read the report",
                "path": [
                    {
                        "call_id": str(uuid4()),
                        "method_id": str(uuid4()),
                        "definition_digest": "sha256:" + "a" * 64,
                    }
                ],
            },
            "expires_at": world.runs.now() + timedelta(minutes=5),
            "sha256": version.sha256,
        }
    )
    parent = await world.runs.method_parent_grant("alice", "knowbench", request)
    await world.runs.consent_method_read("alice", "knowbench", parent.id, request)
    if length == 16000:
        _, grant_id = await world.runs.read_for_method("alice", request.read)
        assert grant_id == parent.id
    else:
        with pytest.raises(UserDataError) as error:
            await world.runs.read_for_method("alice", request.read)
        assert error.value.code == "method_read_format"
