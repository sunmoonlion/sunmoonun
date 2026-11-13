"""Export provider-owned Python DTOs and content lock to the KnowBench consumer."""

import hashlib
import json
from pathlib import Path
import sys

source = Path(__file__).with_name("script_contract.py")
target = Path(sys.argv[1]) / "app/domain/workbench/script_contract_generated.py"
target.write_bytes(
    b"# Generated from sandbox-platform/provisioner/script_contract.py; do not edit.\n"
    + source.read_bytes()
)
target.with_suffix(".lock.json").write_text(
    json.dumps(
        {
            "provider": "sandbox-platform/provisioner/script_contract.py",
            "version": 1,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        },
        indent=2,
    )
    + "\n"
)
