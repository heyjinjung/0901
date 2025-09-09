#!/usr/bin/env node
import { execSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';

function run(cmd) {
    try { return execSync(cmd, { stdio: ['ignore', 'pipe', 'ignore'] }).toString().trim(); } catch { return ''; }
}
const hash = run('git rev-parse --short HEAD') || 'nogit';
const ts = new Date();
const pad = (n) => String(n).padStart(2, '0');
const stamp = `${ts.getUTCFullYear()}${pad(ts.getUTCMonth() + 1)}${pad(ts.getUTCDate())}-${pad(ts.getUTCHours())}${pad(ts.getUTCMinutes())}${pad(ts.getUTCSeconds())}`;
const buildId = `${hash}-${stamp}`;
writeFileSync('.env.build', `NEXT_PUBLIC_BUILD_ID=${buildId}\n`);
console.log('[gen-build-id] generated', buildId);
