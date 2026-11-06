import http.client
import http.server
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest

BRIDGE = Path(__file__).resolve().parents[1] / 'testing/mcp/bridge.mjs'
NODE = shutil.which('node')


class Upstream(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        self.server.requests.append((self.path, dict(self.headers), data))
        if data == b'slow':
            time.sleep(.5)
        if data == b'redirect':
            self.send_response(302); self.send_header('Location', 'http://example.invalid/'); self.end_headers(); return
        if data == b'large':
            body = b'x' * (8 * 1024 * 1024 + 1)
        else:
            body = data
        self.send_response(204 if data == b'notify204' else 202 if data == b'notify202' else 200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-Secret', 'must-not-forward')
        self.end_headers()
        try:
            self.wfile.write(b'' if data.startswith(b'notify') else body)
        except (BrokenPipeError, ConnectionResetError):
            pass


@unittest.skipUnless(NODE, 'Node.js is not installed')
class BridgeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.key = Path(self.tmp.name) / 'key.json'
        self.key.write_text('{"apiKey":"dr_sk_synthetic_test"}')
        self.key.chmod(0o600)
        self.upstream = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        self.upstream.requests = []
        self.thread = threading.Thread(target=self.upstream.serve_forever, daemon=True); self.thread.start()
        self.proc = None

    def tearDown(self):
        if self.proc:
            self.proc.terminate()
            try: self.proc.communicate(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill(); self.proc.communicate(timeout=3)
        self.upstream.shutdown(); self.upstream.server_close(); self.thread.join()
        self.tmp.cleanup()

    def start(self, **override):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0)); self.port = sock.getsockname()[1]
        env = dict(os.environ, BRIDGE_PORT=str(self.port), BRIDGE_UPSTREAM_URL=f'http://127.0.0.1:{self.upstream.server_port}/mcp/openai', MOBILERUN_LOCAL_CREDENTIAL_FILE=str(self.key), BRIDGE_TIMEOUT_MS='200')
        env.update(override)
        self.proc = subprocess.Popen([NODE, str(BRIDGE)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(100):
            if self.proc.poll() is not None: break
            try:
                if self.request('GET', '/health')[0] == 200: return True
            except OSError: time.sleep(.01)
        return False

    def request(self, method, path, body=None, headers=None):
        c = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        try:
            c.request(method, path, body, headers or {})
            r = c.getresponse(); return r.status, dict(r.getheaders()), r.read()
        finally: c.close()

    def test_routing_headers_and_raw_response(self):
        self.assertTrue(self.start())
        data = b'{"jsonrpc":"2.0","result":{"resources":[{"_meta":{"blob":"abc"}}]}}'
        status, headers, result = self.request('POST', '/mcp/openai', data, {'Authorization': 'Bearer attacker', 'x-mobilerun-cloud-api-key': 'evil', 'X-Forwarded-Host': 'evil'})
        self.assertEqual((status, result), (200, data))
        self.assertNotIn('X-Secret', headers)
        path, sent, body = self.upstream.requests[-1]
        self.assertEqual(path, '/mcp/openai'); self.assertEqual(body, data)
        sent = {k.lower(): v for k, v in sent.items()}
        self.assertEqual(sent['authorization'], 'Bearer dr_sk_synthetic_test')
        self.assertNotIn('x-mobilerun-cloud-api-key', sent); self.assertNotIn('x-forwarded-host', sent)
        self.assertEqual(self.request('POST', '/mcp/openai?route=evil', b'')[0], 404)
        self.assertEqual(self.request('GET', '/mcp/openai')[0], 405)

    def test_notifications_limits_redirect_and_timeout(self):
        self.assertTrue(self.start())
        for code in (202, 204):
            status, _, body = self.request('POST', '/mcp/openai', f'notify{code}'.encode())
            self.assertEqual((status, body), (code, b''))
        self.assertEqual(self.request('POST', '/mcp/openai', b'x' * (2 * 1024 * 1024 + 1))[0], 413)
        self.assertEqual(self.request('POST', '/mcp/openai', b'large')[0], 502)
        self.assertEqual(self.request('POST', '/mcp/openai', b'redirect')[0], 502)
        self.assertEqual(self.request('POST', '/mcp/openai', b'slow')[0], 504)

    def test_bad_credentials_fail_closed(self):
        for contents, mode, symlink in [('{"apiKey":"dr_sk_synthetic_test"}', 0o644, False), ('x' * 4097, 0o600, False), ('{"apiKey":"bad"}', 0o600, False), ('', 0o600, True)]:
            with self.subTest(mode=mode, symlink=symlink, length=len(contents)):
                self.key.unlink(missing_ok=True)
                if symlink:
                    target = Path(self.tmp.name) / 'target.json'
                    target.write_text('{"apiKey":"dr_sk_synthetic_test"}'); target.chmod(0o600)
                    self.key.symlink_to(target)
                else: self.key.write_text(contents); self.key.chmod(mode)
                self.assertFalse(self.start())
                out, err = self.proc.communicate(timeout=3)
                self.assertNotEqual(self.proc.returncode, 0)
                self.assertNotIn(b'dr_sk_synthetic_test', out + err)
                self.proc = None
        self.key.unlink(missing_ok=True)
        self.assertFalse(self.start())

    def test_rejects_non_loopback_upstream(self):
        self.assertFalse(self.start(BRIDGE_UPSTREAM_URL='http://example.com/mcp/openai'))

    def test_credential_with_trailing_newline_fails_at_startup(self):
        self.key.write_text(json.dumps({'apiKey': 'dr_sk_synthetic_test\n'}))
        self.assertFalse(self.start())
        out, err = self.proc.communicate(timeout=3)
        self.assertNotEqual(self.proc.returncode, 0)
        self.assertNotIn(b'dr_sk_synthetic_test', out + err)

    def test_chunked_request_limit(self):
        self.assertTrue(self.start())
        c = http.client.HTTPConnection('127.0.0.1', self.port, timeout=3)
        try:
            c.request('POST', '/mcp/openai', [b'x' * (1024 * 1024), b'x' * (1024 * 1024), b'x'], encode_chunked=True)
            self.assertEqual(c.getresponse().status, 413)
        finally: c.close()

    def test_connection_failure_returns_bad_gateway(self):
        self.upstream.shutdown(); self.upstream.server_close(); self.thread.join()
        self.assertTrue(self.start())
        self.assertEqual(self.request('POST', '/mcp/openai', b'{}')[0], 502)

    def test_concurrency_is_bounded(self):
        self.assertTrue(self.start(BRIDGE_TIMEOUT_MS='2000'))
        sockets = []
        try:
            for _ in range(16):
                s = socket.create_connection(('127.0.0.1', self.port), timeout=3)
                s.sendall(b'POST /mcp/openai HTTP/1.1\r\nHost: localhost\r\nContent-Length: 10\r\n\r\nx')
                sockets.append(s)
            time.sleep(.1)
            self.assertEqual(self.request('POST', '/mcp/openai', b'{}')[0], 503)
        finally:
            for s in sockets: s.close()


if __name__ == '__main__': unittest.main()
