"""One accepted author operation, through knowlab's existing application services.

Default: offline validation only. --apply: run in the matching knowlab release,
using its normal configuration. No SQL writes, model calls, tests or listing.
One outer repository transaction covers creation, freeze, binding and publish.
The source-request lock and accepted-content marker make a lost reply replayable.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from pathlib import Path
from uuid import UUID, uuid5

from app.application.services.knowbot_methods import KnowbotMethodService
from app.application.services.knowbot_service import KnowbotCreationService
from app.application.services.knowbot_workdraft import KnowbotWorkdraftService
from app.domain.knowbots.compile import compile_manifest
from app.domain.knowbots.drafts import CONSENT_VERSION, KnowbotRequestIn
from app.domain.knowbots.methods import BindMethod, FreezeMethod, freeze
from app.domain.knowbots.workdraft import WorkdraftBody, canonical

HERE = Path(__file__).resolve().parent
OWNER = "b5f49830-db2a-4d1b-b325-567e77b59d4a"
SOURCE_DRAFT = "d0a4623c-5f3b-4417-8131-7553b6409252"
SLOTS = {
    "scope": "analysis_scope",
    "inventory": "data_inventory",
    "reconcile": "reconciliation",
    "series": "quarter_series",
    "indicators": "analysis_results",
    "official": "discussion_comparison",
    "forecast": "forecast_results",
}


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def local_contracts(units):
    """Compare semantics after resolving neutral slots back to expert aliases."""
    result = json.loads(json.dumps(units))
    for unit in result:
        contract = unit["contract"]
        version = contract.pop("step_version", None)
        if version not in (None, "1"):
            raise ValueError("unexpected method version")
        slots = contract["input_slots"]
        aliases = {slot: spec["method_id"] for slot, spec in slots.items()}
        contract["input_refs"] = [aliases[slot] for slot in contract["input_refs"]]
        contract["input_slots"] = {aliases[slot]: spec for slot, spec in slots.items()}
        for check in contract["acceptance"]:
            if "source" in check:
                first, dot, rest = check["source"].partition(".")
                check["source"] = aliases.get(first, first) + dot + rest
            if "when_input_present" in check:
                check["when_input_present"] = aliases[check["when_input_present"]]
    return result


def load_bundle():
    acceptance = json.loads((HERE / "author-acceptance.json").read_text())
    raw = json.loads((HERE / "financial-workdraft-candidate.json").read_text())
    status = json.loads((HERE / "financial-candidate-status.json").read_text())
    if sha(raw) != acceptance["accepted_workdraft_sha256"]:
        raise ValueError("workdraft differs from the author's accepted content")
    if acceptance["answer"] != "接受这份装配，继续生成新准专家":
        raise ValueError("this operation requires its recorded author acceptance")
    body = WorkdraftBody.model_validate(raw)
    preview, problems = compile_manifest(
        body, {}, pack_id="financial-dynamic-candidate", version="1",
        runtime="knowbench", fallback_name=body.name,
    )
    saved = json.loads((HERE / "financial-manifest-preview.json").read_text())
    if problems or preview != saved:
        raise ValueError("release compiler differs from the accepted preview")
    # Exercise new optional-slot contracts before ever connecting to the DB.
    definitions = {}
    for step in body.steps:
        command = FreezeMethod(
            request_id=UUID(SOURCE_DRAFT), revision=1, step_id=step.id,
            input_slots={name: SLOTS[name] for name in step.uses},
        )
        definitions[step.id] = freeze(body, command)
    return body, acceptance, status, definitions


async def create(repo, runtimes, *, owner, source_draft_id, bundle):
    body, acceptance, status, definitions = bundle
    accepted_hash = acceptance["accepted_workdraft_sha256"]
    marker = f"accepted-dynamic-assembly:{accepted_hash}"
    workdrafts = KnowbotWorkdraftService(repo)
    methods = KnowbotMethodService(repo)
    creation = KnowbotCreationService(repo, runtimes)
    async with repo.transaction():
        source = await repo.get_draft(UUID(source_draft_id))
        if source is None:
            raise ValueError("source draft not found")
        await repo.lock_request(source.request_id)
        request = await repo.get_request(source.request_id)
        if request is None or request.owner_subject != owner:
            raise ValueError("source owner differs")
        if request.consent_version != CONSENT_VERSION:
            raise ValueError("source data consent requires the author's update")
        if sha(source.manifest) != status["source_manifest_sha256"]:
            raise ValueError("source draft differs from the reviewed baseline")
        # Under the source lock, one operation can create exactly one request.
        existing = [r for r in await repo.list_requests_for_owner(owner)
                    if r.idea.get("question", "").startswith(marker + "\n")]
        if len(existing) > 1:
            raise ValueError("duplicate operation marker; do not guess a request")
        if existing:
            target = existing[0]
            drafts = await repo.list_drafts(request_id=target.id)
            if len(drafts) != 1:
                raise ValueError("existing operation changed; review before continuing")
            draft = drafts[0]
        else:
            target = await creation.submit(owner, KnowbotRequestIn.model_validate({
                "title": body.name, "runtime": request.runtime, "mode": "self",
                "consent_test_data": True, "cases": request.cases,
                "idea": {"kind": "question", "question": (
                    marker + "\n作者接受由 Luna 整理的动态财务装配并授权代为录入。"
                    f"原准专家：{source.id}；确认记录：{acceptance['question_ref']}；"
                    f"作者回复：{acceptance['answer']}。独立建稿，原稿保持不变；"
                    "沿用原验收题，不发起付费测试、不交付上架。"
                )},
            }))
            current = await workdrafts.save(
                owner, str(target.id), revision=0,
                edits=[(key, value) for key, value in body.model_dump(mode="json").items()
                       if key != "data_picks"],
            )
            source_revision = current.revision
            frozen = {}
            # Freeze all from the same accepted revision before binding any.
            for step in body.steps:
                mid = uuid5(target.id, accepted_hash + ":" + step.id)
                record = await methods.publish(owner, str(mid), 1, FreezeMethod(
                    request_id=target.id, revision=source_revision, step_id=step.id,
                    input_slots={name: SLOTS[name] for name in step.uses},
                ))
                if record.definition != definitions[step.id].document():
                    raise ValueError("frozen definition differs from accepted method")
                frozen[step.id] = record
            for step in body.steps:
                selection = step.selection
                assert selection is not None
                record = frozen[step.id]
                current = await methods.bind_version(owner, str(record.method_id), 1,
                    BindMethod(
                        request_id=target.id, revision=current.revision,
                        alias=step.id, digest=record.digest,
                        inputs={SLOTS[name]: name for name in step.uses},
                        required=selection.required, max_calls=selection.max_calls,
                    ))
            preview, problems, _ = await workdrafts.preview(owner, str(target.id))
            if problems:
                raise ValueError(f"compiled author checks failed: {problems}")
            # Resolving immutable defaults must not change executable semantics.
            original = json.loads((HERE / "financial-manifest-preview.json").read_text())
            if local_contracts(preview["pack"]["method_units"]) != local_contracts(
                original["pack"]["method_units"]
            ):
                raise ValueError("binding changed accepted method contracts")
            for key in ("planning", "public_capabilities"):
                if preview["pack"][key] != original["pack"][key]:
                    raise ValueError(f"binding changed accepted {key}")
            draft = await workdrafts.publish(owner, str(target.id))
        # Replays check actual pinned records, not just operation labels.
        refs = draft.manifest["pack"]["method_sources"]
        if set(refs) != set(definitions):
            raise ValueError("new draft does not reference every accepted method")
        for alias, snapshot in refs.items():
            ref = snapshot["reference"]
            record = await methods.get(owner, ref["method_id"], ref["version"])
            if (ref["digest"] != definitions[alias].digest()
                    or record.definition != definitions[alias].document()
                    or snapshot["definition"] != record.definition):
                raise ValueError("pinned method differs from author acceptance")
        original = json.loads((HERE / "financial-manifest-preview.json").read_text())
        if local_contracts(draft.manifest["pack"]["method_units"]) != local_contracts(
            original["pack"]["method_units"]
        ) or any(draft.manifest["pack"][key] != original["pack"][key]
                 for key in ("planning", "public_capabilities")):
            raise ValueError("existing draft differs from accepted assembly")
        return {
            "status": "draft_created_not_tested", "owner_subject": owner,
            "request_id": str(target.id), "draft_id": str(draft.id),
            "version": draft.version, "revision": draft.revision,
            "manifest_sha256": sha(draft.manifest),
            "accepted_workdraft_sha256": accepted_hash,
            "source_draft_id": source_draft_id,
            "methods": {key: value["reference"] for key, value in refs.items()},
            "paid_test_started": False, "listed": False,
            "test_gate": "preserve original expectations; deploy test-run/v2 on both sides and obtain a new paid-test authorization before starting",
        }


async def main(apply):
    bundle = load_bundle()
    if not apply:
        print(json.dumps({"status": "offline_validated", "methods": len(bundle[3]),
                          "created": False}, ensure_ascii=False))
        return
    from app.infrastructure.external.knowbot_clients import RuntimeTestClients
    from app.infrastructure.repositories.knowbots import SqlKnowlabRepository
    from app.infrastructure.storage.postgres import get_postgres

    pg = get_postgres()
    await pg.init()
    try:
        async with pg.session_factory() as session:
            receipt = await create(SqlKnowlabRepository(session), RuntimeTestClients(),
                owner=OWNER, source_draft_id=SOURCE_DRAFT, bundle=bundle)
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
    finally:
        await pg.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    asyncio.run(main(args.apply))
