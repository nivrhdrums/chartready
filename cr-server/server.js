// ChartReady server: serves the app and relays remote-control messages between one computer and one phone.
// Run:  REMOTE_PASSWORD=yourpassword node server.js     (PORT defaults to 8787)
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { WebSocketServer } = require('ws');

const PORT = +process.env.PORT || 8787;
const PUBLIC = path.resolve(process.env.PUBLIC_DIR || path.join(__dirname, 'public'));
const DATA = path.resolve(process.env.DATA_FILE || path.join(__dirname, 'data', 'pairs.json'));
const PASSWORD = process.env.REMOTE_PASSWORD || '';
// LOCAL=1: the personal version on your own computer. The computer itself (localhost) becomes the host without a password;
// phones on the same WiFi still pair only with the 6-digit code shown on the computer.
const LOCAL = process.env.LOCAL === '1';
const os = require('os');
// home WiFi addresses first (192.168.x, then 10.x); virtual adapters (WSL, Hyper-V, VPN, 172.x) and 169.254.x last
const lanRank = ip => ip.startsWith('192.168.') ? 0 : ip.startsWith('10.') ? 1 : ip.startsWith('169.254.') ? 9 : 5;
const lanIPs = () => Object.entries(os.networkInterfaces()).flatMap(([name, l]) => (l || []).filter(i => i && (i.family === 'IPv4' || i.family === 4) && !i.internal).map(i => ({ ip: i.address, name })))
  .filter(x => !/vEthernet|WSL|VirtualBox|VMware|docker|Hyper-V|vboxnet|utun|tailscale|zerotier/i.test(x.name) || true)
  .sort((a, b) => lanRank(a.ip) - lanRank(b.ip) || (/vEthernet|WSL|VirtualBox|VMware|docker|vbox|Hyper-V/i.test(a.name) ? 1 : 0) - (/vEthernet|WSL|VirtualBox|VMware|docker|vbox|Hyper-V/i.test(b.name) ? 1 : 0))
  .map(x => x.ip);
