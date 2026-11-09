import json
import pty
import select
import time
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / 'plugins/test-plugin/scripts/local-mcp.mjs'
KEY = 'dr_sk_fixture_only'


def safe_env(home, **values):
    env = dict(os.environ)
    for name in ('MOBILERUN_CLOUD_API_KEY', 'MOBILERUN_LOCAL_CREDENTIAL_FILE', 'MOBILERUN_LOCAL_MCP_URL'):
        env.pop(name, None)
    env.update(HOME=str(home), **values)
    return env



class Upstream(BaseHTTPRequestHandler):
    received = []
    response = {}

    def do_POST(self):
        type(self).received.append((self.headers.get('Authorization'), json.loads(self.rfile.read(int(self.headers['Content-Length'])))))
        if self.headers.get('Accept') != 'application/json, text/event-stream':
            self.send_response(406); self.end_headers(); return
        body = json.dumps(type(self).response).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def test_bridge_preserves_rpc_result_and_private_metadata_and_forwards_notifications():
    http = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
    thread = threading.Thread(target=http.serve_forever, daemon=True)
    thread.start()
    try:
        Upstream.received = []
        msg = {'jsonrpc': '2.0', 'id': 7, 'result': {'tools': [{'name': 'private', '_meta': {'secret': 'metadata'}}], 'resources': [{'uri': 'file:///fixture', '_meta': {'kind': 'fixture'}}], 'structuredContent': {'x': 1}}}
        Upstream.response = msg
        with tempfile.TemporaryDirectory() as tmp:
            cred = Path(tmp) / 'cred.json'
            cred.write_text(json.dumps({'apiKey': KEY}))
            cred.chmod(0o600)
            env = safe_env(tmp, MOBILERUN_LOCAL_CREDENTIAL_FILE=str(cred), MOBILERUN_LOCAL_MCP_URL=f'http://127.0.0.1:{http.server_port}/mcp/openai')
            proc = subprocess.run(['node', str(BRIDGE), 'stdio'], input='{"jsonrpc":"2.0","id":7,"method":"initialize"}\n{"jsonrpc":"2.0","method":"notifications/initialized"}\n', text=True, capture_output=True, env=env, timeout=10)
        assert proc.returncode == 0
        assert [json.loads(x) for x in proc.stdout.splitlines()] == [msg]
        assert KEY not in proc.stdout + proc.stderr
        assert Upstream.received == [('Bearer ' + KEY, {'jsonrpc': '2.0', 'id': 7, 'method': 'initialize'}), ('Bearer ' + KEY, {'jsonrpc': '2.0', 'method': 'notifications/initialized'})]
    finally:
        http.shutdown()
        http.server_close()


def test_bridge_rejects_insecure_credential_file_without_leaking_details():
    with tempfile.TemporaryDirectory() as tmp:
        cred = Path(tmp) / 'cred.json'
        cred.write_text(json.dumps({'apiKey': KEY}))
        cred.chmod(0o644)
        proc = subprocess.run(['node', str(BRIDGE), 'stdio'], input='', text=True, capture_output=True,
                              env=safe_env(tmp, MOBILERUN_LOCAL_CREDENTIAL_FILE=str(cred)), timeout=10)
    assert proc.returncode != 0
    assert KEY not in proc.stdout + proc.stderr
    assert not proc.stdout


