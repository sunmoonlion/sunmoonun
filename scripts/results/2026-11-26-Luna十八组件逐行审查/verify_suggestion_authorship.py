"""把实际建议原文交给同一个 decide 服务，检查存下的来源。"""
from pathlib import Path
from tempfile import NamedTemporaryFile
import subprocess

app = Path('knowlab-app/knowlab-backend/app').resolve()
source = (app / 'tests/test_knowbot_incubation_service.py').read_text()
fixture = source.split('@pytest.mark.asyncio')[0]
case = """
@pytest.mark.asyncio
async def test_unchanged_suggestion_attribution(w):
    request, done = await _first_round(w)
    assert not done.review['s3']['verified']
    value = next(s['value'] for s in FIRST['suggestions'] if s['id'] == 's3')
    stored, _ = await w.inc.decide(OWNER, str(request.id), str(done.id), 's3',
        action='accept_edited', revision=0, value=value)
    source = stored.sources['tagline']
    entry = w.repo.entries[uuid.UUID(source['ref'].removeprefix('record:'))]
    assert (stored.body['tagline'], source['kind'], entry.suggestion_ref) == (value, 'user_text', None)
"""
with NamedTemporaryFile(dir=app/'tests', prefix='test_review_', suffix='.py', mode='w') as f:
    f.write(fixture + case)
    f.flush()
    subprocess.run([app/'.venv/bin/python', '-m', 'pytest', '-q', f.name], cwd=app, check=True)
