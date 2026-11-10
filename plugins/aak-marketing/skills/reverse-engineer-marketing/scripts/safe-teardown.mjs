#!/usr/bin/env node
// KIT ADDITION — ai-agentic-kit safety wrapper, NOT upstream.
// Runs the vendored, unmodified `teardown.mjs` with two guards installed first:
//
//   1. SSRF guard on every fetch(): only http(s); each hop's hostname is resolved
//      and refused if any address is loopback, private, link-local, CGNAT,
//      unique-local, multicast or unspecified (cloud metadata included).
//      Redirects are followed manually (max 5) so every hop is re-checked.
//      Set AAK_ALLOW_PRIVATE_URLS=1 to scan localhost/intranet on purpose.
//   2. Decompression cap: gunzipSync() output is capped (default 256 MiB,
//      override with AAK_MAX_GUNZIP_BYTES) to stop gzip bombs in sitemaps.
//
// Why: teardown.mjs follows URLs taken from the target's own content
// (robots.txt `Sitemap:` lines, sitemap <loc> entries, a GrowthBook `apiHost`
// in the homepage HTML), so a hostile target could point it at internal hosts.
// Residual risk: DNS can change between this check and fetch's own lookup
// (rebinding); the guard narrows, not eliminates, that window.
//
// Usage: identical to teardown.mjs —  node <skill-dir>/scripts/safe-teardown.mjs <cmd> [args]

import { lookup } from 'node:dns/promises';
import { isIP } from 'node:net';
import { syncBuiltinESMExports } from 'node:module';
import zlib from 'node:zlib';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const ALLOW_PRIVATE = process.env.AAK_ALLOW_PRIVATE_URLS === '1';
const MAX_GUNZIP = Number(process.env.AAK_MAX_GUNZIP_BYTES) > 0
  ? Number(process.env.AAK_MAX_GUNZIP_BYTES) : 256 * 1024 * 1024;
const MAX_REDIRECTS = 5;

function v4Blocked(ip) {
  const [a, b] = ip.split('.').map(Number);
  return a === 0 || a === 10 || a === 127 || a >= 224 ||
    (a === 100 && b >= 64 && b <= 127) ||          // CGNAT
    (a === 169 && b === 254) ||                     // link-local / metadata
    (a === 172 && b >= 16 && b <= 31) ||
    (a === 192 && b === 168) ||
    (a === 192 && b === 0) ||                       // 192.0.0.0/24, 192.0.2.0/24
    (a === 198 && (b === 18 || b === 19));          // benchmarking
}

export function isBlockedAddress(ip) {
  if (isIP(ip) === 4) return v4Blocked(ip);
  const s = ip.toLowerCase().replace(/^\[|\]$/g, '').split('%')[0];
  const mapped = s.match(/^::ffff:(\d+\.\d+\.\d+\.\d+)$/);
  if (mapped) return v4Blocked(mapped[1]);
  if (s === '::' || s === '::1') return true;
  return /^(fc|fd|fe[89ab]|ff)/.test(s);           // ULA, link-local, multicast
}

async function assertPublic(url) {
  const u = new URL(url);
  if (u.protocol !== 'https:' && u.protocol !== 'http:') {
    throw new Error(`blocked by kit SSRF guard: scheme ${u.protocol} (${url})`);
  }
  if (ALLOW_PRIVATE) return;
  const host = u.hostname.replace(/^\[|\]$/g, '');
  const addrs = isIP(host) ? [{ address: host }] : await lookup(host, { all: true });
  for (const { address } of addrs) {
    if (isBlockedAddress(address)) {
      throw new Error(`blocked by kit SSRF guard: ${u.hostname} resolves to non-public ${address}. ` +
        'Set AAK_ALLOW_PRIVATE_URLS=1 to scan localhost/intranet on purpose.');
    }
  }
}

const realFetch = globalThis.fetch;
globalThis.fetch = async function guardedFetch(input, init = {}) {
  let url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
  const follow = (init.redirect ?? 'follow') === 'follow';
  for (let hop = 0; ; hop++) {
    await assertPublic(url);
    const res = await realFetch(url, { ...init, redirect: 'manual' });
    const loc = res.headers.get('location');
    if (!follow || res.status < 300 || res.status > 399 || !loc) return res;
    if (hop >= MAX_REDIRECTS) throw new Error(`too many redirects (${url})`);
    url = new URL(loc, url).href;
  }
};

const realGunzipSync = zlib.gunzipSync;
zlib.gunzipSync = (buf, opts = {}) => realGunzipSync(buf, { maxOutputLength: MAX_GUNZIP, ...opts });
syncBuiltinESMExports();

const target = join(dirname(fileURLToPath(import.meta.url)), 'teardown.mjs');
process.argv[1] = target;                           // let teardown.mjs's own entry check run main()
await import(pathToFileURL(target).href);
