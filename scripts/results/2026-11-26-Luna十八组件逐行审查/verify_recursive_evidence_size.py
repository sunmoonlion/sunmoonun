import json
from test_workbench_ledger_db import db
from test_formal_recursive_evidence_db import finished
import pytest

@pytest.mark.asyncio
async def test_leaf_projection_size(db):
    _, evidence = await finished(db)
    leaves = [node for node in evidence['nodes'] if node['kind'] == 'tool']
    assert leaves == evidence['steps']
    def size(value):
        return len(json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode())
    print('leaf_count', len(leaves), 'step_bytes', size(evidence['steps']), 'total_bytes', size(evidence))
