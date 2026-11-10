#!/usr/bin/env node
// KIT ADDITION — ai-agentic-kit safety wrapper, NOT upstream.
// Runs the vendored, unmodified `teardown.mjs` with two guards installed first:
//
//   1. SSRF guard on every fetch(): only http(s); each hop's hostname is resolved
//      and refused if any address is loopback, private, link-local, CGNAT,
//      unique-local, multicast or unspecified (cloud metadata included).
//      IPv6 is parsed to 16 bytes; IPv4 embedded via ::ffff:, ::a.b.c.d, NAT64
//      (64:ff9b::) or 6to4 (2002::) is extracted and checked against the IPv4 list.
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
import { isIP, BlockList } from 'node:net';
import { syncBuiltinESMExports } from 'node:module';
import zlib from 'node:zlib';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const ALLOW_PRIVATE = process.env.AAK_ALLOW_PRIVATE_URLS === '1';
const MAX_GUNZIP = Number(process.env.AAK_MAX_GUNZIP_BYTES) > 0
  ? Number(process.env.AAK_MAX_GUNZIP_BYTES) : 256 * 1024 * 1024;
const MAX_REDIRECTS = 5;

// IPv4 ranges that are never a public web origin.
const V4 = new BlockList();
for (const [net, bits] of [
  ['0.0.0.0', 8], ['10.0.0.0', 8], ['100.64.0.0', 10], ['127.0.0.0', 8],
  ['169.254.0.0', 16], ['172.16.0.0', 12], ['192.0.0.0', 24], ['192.0.2.0', 24],
  ['192.168.0.0', 16], ['198.18.0.0', 15], ['198.51.100.0', 24], ['203.0.113.0', 24],
  ['224.0.0.0', 4], ['240.0.0.0', 4],
]) V4.addSubnet(net, bits, 'ipv4');

// Expand any IPv6 text form (incl. "::", embedded dotted quad, zone id) to 16 bytes.
function v6Bytes(s) {
  s = s.split('%')[0];
  const dq = s.match(/(\d+\.\d+\.\d+\.\d+)$/);
  if (dq) {
    const o = dq[1].split('.').map(Number);
    s = s.slice(0, -dq[1].length) + ((o[0] << 8) | o[1]).toString(16) + ':' + ((o[2] << 8) | o[3]).toString(16);
  }
  const [head, tail] = s.split('::');
  const h = head ? head.split(':') : [];
  const tl = tail !== undefined ? (tail ? tail.split(':') : []) : [];
  const groups = tail !== undefined ? [...h, ...Array(8 - h.length - tl.length).fill('0'), ...tl] : h;
  if (groups.length !== 8) return null;
  const b = [];
  for (const g of groups) { const n = parseInt(g, 16); b.push(n >> 8, n & 255); }
  return b;
}

const v4of = (b, i) => `${b[i]}.${b[i + 1]}.${b[i + 2]}.${b[i + 3]}`;

export function isBlockedAddress(ip) {
  ip = ip.replace(/^\[|\]$/g, '');
  if (isIP(ip) === 4) return V4.check(ip, 'ipv4');
  if (isIP(ip.split('%')[0]) !== 6) return true;          // unparseable: refuse
  const b = v6Bytes(ip);
  if (!b) return true;
  const zero = (from, to) => b.slice(from, to).every(x => x === 0);
  if (zero(0, 16)) return true;                              // ::
  if (zero(0, 15) && b[15] === 1) return true;               // ::1
  if (zero(0, 10) && b[10] === 255 && b[11] === 255) return V4.check(v4of(b, 12), 'ipv4'); // ::ffff:a.b.c.d
  if (zero(0, 12)) return V4.check(v4of(b, 12), 'ipv4');     // ::a.b.c.d (IPv4-compatible)
  if (b[0] === 0x00 && b[1] === 0x64 && b[2] === 0xff && b[3] === 0x9b) {
    if (b[4] === 0x00 && b[5] === 0x01) return true;          // 64:ff9b:1::/48 local-use NAT64: refuse
    return V4.check(v4of(b, 12), 'ipv4');                    // well-known NAT64 64:ff9b::/96
  }
  if (b[0] === 0x20 && b[1] === 0x02) return V4.check(v4of(b, 2), 'ipv4'); // 6to4 2002::/16
  if (b[0] === 0x20 && b[1] === 0x01 && b[2] === 0 && b[3] === 0) return true; // Teredo 2001::/32
  if ((b[0] & 0xfe) === 0xfc) return true;                   // fc00::/7 unique-local
  if (b[0] === 0xfe && (b[1] & 0xc0) === 0x80) return true;  // fe80::/10 link-local
  if (b[0] === 0xfe && (b[1] & 0xc0) === 0xc0) return true;  // fec0::/10 site-local (deprecated)
  if (b[0] === 0xff) return true;                            // multicast
  if (b[0] === 0x20 && b[1] === 0x01 && b[2] === 0x0d && b[3] === 0xb8) return true; // documentation
  return false;
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
