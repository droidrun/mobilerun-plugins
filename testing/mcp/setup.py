#!/usr/bin/env python3
"""Safe, foreground-only launcher and smoke checker for the local MCP tunnel."""
import argparse
import ipaddress
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import queue
import re
import threading
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
DEFAULT_UPSTREAM = "http://127.0.0.1:8080/mcp/openai"
READINESS_TIMEOUT = 30
HTTP_TIMEOUT = 8


def validate_mcp_url(url):
    if not isinstance(url, str) or not url or any(ord(ch) < 32 or ord(ch) == 127 for ch in url) or url != url.strip():
        raise ValueError("Invalid MCP URL")
    parsed = urlsplit(url)
    try:
        parsed.port
    except ValueError:
        raise ValueError("Invalid MCP URL") from None
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise ValueError("URL must not contain credentials, query, or fragment")
    if parsed.path != "/mcp/openai":
        raise ValueError("URL path must be /mcp/openai")
    if parsed.scheme == "https" and parsed.hostname:
        return url
    if parsed.scheme == "http" and parsed.hostname:
        try:
            if ipaddress.ip_address(parsed.hostname).is_loopback:
                return url
        except ValueError:
            if parsed.hostname.lower() == "localhost":
                return url
    raise ValueError("URL must use HTTPS, or HTTP on loopback only")


def validate_upstream_url(url):
    validate_mcp_url(url)
    parsed = urlsplit(url)
    if parsed.scheme != "http":
        raise ValueError("Upstream must use loopback HTTP")
    hostname = parsed.hostname.lower()
    loopback = hostname in ("127.0.0.1", "::1", "localhost")
    if not loopback:
        raise ValueError("Upstream must use loopback HTTP")
    return url


def validate_port(port):
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535")
    return port


