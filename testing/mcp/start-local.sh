#!/bin/bash
set -euo pipefail
umask 077
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPO="${MOBILERUN_MCP_REPO:-$HOME/Documents/GitHub/mobilerun-mcp}"
build=1
show=0
for arg in "$@"; do
  case "$arg" in
    --no-build) build=0 ;;
    --show-url) show=1 ;;
    *) echo "Usage: $0 [--no-build] [--show-url]" >&2; exit 2 ;;
  esac
done
: "${MOBILERUN_API_KEY:?Set MOBILERUN_API_KEY before starting}"
for cmd in docker git node cloudflared curl openssl python3; do
  command -v "$cmd" >/dev/null || { echo "Missing dependency: $cmd" >&2; exit 1; }
done
export MOBILERUN_CHATGPT_PATH_TOKEN="${MOBILERUN_CHATGPT_PATH_TOKEN:-$(openssl rand -hex 32)}"
if [[ ! "$MOBILERUN_CHATGPT_PATH_TOKEN" =~ ^[0-9a-f]{64,}$ ]]; then
  echo 'Path token must be at least 64 lowercase hexadecimal characters.' >&2; exit 1
fi
if docker container inspect mobilerun-mcp-local >/dev/null 2>&1; then
  echo 'Container mobilerun-mcp-local already exists; refusing to replace it.' >&2; exit 1
