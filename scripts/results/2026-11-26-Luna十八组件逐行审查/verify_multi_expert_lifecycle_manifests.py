"""Check the three published-era snapshots created inside the existing lifecycle test."""
from app.domain.knowbots.compile import pack_problems
from app.domain.knowbots.workdraft import WorkdraftBody
from tests import test_agy_author_lifecycle_closure as example


def test_all_reuse_snapshots_pass_whole_pack_checks(monkeypatch):
    compile_original = example.compile_manifest
    rejected = {}

    def capture(body, *args, **kwargs):
        manifest, errors = compile_original(body, *args, **kwargs)
        issues = pack_problems(manifest["pack"])
        if issues:
            rejected[kwargs["pack_id"]] = [v.message for v in issues]
        doc = body.model_dump(mode="json")
        doc["planning"]["final_units"] = [doc["steps"][0]["id"]]
        corrected, issues = compile_original(WorkdraftBody.model_validate(doc), *args, **kwargs)
        assert not issues and not pack_problems(corrected["pack"])
        return manifest, errors

    monkeypatch.setattr(example, "compile_manifest", capture)
    example.test_author_method_lifecycle_and_multi_expert_immutability()
    assert not rejected, rejected