class LocalBridgeTests(unittest.TestCase):
    def test_missing_abort_signal_any_fails_before_credentials_or_upstream(self):
        with tempfile.TemporaryDirectory() as tmp:
            preload = Path(tmp) / 'remove-abort-signal-any.mjs'
            preload.write_text('AbortSignal.any = undefined;\n')
            env = safe_env(tmp, NODE_OPTIONS=f'--import={preload}')
            proc = subprocess.run(['node', str(BRIDGE), 'stdio'], input='', text=True,
                                  capture_output=True, env=env, timeout=10)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout, '')
        self.assertIn('Node.js 20.3 or later', proc.stderr)
        self.assertIn('AbortSignal.any', proc.stderr)
        self.assertNotIn('credential', proc.stderr.lower())

    def test_round_trip(self):
        test_bridge_preserves_rpc_result_and_private_metadata_and_forwards_notifications()

    def test_exact_config_command(self):
        config = json.loads((ROOT / 'plugins/test-plugin/mcp.json').read_text())['mcpServers']['test-plugin']
        with tempfile.TemporaryDirectory() as tmp:
            env = safe_env(tmp, MOBILERUN_CLOUD_API_KEY=KEY)
            cmd = [config['command']] + [arg.replace('${PLUGIN_ROOT}', str(BRIDGE.parents[1])) for arg in config['args']]
            proc = subprocess.run(cmd, input='', text=True, capture_output=True, env=env, timeout=10)
            self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_malformed_request_gets_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(['node', str(BRIDGE), 'stdio'], input='not json\n', text=True, capture_output=True,
                                  env=safe_env(tmp, MOBILERUN_CLOUD_API_KEY=KEY), timeout=10)
            self.assertEqual(json.loads(proc.stdout)['error']['code'], -32700)

    def test_bad_credentials_and_endpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            cred = Path(tmp) / 'cred'
            cred.write_text(json.dumps({'apiKey': KEY})); cred.chmod(0o600)
            link = Path(tmp) / 'link'; link.symlink_to(cred)
            for env in (safe_env(tmp), safe_env(tmp, MOBILERUN_LOCAL_CREDENTIAL_FILE=str(link)),
                        safe_env(tmp, MOBILERUN_CLOUD_API_KEY='dr_sk_bad key'),
                        safe_env(tmp, MOBILERUN_CLOUD_API_KEY=KEY, MOBILERUN_LOCAL_MCP_URL='https://example.com/mcp')):
                result = subprocess.run(['node', str(BRIDGE)], input='', text=True, capture_output=True, env=env, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
                self.assertEqual(result.stderr, 'Local MCP bridge unavailable. Run setup-local-auth.mjs to configure local credentials.\n')

    def test_bad_upstream_and_redirect(self):
        class Handler(BaseHTTPRequestHandler):
            target_count = 0
            mode = 'wrong_id'
            def do_POST(self):
                self.rfile.read(int(self.headers['Content-Length']))
                if self.path == '/target':
                    type(self).target_count += 1
                if type(self).mode == 'redirect':
                    self.send_response(307); self.send_header('Location', '/target'); self.end_headers(); return
                bodies = {'wrong_id': b'{"jsonrpc":"2.0","id":99,"result":{}}',
                          'missing_result': b'{"jsonrpc":"2.0","id":1}', 'invalid': b'not json'}
                body = bodies[type(self).mode]
                self.send_response(200); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body)
            def log_message(self, *_): pass
        http = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=http.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                env = safe_env(tmp, MOBILERUN_CLOUD_API_KEY=KEY, MOBILERUN_LOCAL_MCP_URL=f'http://127.0.0.1:{http.server_port}/mcp')
                for mode in ('wrong_id', 'missing_result', 'invalid', 'redirect'):
                    Handler.mode = mode
                    result = subprocess.run(['node', str(BRIDGE)], input='{"jsonrpc":"2.0","id":1,"method":"tools/list"}\n', text=True, capture_output=True, env=env, timeout=10)
                    response = json.loads(result.stdout)
                    self.assertEqual(response['id'], 1); self.assertEqual(response['error']['code'], -32000)
                self.assertEqual(Handler.target_count, 0)
        finally:
            http.shutdown(); http.server_close()

    def test_setup_hidden_tty_and_existing_file_and_symlink_parent(self):
        helper = BRIDGE.parent / 'setup-local-auth.mjs'
        def run(home):
            pid, master = pty.fork()
            if pid == 0:
                os.execvpe('node', ['node', str(helper)], safe_env(home))
            output = b''
            try:
                deadline = time.monotonic() + 8
                while b'input hidden' not in output and time.monotonic() < deadline:
                    if select.select([master], [], [], 0.2)[0]: output += os.read(master, 4096)
                self.assertIn(b'input hidden', output)
                os.write(master, KEY.encode() + b'\r')
                while time.monotonic() < deadline:
                    ready, _, _ = select.select([master], [], [], 0.2)
                    if ready:
                        try: output += os.read(master, 4096)
                        except OSError: break
                _, status = os.waitpid(pid, 0)
                self.assertNotIn(KEY.encode(), output)
                return os.waitstatus_to_exitcode(status)
            finally: os.close(master)
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run(tmp), 0)
            cred = Path(tmp) / '.config/mobilerun/local-mcp.json'
            self.assertEqual(cred.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(cred.read_text()), {'apiKey': KEY})
            self.assertNotEqual(run(tmp), 0)
            self.assertEqual(json.loads(cred.read_text()), {'apiKey': KEY})
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as target:
            (Path(tmp) / '.config').symlink_to(target)
            self.assertNotEqual(run(tmp), 0)
            self.assertFalse((Path(target) / 'mobilerun').exists())

    def test_oversize_line_then_valid_malformed_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(['node', str(BRIDGE)], input='x' * (1024 * 1024 + 1) + '\nnot json\n',
                                    text=True, capture_output=True, env=safe_env(tmp, MOBILERUN_CLOUD_API_KEY=KEY), timeout=10)
            self.assertEqual([json.loads(x)['error']['code'] for x in result.stdout.splitlines()], [-32600, -32700])

    def test_credential_permissions(self):
        test_bridge_rejects_insecure_credential_file_without_leaking_details()