fi
log="$(mktemp)"
proxy_pid=''
tunnel_pid=''
container_id=''
cleanup() {
  trap - EXIT INT TERM
  [ -z "$tunnel_pid" ] || kill "$tunnel_pid" 2>/dev/null || true
  [ -z "$proxy_pid" ] || kill "$proxy_pid" 2>/dev/null || true
  [ -z "$tunnel_pid" ] || wait "$tunnel_pid" 2>/dev/null || true
  [ -z "$proxy_pid" ] || wait "$proxy_pid" 2>/dev/null || true
  if [ -n "$container_id" ]; then
    docker rm -f "$container_id" >/dev/null 2>&1 || true
  else
    owned="$(docker ps -aq --filter 'name=^/mobilerun-mcp-local$' --filter "label=mobilerun-local-launcher=$$" 2>/dev/null || true)"
    if [ -n "$owned" ]; then
      while IFS= read -r id; do docker rm -f "$id" >/dev/null 2>&1 || true; done <<< "$owned"
    fi
  fi
  rm -f "$log"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
if [ "$build" = 1 ]; then
  git -C "$REPO" fetch origin main
  git -C "$REPO" archive origin/main | docker build -t mobilerun-mcp-local-main -
fi
container_id="$(docker create --name mobilerun-mcp-local --label "mobilerun-local-launcher=$$" -p 127.0.0.1:18080:8080 -e MOBILERUN_API_KEY -e MCP_DEVICE_STREAM_ENABLED=true -e MCP_DEVICE_STREAM_ORIGINS=wss://api.mobilerun.ai,wss://cloud.mobilerun.ai mobilerun-mcp-local-main)"
docker start "$container_id" >/dev/null
ready=0
for ((i=0; i<60; i++)); do
  if curl --noproxy '*' -fsS http://127.0.0.1:18080/health >/dev/null 2>&1; then ready=1; break; fi
  sleep 1
done
[ "$ready" = 1 ] || { echo 'Container health check failed.' >&2; exit 1; }
node - <<'NODE' &
'use strict';
const http = require('node:http');
const crypto = require('node:crypto');
const expected = Buffer.from(process.env.MOBILERUN_CHATGPT_PATH_TOKEN);
const key = process.env.MOBILERUN_API_KEY;
function route(req) {
  const match = /^\/([0-9a-f]+)(\/[^#]*)$/.exec(req.url || '');
  if (!match) return null;
  const candidate = Buffer.from(match[1]);
  return candidate.length === expected.length && crypto.timingSafeEqual(candidate, expected) ? match[2] : null;
}
function headers(req) {
  const result = {...req.headers, host:'127.0.0.1:18080', 'x-mobilerun-cloud-api-key':key};
  delete result.authorization; delete result['proxy-authorization']; delete result.cookie;
  return result;
}
const server = http.createServer((req, res) => {
  const path = route(req);
  if (!path) { res.writeHead(404, {'content-length':'0'}); return res.end(); }
  const proxy = http.request({host:'127.0.0.1', port:18080, method:req.method, path, headers:headers(req)}, upstream => {
    res.writeHead(upstream.statusCode, upstream.headers); upstream.pipe(res);
  });
  proxy.on('error', () => { if (!res.headersSent) res.writeHead(502); res.end(); });
  req.on('aborted', () => proxy.destroy()); res.on('close', () => proxy.destroy()); req.pipe(proxy);
});
server.on('upgrade', (req, socket, head) => {
  const path = route(req);
  if (!path) return socket.end('HTTP/1.1 404 Not Found\r\nConnection: close\r\nContent-Length: 0\r\n\r\n');
  const proxy = http.request({host:'127.0.0.1', port:18080, method:req.method, path, headers:headers(req)});
  proxy.on('upgrade', (response, target, first) => {
    let output = 'HTTP/1.1 101 Switching Protocols\r\n';
    for (let i=0; i<response.rawHeaders.length; i+=2) output += response.rawHeaders[i]+': '+response.rawHeaders[i+1]+'\r\n';
    socket.write(output+'\r\n'); if (first.length) socket.write(first); if (head.length) target.write(head);
    target.on('error',()=>socket.destroy()); socket.on('error',()=>target.destroy()); target.pipe(socket).pipe(target);
  });
  proxy.on('response', () => socket.end('HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\nContent-Length: 0\r\n\r\n'));
  proxy.on('error', () => socket.destroy()); proxy.end();
});
server.listen(18081, '127.0.0.1');
NODE
proxy_pid=$!
ready=0
for ((i=0; i<10; i++)); do
  kill -0 "$proxy_pid" 2>/dev/null || break
  if [ "$(curl --noproxy '*' -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18081/ || true)" = 404 ]; then ready=1; break; fi
  sleep 1
done
[ "$ready" = 1 ] || { echo 'Proxy failed to start.' >&2; exit 1; }
cloudflared tunnel --no-autoupdate --url http://127.0.0.1:18081 >"$log" 2>&1 &
tunnel_pid=$!
tunnel=''
for ((i=0; i<60; i++)); do
  kill -0 "$tunnel_pid" 2>/dev/null || break
  tunnel="$(grep -Eo 'https://[-a-z0-9]+\.trycloudflare\.com' "$log" | head -1 || true)"
  [ -z "$tunnel" ] || break
  sleep 1
done
[ -n "$tunnel" ] || { echo 'Tunnel failed to start.' >&2; exit 1; }
export LOCAL_MCP_URL="$tunnel/$MOBILERUN_CHATGPT_PATH_TOKEN/mcp"
export LOCAL_MCP_ROOT="$ROOT"
python3 - <<'PY'
import io, json, os, pathlib, stat, tempfile, time, urllib.request, urllib.error, zipfile
root = pathlib.Path(os.environ['LOCAL_MCP_ROOT'])
url = os.environ['LOCAL_MCP_URL']
headers = {'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'}
def rpc(method, params, ident):
    data = json.dumps({'jsonrpc':'2.0', 'id':ident, 'method':method, 'params':params}).encode()
    with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=30) as response:
        raw = response.read().decode()
    if raw.startswith('event:') or raw.startswith('data:'):
        raw = next(line[6:] for line in raw.splitlines() if line.startswith('data: '))
    result = json.loads(raw)
    if result.get('id') != ident or 'error' in result or not isinstance(result.get('result'), dict):
        raise RuntimeError('MCP verification failed')
    return result['result']
# Avoid caching an initial NXDOMAIN before Cloudflare publishes the quick tunnel.
time.sleep(10)
deadline = time.monotonic() + 300
while True:
    try:
        rpc('initialize', {'protocolVersion':'2025-03-26', 'capabilities':{}, 'clientInfo':{'name':'local-check','version':'1'}}, 1)
        break
    except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
        if time.monotonic() >= deadline:
            detail = f'HTTP {exc.code}' if isinstance(exc, urllib.error.HTTPError) else type(getattr(exc, 'reason', exc)).__name__
            raise RuntimeError(f'Public tunnel did not become ready ({detail})') from None
        time.sleep(2)
if not any(t.get('name') == 'list_devices' for t in rpc('tools/list', {}, 2).get('tools', [])):
    raise RuntimeError('list_devices not advertised')
try:
    urllib.request.urlopen(url.split('/', 3)[0] + '//' + url.split('/')[2] + '/mcp', timeout=30)
    raise RuntimeError('Missing-token request was accepted')
except urllib.error.HTTPError as exc:
    if exc.code != 404: raise
print('Public MCP initialize and tools/list passed; missing token returns 404.')
files = {
 'openai': ['plugin.json','mcp.json','README.md','LICENSE','assets/logo.svg','skills/onboarding/SKILL.md','skills/mobile-tasks/SKILL.md'],
 'claude': ['.claude-plugin/plugin.json','.mcp.json','README.md','LICENSE','assets/icon.png','skills/onboarding/SKILL.md','skills/mobile-tasks/SKILL.md'],
}
out = root / 'testing' / 'mcp' / 'zip'
out.mkdir(exist_ok=True)
def refuse_unsafe(target):
    try:
        mode = target.lstat().st_mode
    except FileNotFoundError:
        return
    if not stat.S_ISREG(mode):
        raise ValueError(f'Refusing non-regular destination: {target}')

def write_archive(target, data):
    refuse_unsafe(target)
    fd, name = tempfile.mkstemp(prefix='.local-mcp-', suffix='.zip', dir=target.parent)
    try:
        with os.fdopen(fd, 'w+b') as file:
            file.write(data)
        refuse_unsafe(target)
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)

for provider, names in files.items():
    source = root / 'plugins' / provider
    target = out / ('local-codex.zip' if provider == 'openai' else 'local-claude.zip')
    contents = {name:(source/name).read_bytes() for name in names}
    contents['LOCAL-TEST.md'] = (b'# Local test\n\nThis private tunnel URL grants access using the owner API key. '
        b'No OAuth is needed. The URL changes on restart. Keep this ZIP private.\n')
    config = 'mcp.json' if provider == 'openai' else '.mcp.json'
    contents[config] = (json.dumps({'mcpServers':{'mobilerun':{'type':'streamable-http' if provider == 'openai' else 'http', 'url':url}}}, indent=2)+'\n').encode()
    if provider == 'openai':
        manifest = json.loads(contents['plugin.json'])
        manifest['name'] = 'mobilerun-local'
        manifest['extensions']['com.openai']['interface']['displayName'] = 'Mobilerun (local)'
        contents['plugin.json'] = (json.dumps(manifest, indent=2)+'\n').encode()
    destination = pathlib.Path.home() / 'Downloads' / target.name
    refuse_unsafe(target)
    refuse_unsafe(destination)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        for member, data in contents.items():
            archive.writestr(member, data)
    write_archive(target, buffer.getvalue())
    write_archive(destination, buffer.getvalue())
    print('ZIP:', target, 'and', destination)
PY
if [ "$show" = 1 ]; then printf 'MCP URL: %s\n' "$LOCAL_MCP_URL"; else printf 'MCP URL: %s/[redacted]/mcp\n' "$tunnel"; fi
printf 'Anyone with the URL can access your account. Ctrl-C to stop.\n'
while kill -0 "$proxy_pid" 2>/dev/null && kill -0 "$tunnel_pid" 2>/dev/null; do sleep 1; done
echo 'A managed process exited.' >&2
exit 1
