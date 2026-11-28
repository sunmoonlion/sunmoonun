"""使用正常的单回合，只在完成帧提供本次回合的最终输出。"""
import pytest
from test_instruction_runner_db import drive, stack
from test_workbench_ledger_db import db


@pytest.mark.asyncio
async def test_complete_turn_with_embedded_output_is_marked_missing(db):
    scene = await stack(db)
    original = scene.driver.connector
    captured = []

    def connector(*args, on_notification, **kwargs):
        async def frame(method, payload):
            if method == "item/completed":
                captured.append(payload["item"])
                return
            if method == "turn/completed":
                payload = {**payload, "turn": {**payload["turn"], "items": captured}}
            await on_notification(method, payload)
        return original(*args, on_notification=frame, **kwargs)

    scene.driver.connector = connector
    scene.units.ready = True
    await drive(scene)
    assert len(scene.provider_requests) == 1 and captured[0]["text"] == '{"summary": "ready"}'
    async with scene.host() as service:
        (attempt,) = await service.repo.list_attempts(scene.task)
        assert attempt["refs"]["instruction_usage"]["response_id"] == "receipt-a"
        assert attempt["refs"]["formal_result"]["detail"] == "instruction_final_missing"
        assert (await service.repo.get_task(scene.task))["state"] == "FAILED"
