"""检查新受理的资料能否使用运营重新绑定的数据集。"""
import json

import pytest
from test_durable_delivery_db import db
from test_knowledge_delivery_db import authorized_settings
from app.application.ports.knowledge_provider import ProviderDataset, ProviderProtocolError
from app.application.services.provider_delivery import dataset


class Index:
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id

    async def find_datasets(self, name):
        return [ProviderDataset(self.dataset_id, name)]


async def test_new_binding_conflicts_with_previous_lookup(db):
    key = "market-news"
    settings = authorized_settings()
    async with db() as session:
        old = await dataset(session, Index("dataset-1"), key, "tenant", settings)
    assert old.id == "dataset-1"
    bindings = {key: {"dataset_id": "new-id", "dataset_name": key}}
    rebound = settings.model_copy(update={"ingestion_dataset_bindings": json.dumps(bindings)})
    async with db() as session:
        with pytest.raises(ProviderProtocolError, match="conflicts with confirmed identity"):
            await dataset(session, Index("new-id"), key, "tenant", rebound)
