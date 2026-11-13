"""Pinned Codex protocol probe. Disposable, network-none Docker container only."""
import asyncio
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

captures = []
mcp_events = []
results = []
outdir = Path('/tmp/evidence')
next_model_tool = None


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(405)
        self.end_headers()

    def do_DELETE(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        raw = self.rfile.read(int(self.headers['Content-Length']))
        msg = json.loads(raw)
        if self.path == '/v1/responses':
            global next_model_tool
            captures.append(msg)
            rid = 'resp_' + str(len(captures))
            item = {'type': 'message', 'role': 'assistant', 'id': 'msg_' + rid,
                    'content': [{'type': 'output_text', 'text': 'synthetic_ok'}]}
            if next_model_tool:
                item = {'type': 'function_call', 'id': 'fc_' + rid,
                        'call_id': 'call_' + rid, 'name': next_model_tool,
                        'namespace': 'mcp__scope_probe', 'arguments': '{}', 'status': 'completed'}
                next_model_tool = None
            events = [
                {'type': 'response.created', 'response': {'id': rid}},
                {'type': 'response.output_item.done', 'item': item},
                {'type': 'response.completed', 'response': {'id': rid,
                    'usage': {'input_tokens': 1, 'output_tokens': 1, 'total_tokens': 2}}},
            ]
            data = ''.join('event: ' + e['type'] + '\ndata: ' + json.dumps(e) + '\n\n' for e in events).encode()
            ctype = 'text/event-stream'
        elif self.path == '/mcp':
            mcp_events.append({'method': msg.get('method'), 'params': msg.get('params')})
            if 'id' not in msg:
                self.send_response(202)
                self.end_headers()
                return
            method = msg['method']
            if method == 'initialize':
                value = {'protocolVersion': msg['params']['protocolVersion'],
                         'capabilities': {'tools': {}},
                         'serverInfo': {'name': 'scope-probe', 'version': '1'}}
            elif method == 'tools/list':
                value = {'tools': [{**tool(n), 'annotations': {'readOnlyHint': True, 'destructiveHint': False}}
                                   for n in ('read_a', 'read_b')]}
            elif method == 'tools/call':
                value = {'content': [{'type': 'text', 'text': 'synthetic_' + msg['params']['name']}], 'isError': False}
            else:
                value = {}
            data = json.dumps({'jsonrpc': '2.0', 'id': msg['id'], 'result': value}).encode()
            ctype = 'application/json'
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def tool(name):
    return {'name': name, 'description': 'Synthetic no-side-effect probe ' + name,
            'inputSchema': {'type': 'object', 'properties': {}, 'additionalProperties': False}}


def tool_names(body):
    def walk(items, prefix=''):
        names = []
        for item in items:
            if item.get('type') == 'namespace':
                names += walk(item.get('tools', []), item['name'] + '.')
            else:
                names.append(prefix + item.get('name', item.get('type', '?')))
        return names
    return sorted(walk(body.get('tools', [])))


async def main():
    assert Path('/.dockerenv').exists()
    assert {p.name for p in Path('/sys/class/net').iterdir()} == {'lo'}
    folder = Path('/data/codex')
    folder.mkdir(parents=True)
    cwd = Path('/tmp/step-probe')
    cwd.mkdir()
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    (folder / 'config.toml').write_text(f'''model = "test-model"
model_provider = "probe"
approval_policy = "never"
sandbox_mode = "read-only"
web_search = "disabled"
[features]
shell_tool = false
multi_agent = false
apps = false
[analytics]
enabled = false
[model_providers.probe]
name = "Offline probe"
base_url = "http://127.0.0.1:{server.server_port}/v1"
wire_api = "responses"
requires_openai_auth = false
supports_websockets = false
request_max_retries = 0
stream_max_retries = 0
[mcp_servers.scope_probe]
url = "http://127.0.0.1:{server.server_port}/mcp"
startup_timeout_sec = 5
required = true
''')
    version = await asyncio.create_subprocess_exec('/probe/codex', '--version', stdout=asyncio.subprocess.PIPE)
    version_text = (await version.communicate())[0].decode().strip()
    assert version_text == 'codex-cli 0.155.1', version_text
    proc = await asyncio.create_subprocess_exec('/probe/codex', 'app-server', '--listen', 'stdio://',
            cwd=cwd, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    pending = {}
    notices = []
    seq = 0
    stderr_lines = []

    async def consume():
        while line := await proc.stdout.readline():
            msg = json.loads(line)
            if 'method' in msg:
                notices.append(msg)
            elif msg.get('id') in pending:
                f = pending[msg['id']]
                if not f.done():
                    f.set_result(msg)

    async def err():
        while line := await proc.stderr.readline():
            stderr_lines.append(line.decode(errors='replace'))

    readers = [asyncio.create_task(consume()), asyncio.create_task(err())]

    async def call(method, params):
        nonlocal seq
        seq += 1
        number = seq
        pending[number] = asyncio.get_running_loop().create_future()
        proc.stdin.write((json.dumps({'id': number, 'method': method, 'params': params}) + '\n').encode())
        await proc.stdin.drain()
        answer = await asyncio.wait_for(pending[number], 20)
        pending.pop(number, None)
        if 'error' in answer:
            raise RuntimeError(json.dumps({'method': method, 'error': answer['error']}))
        return answer['result']

    async def start(dynamic=None, enabled=None):
        params = {'cwd': str(cwd), 'approvalPolicy': 'never', 'environments': []}
        if dynamic is not None:
            params['dynamicTools'] = [tool(n) for n in dynamic]
            params['config'] = {'mcp_servers.scope_probe.enabled': False}
        else:
            params['config'] = {'mcp_servers.scope_probe.enabled_tools': enabled}
        reply = await call('thread/start', params)
        return reply['thread']['id']

    async def turn(tid, label, extra=None, invoke=None):
        global next_model_tool
        next_model_tool = invoke
        before = len(captures)
        n_before = len(notices)
        params = {'threadId': tid, 'input': [{'type': 'text', 'text': 'MARKER_' + label}], 'environments': []}
        params.update(extra or {})
        reply = await call('turn/start', params)
        turnid = reply['turn']['id']
        for _ in range(400):
            completed = next((m for m in notices[n_before:] if m.get('method') == 'turn/completed'
                and m['params']['turn']['id'] == turnid), None)
            if completed:
                assert completed['params']['turn']['status'] == 'completed', completed
                break
            await asyncio.sleep(.05)
        else:
            raise TimeoutError(label + ': turn did not complete')
        assert len(captures) == before + (2 if invoke else 1), (label, len(captures) - before)
        body = captures[-1]
        names = tool_names(body)
        row = {'case': label, 'thread_id': tid, 'tools': names,
               'history_has_first_dynamic_marker': 'MARKER_D1_initial' in json.dumps(body.get('input')),
               'history_has_first_mcp_marker': 'MARKER_M1_read_a' in json.dumps(body.get('input'))}
        results.append(row)
        print(json.dumps(row), flush=True)
        return names

    async def resume(tid, **kwargs):
        reply = await call('thread/resume', {'threadId': tid, 'excludeTurns': True, **kwargs})
        assert reply['thread']['id'] == tid

    try:
        await call('initialize', {'clientInfo': {'name': 'step-scope-probe', 'version': '1'},
                                 'capabilities': {'experimentalApi': True}})
        proc.stdin.write(b'{"method":"initialized"}\n')
        await proc.stdin.drain()
        d = await start(dynamic=['probe_alpha'])
        await turn(d, 'D1_initial')
        await turn(d, 'D2_turn_dynamicTools_beta', {'dynamicTools': [tool('probe_beta')]})
        await call('thread/settings/update', {'threadId': d, 'dynamicTools': [tool('probe_beta')]})
        await turn(d, 'D3_settings_dynamicTools_beta')
        await resume(d, dynamicTools=[tool('probe_beta')])
        await turn(d, 'D4_live_resume_dynamicTools_beta')
        await call('thread/unsubscribe', {'threadId': d})
        await resume(d, dynamicTools=[tool('probe_beta')], config={'mcp_servers.scope_probe.enabled': False})
        await turn(d, 'D5_detach_resume_dynamicTools_beta')
        other = await start(dynamic=['probe_beta'])
        await turn(other, 'D6_new_thread_beta')
        a = await start(enabled=['read_a'])
        await turn(a, 'M1_read_a')
        control = await start(enabled=['read_a', 'read_b'])
        await turn(control, 'M2_control_both')
        await resume(a, config={'mcp_servers.scope_probe.enabled_tools': ['read_b']})
        await turn(a, 'M3_live_resume_read_b')
        await call('thread/unsubscribe', {'threadId': a})
        await resume(a, config={'mcp_servers.scope_probe.enabled_tools': ['read_b']})
        await turn(a, 'M4_detach_resume_read_b')
        calls_before = len([e for e in mcp_events if e['method'] == 'tools/call'])
        await turn(a, 'M8_allowed_model_call_b', invoke='read_b')
        calls = [e for e in mcp_events if e['method'] == 'tools/call']
        assert len(calls) == calls_before + 1 and calls[-1]['params']['name'] == 'read_b', {
            'mcp_calls': calls,
            'model_tool_results': [x for x in captures[-1].get('input', []) if x.get('type') == 'function_call_output']}
        await turn(a, 'M9_excluded_model_call_a', invoke='read_a')
        assert len([e for e in mcp_events if e['method'] == 'tools/call']) == len(calls)
        await turn(control, 'M5_control_unchanged')
        await call('thread/unsubscribe', {'threadId': a})
        await resume(a, config={'mcp_servers.scope_probe.enabled_tools': []})
        await turn(a, 'M6_detach_resume_empty')
        await call('thread/unsubscribe', {'threadId': a})
        await resume(a, config={'mcp_servers.scope_probe.enabled_tools': ['read_a']})
        await turn(a, 'M7_detach_resume_restore_a')
        by_case = {r['case']: r for r in results}
        for label in ('D1_initial', 'D2_turn_dynamicTools_beta', 'D3_settings_dynamicTools_beta',
                      'D4_live_resume_dynamicTools_beta', 'D5_detach_resume_dynamicTools_beta'):
            names = by_case[label]['tools']
            assert 'probe_alpha' in names and 'probe_beta' not in names, label
        assert 'probe_beta' in by_case['D6_new_thread_beta']['tools']
        expected = {'M1_read_a': ['read_a'], 'M2_control_both': ['read_a', 'read_b'],
                    'M3_live_resume_read_b': ['read_a'], 'M4_detach_resume_read_b': ['read_b'],
                    'M5_control_unchanged': ['read_a', 'read_b'], 'M6_detach_resume_empty': [],
                    'M7_detach_resume_restore_a': ['read_a']}
        for label, want in expected.items():
            got = [n.split('.')[-1] for n in by_case[label]['tools'] if n.startswith('mcp__scope_probe.')]
            assert got == want, (label, got, want)
        assert all(r['thread_id'] == a and r['history_has_first_mcp_marker'] for r in results
                   if r['case'] in ('M3_live_resume_read_b', 'M4_detach_resume_read_b',
                                    'M6_detach_resume_empty', 'M7_detach_resume_restore_a'))
        print('PASS: dynamic tools immutable through tested RPCs; same-thread MCP allowlist switch, history, peer isolation, allowed and denied model calls', flush=True)
    finally:
        if proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), 5)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
        for t in readers:
            t.cancel()
        server.shutdown()
        outdir.mkdir(exist_ok=True)
        (outdir / 'summary.json').write_text(json.dumps({'version': version_text,
            'results': results, 'mcp_events': mcp_events}, indent=2))
        (outdir / 'model_requests.json').write_text(json.dumps(captures, indent=2))
        (outdir / 'stderr.log').write_text(''.join(stderr_lines))


if __name__ == '__main__':
    asyncio.run(main())
