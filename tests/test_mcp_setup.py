import http.server
import json
import signal
import threading
import unittest
from unittest import mock

from testing.mcp import setup


class SetupTests(unittest.TestCase):
    def test_rejects_unsafe_urls(self):
        for url in (
            "http://example.com/mcp/openai",
            "https://user:pass@example.com/mcp/openai",
            "https://example.com/mcp/openai?token=x",
            "https://example.com/other",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                setup.validate_mcp_url(url)

    def test_allows_only_https_public_or_loopback_http(self):
        self.assertEqual(setup.validate_mcp_url("https://host.example/mcp/openai"), "https://host.example/mcp/openai")
        self.assertEqual(setup.validate_mcp_url("http://127.0.0.1:8081/mcp/openai"), "http://127.0.0.1:8081/mcp/openai")
        with self.assertRaises(ValueError):
            setup.validate_mcp_url("http://192.168.1.2/mcp/openai")

    def test_upstream_must_be_loopback_http_and_valid_port(self):
        for url in ("https://127.0.0.1/mcp/openai", "http://example.test/mcp/openai", "http://127.0.0.1:bad/mcp/openai", " http://127.0.0.1/mcp/openai", "http://127.0.0.1/mcp/openai\n"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                setup.validate_upstream_url(url)
        with self.assertRaises(ValueError):
            setup.validate_upstream_url("http://127.0.0.2/mcp/openai")
        for port in (0, 65536, -1):
            with self.subTest(port=port), self.assertRaises(ValueError):
                setup.validate_port(port)

    def test_upstream_preflight_uses_health_not_authenticated_mcp_route(self):
        paths = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                paths.append(self.path)
                self.send_response(200 if self.path == "/health" else 401)
                self.end_headers()

            def do_POST(self):
                paths.append(self.path)
                self.send_response(401)
                self.end_headers()

            def log_message(self, *_args):
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            setup.check_upstream(f"http://127.0.0.1:{server.server_port}/mcp/openai")
        finally:
            server.shutdown()
            thread.join()
            server.server_close()
        self.assertEqual(paths, ["/health"])

    def test_cli_errors_do_not_echo_exception_or_url(self):
        with mock.patch.object(setup, "check_url", side_effect=ValueError("https://user:secret@example.test/mcp/openai")), mock.patch("builtins.print") as output:
            self.assertEqual(setup.main(["check", "--url", "https://example.test/mcp/openai"]), 1)
        self.assertNotIn("secret", str(output.call_args_list))

    def test_start_requires_opt_in_without_spawning_any_child(self):
        with mock.patch.object(setup.subprocess, "Popen") as popen, self.assertRaisesRegex(ValueError, "requires"):
            setup.start(allow_public_account_access=False)
        popen.assert_not_called()

    def test_start_failure_cleans_only_its_started_child_and_restores_handlers(self):
        events = []

        class Child:
            stdout = None

            def poll(self):
                return None

            def terminate(self):
                events.append("terminate-managed-child")

            def wait(self, timeout=None):
                return 0

        managed = Child()
        def signal_handler(sig, handler):
            events.append(("signal", sig, handler))
            return f"previous-{sig}"

        def spawn(*_args, **_kwargs):
            if not any(event == "spawn" for event in events):
                events.append("spawn")
                return managed
            raise OSError("synthetic tunnel startup failure")

        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *_args): pass

        with mock.patch.object(setup.shutil, "which", side_effect=lambda name: name), \
             mock.patch.object(setup, "check_upstream"), \
             mock.patch.object(setup, "_port_available", return_value=True), \
             mock.patch.object(setup.Path, "is_file", return_value=True), \
             mock.patch.object(setup.signal, "signal", side_effect=signal_handler), \
             mock.patch.object(setup.subprocess, "Popen", side_effect=spawn), \
             mock.patch.object(setup, "check_url", return_value=True), \
             mock.patch.object(setup, "urlopen", return_value=Response()):
            with self.assertRaises(OSError):
                setup.start(allow_public_account_access=True)

        first_spawn = events.index("spawn")
        self.assertGreater(first_spawn, 1, "signal handlers must be installed before the first child")
        signal_events = [event for event in events if isinstance(event, tuple) and event[0] == "signal"]
        self.assertEqual([event[1] for event in signal_events], [2, 15, 2, 15])
        self.assertEqual(signal_events[2][2:], ("previous-2",))
        self.assertEqual(signal_events[3][2:], ("previous-15",))
        self.assertEqual(events.count("terminate-managed-child"), 1)

    def test_failed_bridge_mcp_check_prevents_tunnel_and_cleans_bridge(self):
        events = []

        class Child:
            stdout = None
            def poll(self): return None
            def terminate(self): events.append("bridge-terminated")
            def wait(self, timeout=None): return 0

        managed = Child()
        response = type("Response", (), {"status": 200, "__enter__": lambda self: self, "__exit__": lambda *args: None})()

        def spawn(*args, **_kwargs):
            events.append(args[0][0])
            return managed

        with mock.patch.object(setup.shutil, "which", side_effect=lambda name: name), \
             mock.patch.object(setup, "check_upstream"), \
             mock.patch.object(setup, "_port_available", return_value=True), \
             mock.patch.object(setup.Path, "is_file", return_value=True), \
             mock.patch.object(setup.signal, "signal", side_effect=lambda _sig, handler: signal.SIG_DFL), \
             mock.patch.object(setup.subprocess, "Popen", side_effect=spawn), \
             mock.patch.object(setup, "urlopen", return_value=response), \
             mock.patch.object(setup.socket, "create_connection", return_value=mock.MagicMock(__enter__=lambda self: self, __exit__=lambda *args: None)), \
             mock.patch.object(setup, "check_url", side_effect=RuntimeError("bridge MCP initialization failed")):
            with self.assertRaisesRegex(RuntimeError, "initialization"):
                setup.start(allow_public_account_access=True)
        self.assertEqual(events, ["node", "bridge-terminated"])

    def test_check_rejects_mismatched_jsonrpc_response_id(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                payload = json.dumps({"jsonrpc": "2.0", "id": 999, "result": {}}).encode()
                self.send_response(200)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            def log_message(self, *_args): pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with self.assertRaisesRegex(RuntimeError, "MCP request failed"):
                setup._rpc(f"http://127.0.0.1:{server.server_port}/mcp/openai", "initialize", request_id=1)
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def test_check_initializes_and_discovers_list_devices_without_calling_tool(self):
        received = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                request = json.loads(body)
                received.append(request)
                if "id" not in request:
                    self.send_response(202)
                    self.end_headers()
                    return
                if request["method"] == "initialize":
                    result = {"protocolVersion": "2025-03-26", "capabilities": {"tools": {}}, "serverInfo": {"name": "test", "version": "1"}}
                else:
                    result = {"tools": [{"name": "list_devices"}]}
                payload = json.dumps({"jsonrpc": "2.0", "id": request["id"], "result": result}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *_args):
                pass

        server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            result = setup.check_url(f"http://127.0.0.1:{server.server_port}/mcp/openai")
        finally:
            server.shutdown()
            thread.join()
            server.server_close()
        self.assertTrue(result)
        self.assertEqual([r["method"] for r in received], ["initialize", "notifications/initialized", "tools/list"])


if __name__ == "__main__":
    unittest.main()
