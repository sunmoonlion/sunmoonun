"""Run from the target knowlab app with its Python environment and PYTHONPATH=. ."""
import importlib.util
import json
import sys
from pathlib import Path

candidate = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('review_financial_fixture', candidate)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
manifest, errors = module.build_financial_expert_manifest()
result = {'compiler_errors': [str(error) for error in errors], 'lost_scope': []}
for method in module.ALL_20_SPECS:
    frozen = json.dumps(module.make_author_method_definition(method).document(), ensure_ascii=False)
    if method.get('does_not') and method['does_not'] not in frozen:
        result['lost_scope'].append(method['id'])
print(json.dumps(result, ensure_ascii=False, indent=2))
