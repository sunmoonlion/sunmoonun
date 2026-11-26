"""Run the maintained bootstrap scripts against temporary files and stub commands."""
from pathlib import Path
import shutil
import subprocess

import pytest

BACKEND = Path(__file__).resolve().parents[4] / "knowlab-app/knowlab-backend"


def sandbox(tmp_path, folder, config, script, action):
    root = tmp_path / folder
    (root / "config").mkdir(parents=True)
    shutil.copyfile(BACKEND / folder / script, root / script)
    (root / "config/common.env").write_text(config)
    return subprocess.run(["bash", str(root / script), action], capture_output=True)


def test_postgres_only_validation(tmp_path):
    result = sandbox(tmp_path, "db-access-bootstrap",
        "ENABLE_POSTGRESQL=true\nDBCTL_BIN=/bin/true\nPG_K8S_CONFIG=dummy\n",
        "db-access-bootstrap.sh", "validate")
    assert result.returncode == 0


def test_clear_redis_user(tmp_path):
    (tmp_path / "app").mkdir()
    target = tmp_path / "app/.env"
    target.write_text("REDIS_USER=prior_account\n")
    incoming = tmp_path / "incoming"
    incoming.write_text("REDIS_USER=\n")
    result = sandbox(tmp_path, "db-access-bootstrap", f'OUT_ENV="{incoming}"\n',
        "merge-and-generate-app-env.sh", "merge-only")
    assert result.returncode == 0
    assert "prior_account" not in target.read_text()


def test_disabled_search_can_still_revoke(tmp_path):
    declaration = tmp_path / "declaration"
    declaration.touch()
    result = sandbox(tmp_path, "search-access-bootstrap",
        f'ENABLE_SEARCH_ACCESS=false\nELASTICSEARCH_DECLARATION="{declaration}"\n'
        "ELASTICSEARCH_PROVISIONER_BIN=/bin/true\nELASTICSEARCH_CLUSTER=local\n",
        "search-access-bootstrap.sh", "revoke")
    assert result.returncode == 0
