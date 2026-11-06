#!/usr/bin/env node
import { open, lstat, mkdir, chmod } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';

function validate(value) {
  if (value.length > 4096 || !/^dr_sk_[A-Za-z0-9_-]+$/.test(value)) throw new Error('Invalid key');
  return value;
}

async function hiddenKey() {
  const tty = await open('/dev/tty', 'r+');
  const wasRaw = process.stdin.isRaw;
  try {
    const { stdin } = process;
    if (!stdin.isTTY) throw new Error('Interactive terminal required');
    stdin.setRawMode(true); stdin.resume();
    process.stderr.write('Enter local Mobilerun API key (input hidden): ');
    let value = '';
    for await (const chunk of stdin) {
      for (const char of chunk.toString()) {
        if (char === '\r' || char === '\n') { process.stderr.write('\n'); return validate(value); }
        if (char === '\u0003') throw new Error('Cancelled');
        if (char === '\u007f' || char === '\b') value = value.slice(0, -1); else { value += char; if (value.length > 4096) throw new Error('Invalid key'); }
      }
    }
    throw new Error('No key entered');
  } finally {
    if (process.stdin.isTTY) { process.stdin.setRawMode(Boolean(wasRaw)); process.stdin.pause(); }
    await tty.close();
  }
}

async function main() {
  if (process.argv.length !== 2) throw new Error('Unexpected arguments');
  const key = await hiddenKey();
  const directory = path.join(os.homedir(), '.config/mobilerun');
  for (const dir of [path.join(os.homedir(), '.config'), directory]) {
    try { await mkdir(dir, { mode: 0o700 }); } catch (error) { if (error.code !== 'EEXIST') throw error; }
    const st = await lstat(dir);
    if (!st.isDirectory() || st.isSymbolicLink() || st.uid !== process.getuid?.()) throw new Error('Invalid directory');
  }
  const destination = path.join(directory, 'local-mcp.json');
  try { await lstat(destination); throw new Error('Credential file already exists; remove it manually to replace'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  const file = await open(destination, 'wx', 0o600);
  try { await file.writeFile(JSON.stringify({ apiKey: key }) + '\n'); await file.sync(); }
  catch (error) { await file.close(); throw error; }
  await file.close(); await chmod(destination, 0o600);
  process.stderr.write('Local credential saved securely.\n');
}

main().catch(() => { process.stderr.write('Could not save local credentials.\n'); process.exitCode = 1; });
