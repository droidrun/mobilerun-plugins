#!/usr/bin/env node
import { open } from 'node:fs/promises';
import { constants } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const fail = (message) => { console.error(message); process.exitCode = 1; };
const maxLine = 1024 * 1024;
const maxResponse = 8 * 1024 * 1024;
let controller;
let shuttingDown = false;
const active = new Set();

function keyCheck(key) {
  if (typeof key !== 'string' || key.length > 4096 || !/^dr_sk_[A-Za-z0-9_-]+$/.test(key)) throw new Error('Invalid local API key');
  return key;
}

async function getKey() {
  if (process.env.MOBILERUN_CLOUD_API_KEY) return keyCheck(process.env.MOBILERUN_CLOUD_API_KEY);
  const filename = process.env.MOBILERUN_LOCAL_CREDENTIAL_FILE || path.join(os.homedir(), '.config/mobilerun/local-mcp.json');
  const file = await open(filename, constants.O_RDONLY | constants.O_NOFOLLOW | constants.O_NONBLOCK);
  try {
    const st = await file.stat();
    if (!st.isFile() || st.uid !== process.getuid?.() || (st.mode & 0o077) || st.size > 4096) throw new Error('Invalid credentials');
    const buffer = Buffer.alloc(4097);
    const { bytesRead } = await file.read(buffer, 0, buffer.length, 0);
    if (bytesRead > 4096) throw new Error('Invalid credentials');
    return keyCheck(JSON.parse(buffer.subarray(0, bytesRead).toString('utf8')).apiKey);
  } finally { await file.close(); }
}

function endpoint() {
  const url = new URL(process.env.MOBILERUN_LOCAL_MCP_URL || 'http://localhost:8080/mcp/openai');
  if (url.protocol !== 'http:' || !['localhost', '127.0.0.1', '[::1]'].includes(url.hostname) || url.username || url.password || url.hash) throw new Error('Bridge endpoint must be an explicit loopback HTTP URL');
  return url.href;
}

async function relay(raw, key, target) {
  let request;
  try { request = JSON.parse(raw); } catch { rpcError(null, -32700, 'Parse error'); return; }
  if (!request || typeof request !== 'object' || Array.isArray(request) || request.jsonrpc !== '2.0' || typeof request.method !== 'string' || (Object.hasOwn(request, 'id') && !(request.id === null || typeof request.id === 'string' || typeof request.id === 'number'))) { rpcError(null, -32600, 'Invalid Request'); return; }
  const hasId = Object.hasOwn(request, 'id');
  const abort = new AbortController(); active.add(abort);
  try {
    const response = await fetch(target, { method: 'POST', redirect: 'error', signal: AbortSignal.any([abort.signal, AbortSignal.timeout(30000)]), headers: { 'content-type': 'application/json', accept: 'application/json, text/event-stream', authorization: `Bearer ${key}` }, body: raw });
    if (!hasId) return;
    if (!response.ok) { console.log(JSON.stringify({ jsonrpc: '2.0', id: request.id, error: { code: -32000, message: 'Local MCP server request failed' } })); return; }
    const reader = response.body.getReader(); let bytes = 0; const chunks = [];
    for (;;) { const {done, value} = await reader.read(); if (done) break; bytes += value.length; if (bytes > maxResponse) throw new Error('response too large'); chunks.push(value); }
    const text = Buffer.concat(chunks).toString('utf8');
    const result = JSON.parse(text);
    if (!result || result.jsonrpc !== '2.0' || result.id !== request.id || (Object.hasOwn(result, 'result') === Object.hasOwn(result, 'error'))) throw new Error('Invalid response');
    console.log(JSON.stringify(result));
  } catch {
    if (hasId && !shuttingDown) console.log(JSON.stringify({ jsonrpc: '2.0', id: request.id, error: { code: -32000, message: 'Local MCP server request failed' } }));
  } finally { active.delete(abort); }
}

function rpcError(id, code, message) {
  console.log(JSON.stringify({ jsonrpc: '2.0', id, error: { code, message } }));
}

async function main() {
  if (process.argv.length > 3 || (process.argv[2] && process.argv[2] !== 'stdio')) throw new Error('Invalid arguments');
  if (typeof AbortSignal.any !== 'function') {
    console.error('This local MCP bridge requires Node.js 20.3 or later (AbortSignal.any is unavailable).');
    process.exitCode = 1;
    return;
  }
  const [key, target] = await Promise.all([getKey(), Promise.resolve(endpoint())]);
  const tasks = new Set();
  let pieces = [], size = 0, oversized = false;
  async function dispatch() {
    if (oversized) rpcError(null, -32600, 'Invalid Request');
    else {
      while (tasks.size >= 32) await Promise.race(tasks);
      const task = relay(Buffer.concat(pieces, size).toString('utf8'), key, target);
      tasks.add(task); task.finally(() => tasks.delete(task));
    }
    pieces = []; size = 0; oversized = false;
  }
  for await (const chunk of process.stdin) {
    let start = 0;
    for (let i = 0; i <= chunk.length; i++) {
      if (i !== chunk.length && chunk[i] !== 10) continue;
      const part = chunk.subarray(start, i); size += part.length;
      if (size > maxLine) { oversized = true; pieces = []; }
      else if (!oversized) pieces.push(part);
      if (i < chunk.length) await dispatch();
      start = i + 1;
    }
  }
  if (size || oversized) await dispatch();
  await Promise.allSettled(tasks);
}

process.on('SIGINT', () => { shuttingDown = true; for (const c of active) c.abort(); process.exit(0); });
process.on('SIGTERM', () => { shuttingDown = true; for (const c of active) c.abort(); process.exit(0); });
main().catch(() => fail('Local MCP bridge unavailable. Run setup-local-auth.mjs to configure local credentials.'));
