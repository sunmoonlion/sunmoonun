"""普通作者能保存的第一条事实超过工作台给模型的摘要上限。"""
from app.domain.workbench.memory import NOTE_LIMIT, memory_note


def test_legal_single_fact_exceeds_note_limit():
    fact = "甲" * 400
    note = memory_note([{"text": fact, "enabled": True}])
    assert note.splitlines()[1] == "- " + fact
    assert len(note.splitlines()[1]) > NOTE_LIMIT