const isLoop = ip => ['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(ip);
if (!PASSWORD && !LOCAL) console.warn('[warn] REMOTE_PASSWORD is not set; remote control will refuse every computer.');

/* ---------- static files ---------- */
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.png': 'image/png', '.svg': 'image/svg+xml', '.ico': 'image/x-icon', '.css': 'text/css' };
const server = http.createServer((req, res) => {
  let p = decodeURIComponent((req.url || '/').split('?')[0]);
  if (p === '/lan') { const ip = lanIPs()[0]; res.writeHead(200, { 'content-type': 'application/json' }); return res.end(JSON.stringify({ url: ip ? `http://${ip}:${PORT}` : '', local: LOCAL })); }
  if (p === '/' || p === '') p = '/index.html';
  const file = path.resolve(PUBLIC, '.' + p);
  if (!file.startsWith(PUBLIC + path.sep)) { res.writeHead(403); return res.end(); }
  fs.readFile(file, (err, buf) => {
    if (err) { res.writeHead(404, { 'content-type': 'text/plain' }); return res.end('not found'); }
    const headers = { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' };
    if (p.endsWith('sw.js') || p.endsWith('.html')) headers['cache-control'] = 'no-cache';
    res.writeHead(200, headers); res.end(buf);
  });
});

/* ---------- pairing store ---------- */
// hosts: hostToken -> { created, phone: remoteToken|null, phoneName }
// a computer gets its hostToken once (with the password) and reconnects with it; the phone keeps its own remoteToken
let db = { hosts: {} };
try { db = JSON.parse(fs.readFileSync(DATA, 'utf8')); if (!db.hosts) db = { hosts: {} }; } catch (e) {}
function saveDb() { fs.mkdirSync(path.dirname(DATA), { recursive: true }); fs.writeFileSync(DATA, JSON.stringify(db, null, 1)); }
const hostOfPhone = tok => Object.keys(db.hosts).find(h => db.hosts[h].phone && db.hosts[h].phone === tok);
const codes = new Map(); // 6-digit code -> { host, expires }
const sameText = (a, b) => { const x = Buffer.from(String(a)), y = Buffer.from(String(b)); return x.length === y.length && crypto.timingSafeEqual(x, y); };
const token = () => crypto.randomBytes(24).toString('hex');

/* ---------- brute-force guard ---------- */
const attempts = new Map(); // ip -> { n, until }
function tooMany(ip) { const a = attempts.get(ip); return a && a.n >= 8 && Date.now() < a.until; }
function failed(ip) { const a = attempts.get(ip) || { n: 0, until: 0 }; if (Date.now() > a.until) a.n = 0; a.n++; a.until = Date.now() + 10 * 60 * 1000; attempts.set(ip, a); }

/* ---------- relay ---------- */
const rooms = new Map(); // hostToken -> { host, remote }
const wss = new WebSocketServer({ server, path: '/ws', maxPayload: 512 * 1024 });
const send = (ws, o) => { if (ws && ws.readyState === 1) ws.send(JSON.stringify(o)); };
function room(k) { if (!rooms.has(k)) rooms.set(k, { host: null, remote: null }); return rooms.get(k); }
function presence(k) { const r = rooms.get(k); if (!r) return; send(r.host, { t: 'peer', online: !!r.remote, phoneName: (db.hosts[k] || {}).phoneName || '', paired: !!(db.hosts[k] || {}).phone }); send(r.remote, { t: 'peer', online: !!r.host }); }
function join(ws, k, role) {
  const r = room(k), old = r[role];
  if (old && old !== ws) { send(old, { t: 'replaced' }); old.room = null; try { old.close(); } catch (e) {} }
  r[role] = ws; ws.room = k; ws.role = role;
  presence(k);
}

wss.on('connection', (ws, req) => {
  const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  ws.alive = true; ws.on('pong', () => { ws.alive = true; });
  ws.on('message', raw => {
    let m; try { m = JSON.parse(raw); } catch (e) { return; }
    if (m.t === 'host') {
      // computer: first time with the password, afterwards with its saved token
      if (m.token && db.hosts[m.token]) { send(ws, { t: 'hostOk', token: m.token }); return join(ws, m.token, 'host'); }
      if (tooMany(ip)) return send(ws, { t: 'err', code: 'locked' });
      const localOk = LOCAL && isLoop(ip);
      if (!localOk && (!PASSWORD || !sameText(m.pass || '', PASSWORD))) { failed(ip); return send(ws, { t: 'err', code: 'password' }); }
      const tk = token(); db.hosts[tk] = { created: new Date().toISOString(), phone: null, phoneName: '' }; saveDb();
      send(ws, { t: 'hostOk', token: tk }); return join(ws, tk, 'host');
    }
    if (m.t === 'pairStart' && ws.role === 'host') {
      let code; do { code = String(crypto.randomInt(0, 1e6)).padStart(6, '0'); } while (codes.has(code));
      codes.set(code, { host: ws.room, expires: Date.now() + 10 * 60 * 1000 });
      return send(ws, { t: 'pairCode', code });
    }
    if (m.t === 'pairJoin') {
      // phone: once with the code shown on the computer
      if (tooMany(ip)) return send(ws, { t: 'err', code: 'locked' });
      const c = codes.get(String(m.code || ''));
      if (!c || Date.now() > c.expires || !db.hosts[c.host]) { failed(ip); return send(ws, { t: 'err', code: 'badcode' }); }
      codes.delete(String(m.code));
      const r = rooms.get(c.host); if (r && r.remote) { send(r.remote, { t: 'revoked', why: 'other' }); r.remote = null; }
      const tk = token(); db.hosts[c.host].phone = tk; db.hosts[c.host].phoneName = String(m.name || 'טלפון').slice(0, 40); saveDb();
      send(ws, { t: 'paired', token: tk }); return join(ws, c.host, 'remote');
    }
    if (m.t === 'remoteAuto') {
      // personal version: any phone on the home WiFi becomes the remote of the computer, no code
      if (!LOCAL) return send(ws, { t: 'err', code: 'badcode' });
      const live = [...rooms.entries()].find(([k, r]) => r.host && db.hosts[k]);
      const h = live ? live[0] : null;
      if (!h) return send(ws, { t: 'err', code: 'nohost' });
      const r = rooms.get(h); if (r && r.remote && r.remote !== ws) { send(r.remote, { t: 'revoked', why: 'other' }); r.remote = null; }
      const tk = token(); db.hosts[h].phone = tk; db.hosts[h].phoneName = String(m.name || 'טלפון').slice(0, 40); saveDb();
      send(ws, { t: 'paired', token: tk }); return join(ws, h, 'remote');
    }
    if (m.t === 'remote') {
      const h = m.token && hostOfPhone(m.token);
      if (!h) return send(ws, { t: 'revoked' });
      return join(ws, h, 'remote');
    }
    if (m.t === 'unpair' && ws.room) {
      // either side can drop the phone; the computer keeps its own token
      const h = db.hosts[ws.room]; if (h) { h.phone = null; h.phoneName = ''; saveDb(); }
      const r = rooms.get(ws.room);
      if (r && r.remote) { send(r.remote, { t: 'revoked' }); r.remote.room = null; r.remote = null; }
      presence(ws.room); return;
    }
    if (m.t === 'msg' && ws.room) {
      const r = rooms.get(ws.room); if (!r) return;
      send(ws.role === 'host' ? r.remote : r.host, { t: 'msg', d: m.d });
    }
  });
  ws.on('close', () => {
    if (!ws.room) return;
    const r = rooms.get(ws.room); if (!r) return;
    if (r[ws.role] === ws) r[ws.role] = null;
    presence(ws.room);
  });
});
setInterval(() => { wss.clients.forEach(ws => { if (!ws.alive) return ws.terminate(); ws.alive = false; try { ws.ping(); } catch (e) {} }); for (const [c, v] of codes) if (Date.now() > v.expires) codes.delete(c); }, 25000);

/* ---------- auto-update (personal version) ---------- */
// Every few hours the computer checks the site for a newer build of the app (public/) and swaps the files in place.
// Only public/ is updated; server.js, data/ and the start scripts are never touched. NO_UPDATE=1 turns this off.
const https = require('https');
const UPDATE_URL = process.env.UPDATE_URL || 'https://nivrhdrums.github.io/chartready/c40b604d/local/';
const ULOG = path.join(path.dirname(DATA), 'update.log');
function ulog(s) { console.log('[update] ' + s); try { fs.mkdirSync(path.dirname(ULOG), { recursive: true }); fs.appendFileSync(ULOG, new Date().toISOString() + ' ' + s + '\n'); } catch (e) {} }
function fetchBuf(url, hops = 0) {
  return new Promise((ok, no) => {
    const r = https.get(url + (url.includes('?') ? '&' : '?') + 't=' + Date.now(), { headers: { 'cache-control': 'no-cache', 'user-agent': 'ChartReady-local' }, timeout: 30000 }, res => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && hops < 5) { res.resume(); return fetchBuf(new URL(res.headers.location, url).href, hops + 1).then(ok, no); }
      if (res.statusCode !== 200) { res.resume(); return no(new Error('HTTP ' + res.statusCode)); }
      const b = []; res.on('data', c => b.push(c)); res.on('end', () => ok(Buffer.concat(b))); res.on('error', no);
    });
    r.on('timeout', () => r.destroy(new Error('timeout'))); r.on('error', no);
  });
}
const localVer = () => { try { return (fs.readFileSync(path.join(PUBLIC, 'sw.js'), 'utf8').match(/chartready-(\d+\.\d+\.\d+)/) || [])[1] || '0.0.0'; } catch (e) { return '0.0.0'; } };
const isNewer = (a, b) => { const x = a.split('.').map(Number), y = b.split('.').map(Number); for (let i = 0; i < 3; i++) if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) > (y[i] || 0); return false; };
let updating = false, lastErr = '';
async function checkUpdate() {
  if (updating || process.env.NO_UPDATE === '1') return; updating = true;
  try {
    const man = JSON.parse((await fetchBuf(UPDATE_URL + 'version.json')).toString('utf8'));
    const cur = localVer();
    if (!man.v || !Array.isArray(man.files) || !isNewer(String(man.v), cur)) { lastErr = ''; return; }
    const got = [];
    for (const f of man.files) {
      if (!/^[\w.-]+$/.test(f.name || '')) throw new Error('bad file name');
      const buf = await fetchBuf(UPDATE_URL + f.name);
      if (f.size && buf.length !== f.size) throw new Error('size mismatch ' + f.name);
      if (f.sha256 && crypto.createHash('sha256').update(buf).digest('hex') !== f.sha256) throw new Error('hash mismatch ' + f.name);
      got.push([f.name, buf]);
    }
    // sw.js carries the version mark, so it goes last: a half-finished update is simply retried next time
    got.sort((a, b) => (a[0] === 'sw.js') - (b[0] === 'sw.js'));
    for (const [name, buf] of got) { const dst = path.join(PUBLIC, name), tmp = dst + '.new'; fs.writeFileSync(tmp, buf); fs.renameSync(tmp, dst); }
    lastErr = ''; ulog(`updated ${cur} -> ${man.v}`);
  } catch (e) { if (e.message !== lastErr) ulog('check failed: ' + e.message); lastErr = e.message; }
  finally { updating = false; }
}
if (LOCAL) { setTimeout(checkUpdate, 5000); setInterval(checkUpdate, 3 * 60 * 60 * 1000); }

server.listen(PORT, () => {
  // the stop script uses this to find the process
  const PIDF = path.join(path.dirname(DATA), 'server.pid');
  try { fs.mkdirSync(path.dirname(PIDF), { recursive: true }); fs.writeFileSync(PIDF, String(process.pid)); } catch (e) {}
  const bye = () => { try { if (fs.readFileSync(PIDF, 'utf8').trim() === String(process.pid)) fs.unlinkSync(PIDF); } catch (e) {} };
  process.on('exit', bye); process.on('SIGINT', () => process.exit(0)); process.on('SIGTERM', () => process.exit(0));
  console.log(`\n  ChartReady is running:  http://localhost:${PORT}`);
  if (LOCAL) lanIPs().forEach(ip => console.log(`  From your phone (same WiFi):  http://${ip}:${PORT}`));
  console.log('\n  Keep this running. Close it = ChartReady stops.\n');
});
