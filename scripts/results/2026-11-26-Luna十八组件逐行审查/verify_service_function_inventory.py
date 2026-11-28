"""Compare two KnowBench views of a normally tested and registered service function."""
from test_formal_function_db import test_approved_host_function_freezes_with_exact_provider_receipt as register_example
from test_workbench_ledger_db import db
from test_capabilities_db import OWNER
from app.application.workbench.tool_registry import formal_registration
from app.domain.workbench.registry_views import FormalRegistration
from app.infrastructure.workbench.repository import WorkbenchRepository


async def test_inventory_and_detail_disagree_on_frozen_provider_version(db):
    await register_example(db)
    async with db() as session:
        repo = WorkbenchRepository(session)
        inventory = await repo.registry_inventory(OWNER)
        [summary] = [
            FormalRegistration.model_validate(row)
            for row in inventory["formal"] if row["source_kind"] == "service_function"
        ]
        exact = await formal_registration(repo, OWNER, summary.reference)
        assert exact.reference == summary.reference and exact.source_digest == summary.source_digest
        assert exact.source_revision == 1
        assert summary.source_revision is None
