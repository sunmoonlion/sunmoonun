"""以 KnowBase 的隔离 PostgreSQL 和已登记函数 HTTP 测试夹具运行。"""
from test_registered_data_functions import db, world
from app.application.services.data_functions import MAX_TEXT_CHARS

async def test_original_continuation(world):
    material, _ = await world.lib.upload("alice","附注.txt",("甲"*MAX_TEXT_CHARS+"乙").encode())
    await world.lib.show("alice",material.id,"app:knowbench")
    session = await world.runs.register_session("alice","knowbench")
    read = dict(name="read_input",session=session.id,material_id=material.id,what="original")
    first = await world.facts(**read)
    second = await world.facts(**read,offset=MAX_TEXT_CHARS)
    assert first["more"] and first["text"] == "甲"*MAX_TEXT_CHARS
    assert second == first

async def test_reference_also_shown_to_bench(world):
    material, version = await world.publish()
    await world.lib.add_public_references("knowfeed",material.id,version.version_no,[("alice","资料委托")])
    session = await world.runs.register_session("alice","knowbench")
    async def rows():
        result = await world.facts(name="list_library",session=session.id)
        return [row["material_id"] for row in result["materials"]]
    assert await rows() == [material.id]
    await world.lib.show("alice",material.id,"app:knowbench")
    assert await rows() == [material.id,material.id]

async def test_published_scope_schema_and_live_route(world):
    from jsonschema import Draft202012Validator
    from app.application.services.data_query_revisions import function_revision
    args = {"scope":"run"}
    contract = function_revision("list_inputs")["contract"]
    Draft202012Validator(contract["input_schema"]).validate(args)
    result = await world.facts(name="list_inputs",**args)
    assert result == {"error":"Invalid query scope or arguments"}
