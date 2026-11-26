"""使用模板真实录制器、回放匹配器及临时样例目录。"""

import json
from pathlib import Path
import subprocess

import httpx
import pytest
from preview_recorder import Recorder


@pytest.mark.asyncio
async def test_preview_recognizes_exact_recorded_query(tmp_path):
    recorder = Recorder("search", title="搜索", description="")
    def serve(req):
        return httpx.Response(200, json={"query": req.url.params.get("q")})
    async with httpx.AsyncClient(transport=httpx.MockTransport(serve), base_url="http://sample") as http:
        await recorder.get(http, "/catalog")
        await recorder.get(http, "/catalog", q="R&D")
    directory = recorder.write(tmp_path)
    module = Path("../../tpl-web-frontend/app/preview/lib/samples.mjs").resolve().as_uri()
    code = """
        const {loadScenarios, findResponse, readBody} = await import(process.argv[1]);
        const scenario = loadScenarios(process.argv[2]).get('search');
        console.log(readBody(scenario, findResponse(scenario, 'GET', '/catalog', '?q=R%26D')).toString());
    """
    result = subprocess.check_output(["node","--input-type=module","-e",code,module,str(directory.parent)],text=True)
    assert json.loads(result)["query"] == "R&D"


def test_failed_refresh_preserves_previous_preview(tmp_path):
    recorder = Recorder("search", title="已有样例", description="")
    directory = recorder.write(tmp_path)
    prior = (directory / "manifest.json").read_bytes()
    recorder.responses.append(dict(method="GET",path="/catalog",query="",status=200,content_type="application/json",text="incomplete"))
    with pytest.raises(ValueError):
        recorder.write(tmp_path)
    assert (directory / "manifest.json").read_bytes() == prior