def check_upstream(url):
    validate_upstream_url(url)
    parsed = urlsplit(url)
    health = f"http://{parsed.netloc}/health"
    opener = build_opener(_NoRedirect())
    with opener.open(Request(health, method="GET"), timeout=HTTP_TIMEOUT) as response:
        if response.status != 200:
            raise RuntimeError("Upstream health check failed")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _read_tunnel_output(stream, found):
    tail = ""
    pattern = re.compile(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com")
    while True:
        chunk = stream.read(4096)
        if not chunk:
            return
        if isinstance(chunk, bytes):
            chunk = chunk.decode("utf-8", "ignore")
        tail = (tail + chunk)[-8192:]
        match = pattern.search(tail)
        if match:
            try:
                found.put_nowait(match.group(0))
            except queue.Full:
                pass


def _rpc(url, method, params=None, request_id=1):
    payload = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}}).encode()
    request = Request(url, data=payload, headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    with urlopen(request, timeout=HTTP_TIMEOUT) as response:
        if response.status != 200:
            raise RuntimeError("MCP endpoint returned HTTP error")
        raw = response.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise RuntimeError("MCP response exceeded size limit")
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        text = raw.decode("utf-8", "replace")
        candidates = [line[6:] for line in text.splitlines() if line.startswith("data: ")]
        data = json.loads(candidates[-1]) if candidates else None
    if (not isinstance(data, dict) or data.get("jsonrpc") != "2.0"
            or data.get("id") != request_id or "error" in data
            or not isinstance(data.get("result"), dict)):
        raise RuntimeError("MCP request failed")
    return data["result"]


def check_url(url):
    url = validate_mcp_url(url)
    _rpc(url, "initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "mobilerun-mcp-check", "version": "1.0"}}, 1)
    notification = Request(url, data=json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}).encode(), headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    with urlopen(notification, timeout=HTTP_TIMEOUT):
        pass
    result = _rpc(url, "tools/list", {}, 2)
    names = {tool.get("name") for tool in result.get("tools", []) if isinstance(tool, dict)}
    if "list_devices" not in names:
        raise RuntimeError("MCP endpoint does not advertise list_devices")
    print("MCP initialization succeeded; list_devices is advertised (no device call made).")
    return True


def _port_available(port):
    with socket.socket() as sock:
        try:
            sock.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def _stop_children(children):
    for child in reversed(children):
        if child.poll() is None:
            child.terminate()
    deadline = time.monotonic() + 3
    for child in reversed(children):
        if child.poll() is None:
            try:
                child.wait(timeout=max(0.1, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


def start(upstream=DEFAULT_UPSTREAM, port=8081, allow_public_account_access=False, build=False):
    if not allow_public_account_access:
        raise ValueError("start requires --allow-public-account-access")
    upstream = validate_upstream_url(upstream)
    validate_port(port)
    if not _port_available(port):
        raise ValueError(f"Loopback port {port} is already in use")
    node, tunnel = shutil.which("node"), shutil.which("cloudflared")
    if not node or not tunnel:
        raise RuntimeError("Both node and cloudflared must be installed")
    check_upstream(upstream)
    bridge = HERE / "bridge.mjs"
    if not bridge.is_file():
        raise RuntimeError("MCP bridge is missing")
    env = os.environ.copy()
    env.update({"BRIDGE_PORT": str(port), "BRIDGE_UPSTREAM_URL": upstream})
    children = []
    old_handlers = {}
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            old_handlers[sig] = signal.signal(sig, lambda _signum, _frame: (_ for _ in ()).throw(KeyboardInterrupt()))
        children.append(subprocess.Popen([node, str(bridge)], cwd=str(HERE), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            if children[0].poll() is not None:
                raise RuntimeError("Bridge process exited during startup")
            try:
                with urlopen(f"http://127.0.0.1:{port}/health", timeout=0.2) as response:
                    if response.status == 200:
                        break
            except OSError:
                pass
            time.sleep(0.1)
        else:
            raise RuntimeError("Bridge did not become ready")
        check_url(f"http://127.0.0.1:{port}/mcp/openai")
        children.append(subprocess.Popen([tunnel, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=0))
        found = queue.Queue(maxsize=1)
        reader = threading.Thread(target=_read_tunnel_output, args=(children[-1].stdout, found), daemon=True)
        reader.start()
        deadline = time.monotonic() + READINESS_TIMEOUT
        public_url = None
        while time.monotonic() < deadline:
            if children[-1].poll() is not None:
                raise RuntimeError("cloudflared exited before producing a tunnel URL")
            try:
                public_url = found.get(timeout=0.2) + "/mcp/openai"
            except queue.Empty:
                pass
            if public_url:
                break
        if not public_url:
            raise RuntimeError("Timed out waiting for a public tunnel URL")
        validate_mcp_url(public_url)
        print(f"MCP URL: {public_url}", flush=True)
        print("Warning: this public URL exposes the account through all advertised tools. Keep this process running only while needed; Ctrl-C stops its bridge and tunnel.", flush=True)
        if build:
            subprocess.run([sys.executable, str(HERE / "package_plugins.py"), "--url", public_url], check=True)
        while all(child.poll() is None for child in children):
            time.sleep(0.25)
        raise RuntimeError("A managed child process exited")
    finally:
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)
        _stop_children(children)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    begin = sub.add_parser("start")
    begin.add_argument("--allow-public-account-access", action="store_true")
    begin.add_argument("--upstream", default=DEFAULT_UPSTREAM)
    begin.add_argument("--port", type=int, default=8081)
    begin.add_argument("--build", action="store_true")
    check = sub.add_parser("check")
    check.add_argument("--url", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            start(args.upstream, args.port, args.allow_public_account_access, args.build)
        else:
            check_url(args.url)
    except KeyboardInterrupt:
        return 0
    except (ValueError, RuntimeError, URLError, OSError, subprocess.SubprocessError):
        print("Error: MCP setup failed; check the supplied URL, local prerequisites, and service health.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
