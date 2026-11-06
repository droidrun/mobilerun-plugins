#!/usr/bin/env node
import http from 'node:http';
import { open } from 'node:fs/promises';
import { constants } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const MAX_REQUEST = 2 * 1024 * 1024;
const MAX_RESPONSE = 8 * 1024 * 1024;
const MAX_ACTIVE = 16;
// Optional shorter timeout for local testing; never exceeds the 30-second limit.
const timeoutText = process.env.BRIDGE_TIMEOUT_MS ?? '30000';
const TIMEOUT = /^\d+$/.test(timeoutText) && Number(timeoutText) >= 1 && Number(timeoutText) <= 30000 ? Number(timeoutText) : null;

async function credentials() {
  const filename = process.env.MOBILERUN_LOCAL_CREDENTIAL_FILE || path.join(os.homedir(), '.config/mobilerun/local-mcp.json');
  const file = await open(filename, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const st = await file.stat();
    if (!st.isFile() || st.uid !== process.getuid?.() || (st.mode & 0o077) || st.size > 4096) throw new Error();
    const buffer = Buffer.alloc(4097);
    const { bytesRead } = await file.read(buffer, 0, buffer.length, 0);
    if (bytesRead > 4096) throw new Error();
    const key = JSON.parse(buffer.subarray(0, bytesRead).toString('utf8')).apiKey;
    if (typeof key !== 'string' || key.length > 4096 || key.trim() !== key || !/^dr_sk_[A-Za-z0-9_-]+$/.test(key)) throw new Error();
    return key;
  } finally { await file.close(); }
}

function upstreamURL() {
  const url = new URL(process.env.BRIDGE_UPSTREAM_URL || 'http://127.0.0.1:8080/mcp/openai');
  if (url.protocol !== 'http:' || !['127.0.0.1', '[::1]', 'localhost'].includes(url.hostname) || url.username || url.password || url.pathname !== '/mcp/openai' || url.search || url.hash) throw new Error();
  return url.href;
}

async function main() {
  if (TIMEOUT === null) throw new Error();
  const portText = process.env.BRIDGE_PORT ?? '8081';
  if (!/^\d+$/.test(portText) || Number(portText) > 65535) throw new Error();
  const target = upstreamURL();
  const key = await credentials();
  let active = 0;
  const server = http.createServer(async (req, res) => {
    if (req.url === '/health' && req.method === 'GET') { res.writeHead(200, { 'content-type': 'text/plain' }); res.end('ok'); return; }
    if (req.url !== '/mcp/openai') { res.writeHead(404); res.end(); return; }
    if (req.method !== 'POST') { res.writeHead(405); res.end(); return; }
    if (active >= MAX_ACTIVE) { res.writeHead(503); res.end(); return; }
    active++;
    const controller = new AbortController();
    const timer = setTimeout(() => { controller.abort(); if (!res.headersSent) { res.writeHead(504); res.end(); res.once('finish', () => req.destroy()); } else { res.destroy(); req.destroy(); } }, TIMEOUT);
    const abortOnClose = () => { if (!res.writableFinished) { controller.abort(); req.destroy(); } };
    res.on('close', abortOnClose);
    try {
      if (Number(req.headers['content-length']) > MAX_REQUEST) { res.writeHead(413); res.end(); req.resume(); return; }
      const chunks = []; let size = 0;
      for await (const chunk of req) {
        if (controller.signal.aborted) return;
        size += chunk.length;
        if (size > MAX_REQUEST) { res.writeHead(413); res.end(); req.resume(); return; }
        chunks.push(chunk);
      }
      if (controller.signal.aborted) return;
      const upstream = await fetch(target, {
        method: 'POST', redirect: 'error', signal: controller.signal,
        headers: { 'content-type': 'application/json', accept: 'application/json, text/event-stream', authorization: `Bearer ${key}` },
        body: Buffer.concat(chunks, size),
      });
      const result = []; let responseSize = 0;
      if (upstream.body) {
        for await (const chunk of upstream.body) {
          responseSize += chunk.length;
          if (responseSize > MAX_RESPONSE) { controller.abort(); throw new Error(); }
          result.push(chunk);
        }
      }
      if (controller.signal.aborted) return;
      const contentType = upstream.headers.get('content-type');
      res.writeHead(upstream.status, contentType ? { 'content-type': contentType } : {});
      res.end(Buffer.concat(result, responseSize));
    } catch {
      if (!res.headersSent && !res.destroyed) { res.writeHead(502); res.end(); }
      else if (!res.writableEnded) res.destroy();
    } finally { clearTimeout(timer); res.off('close', abortOnClose); active--; }
  });
  server.requestTimeout = TIMEOUT;
  server.headersTimeout = TIMEOUT;
  server.on('error', () => { console.error('Public bridge unavailable.'); process.exitCode = 1; });
  server.listen(Number(portText), '127.0.0.1');
}

main().catch(() => { console.error('Public bridge unavailable.'); process.exitCode = 1; });
