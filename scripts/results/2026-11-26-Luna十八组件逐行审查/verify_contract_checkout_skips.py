"""Inspect contract-gate outcomes when a checked-out app loses one contract file."""
import json

import pytest
from tests import test_knowbot_contract_locks as locks


@pytest.mark.parametrize("missing", ["lock", "schema"])
def test_checked_out_repos_cannot_skip_a_missing_contract(tmp_path, monkeypatch, missing):
    parent = tmp_path / "knowlab-app"
    provider = tmp_path / "knowmart-app"
    for repo in (parent, provider):
        (repo / "contracts").mkdir(parents=True)
        (repo / ".git").mkdir()
    lock = parent / "contracts" / locks.LOCK_V2.name
    if missing == "schema":
        lock.write_text(json.dumps({
            "provider": "knowmart-app", "major_version": 2, "schema": "contracts/missing.json",
        }))
    monkeypatch.setattr(locks, "PARENT", parent)
    monkeypatch.setattr(locks, "LOCK_V2", lock)
    with pytest.raises((FileNotFoundError, AssertionError)):
        try:
            locks.test_v2_locks_match_their_providers()
        except pytest.skip.Exception as exc:
            pytest.fail(f"Checked-out {missing} was treated as an absent checkout: {exc}")
