import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { once } from 'node:events'
import { createPreviewServer } from '../../../../tpl-app/tpl-web-frontend/app/preview/server.mjs'

const root = await mkdtemp(join(tmpdir(), 'luna-preview-'))
const server = createPreviewServer({ config: { app: 'tpl' }, fixturesRoot: root })
try {
  const dir = join(root, 'default')
  await mkdir(dir)
  await writeFile(join(dir, 'manifest.json'), JSON.stringify({
    id: 'default',
    responses: [
      { path: '/api/present', body: { value: 1 } },
      { path: '/api/null', body: null },
      { path: '/api/missing-file', file: 'sample-not-yet-recorded.json' },
    ],
  }))
  server.listen(0, '127.0.0.1')
  await once(server, 'listening')
  const base = 'http://127.0.0.1:' + server.address().port
  assert.deepEqual(await (await fetch(base + '/api/present')).json(), { value: 1 })
  for (const path of ['/api/null', '/api/missing-file']) {
    const response = await fetch(base + path)
    assert.equal(response.status, 200)
    assert.equal(await response.text(), '')
  }
} finally {
  server.close()
  await rm(root, { recursive: true, force: true })
}
