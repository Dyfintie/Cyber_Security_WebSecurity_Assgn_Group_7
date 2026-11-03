const http = require('http');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const APP_PORT = Number(process.env.APP_PORT || 3000);
const ATTACKER_PORT = Number(process.env.ATTACKER_PORT || 4000);
const publicDir = path.join(__dirname, 'public');
const sessions = new Map();

const user = {
  username: 'alice',
  password: 'password123',
  email: 'alice@company.test',
};

function send(res, status, body, type = 'text/html; charset=utf-8', headers = {}) {
  res.writeHead(status, { 'Content-Type': type, ...headers });
  res.end(body);
}

function redirect(res, location, headers = {}) {
  res.writeHead(302, { Location: location, ...headers });
  res.end();
}

function cookieValue(req, name) {
  const cookie = req.headers.cookie || '';
  const match = cookie.split(';').map((item) => item.trim()).find((item) => item.startsWith(`${name}=`));
  return match ? decodeURIComponent(match.slice(name.length + 1)) : null;
}

function sessionFor(req) {
  const id = cookieValue(req, 'sid');
  return id ? sessions.get(id) : null;
}

function newSession() {
  const id = crypto.randomBytes(18).toString('hex');
  const csrfToken = crypto.randomBytes(18).toString('hex');
  const session = { id, csrfToken, username: user.username };
  sessions.set(id, session);
  return session;
}

function parseBody(req) {
  return new Promise((resolve) => {
    let body = '';
    req.on('data', (chunk) => { body += chunk; });
    req.on('end', () => resolve(new URLSearchParams(body)));
  });
}

function pageShell(title, content, active = 'portal') {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${title}</title><link rel="stylesheet" href="/styles.css"></head>
<body><div class="glow glow-a"></div><div class="glow glow-b"></div>
<header class="topbar"><a class="brand" href="http://localhost:${APP_PORT}/"><span class="brand-mark">✦</span><span>Northstar <b>Employee Portal</b></span></a>
<nav><a class="${active === 'portal' ? 'active' : ''}" href="http://localhost:${APP_PORT}/">Portal</a><a href="http://localhost:${ATTACKER_PORT}/attacker.html">Attack lab</a><a href="http://localhost:${APP_PORT}/about.html">About CSRF</a></nav>
<span class="status"><i></i> demo environment</span></header>
<main class="page">${content}</main><footer>Training application · intentionally vulnerable · run locally only</footer>
</body></html>`;
}

function loginPage(message = '') {
  return pageShell('Sign in · Northstar', `<section class="auth-card">
    <div class="eyebrow">NORTHSTAR / INTERNAL</div><h1>Employee Portal</h1><p class="muted">Sign in to manage your employee profile.</p>
    ${message ? `<div class="alert danger">${message}</div>` : ''}
    <form method="post" action="/login" class="stack"><label>Username<input name="username" value="alice" autocomplete="username"></label>
    <label>Password<input name="password" type="password" value="password123" autocomplete="current-password"></label>
    <button class="button primary" type="submit">Sign in <span>→</span></button></form>
    <div class="hint"><span>Demo credentials</span><code>alice / password123</code></div>
  </section>`);
}

function portalPage(session, notice = '') {
  return pageShell('Profile · Northstar', `<section class="hero"><div><div class="eyebrow">AUTHENTICATED SESSION</div><h1>Welcome back, Alice</h1><p class="muted">Manage your employee profile and security settings.</p></div><span class="pill green">● signed in</span></section>
  ${notice ? `<div class="alert ${notice.type}">${notice.text}</div>` : ''}
  <div class="grid two"><article class="card profile-card"><div class="card-head"><span class="icon violet">◎</span><div><h2>Profile details</h2><p class="muted">Personal information on file</p></div></div>
    <div class="data-row"><span>Employee</span><strong>Alice Johnson</strong></div><div class="data-row"><span>Department</span><strong>Finance</strong></div><div class="data-row"><span>Email</span><strong class="email-value">${user.email}</strong></div>
  </article><article class="card"><div class="card-head"><span class="icon amber">⚿</span><div><h2>Security</h2><p class="muted">Keep your account protected</p></div></div>
    <div class="security-line"><span class="check">✓</span><span><b>Password</b><small>Last changed 21 days ago</small></span><span class="pill green">strong</span></div>
    <div class="security-line"><span class="check">✓</span><span><b>Session</b><small>Cookie-based authentication</small></span><span class="pill yellow">active</span></div>
  </article></div>
  <section class="card action-card"><div class="card-head"><span class="icon cyan">✎</span><div><h2>Change email address</h2><p class="muted">The first link is intentionally vulnerable for this lesson.</p></div></div>
    <div class="warning-box"><b>⚠ Vulnerable endpoint</b><code>GET /profile/update-email?email=...</code><span>State-changing actions must not be performed with GET.</span></div>
    <a class="button danger-button" href="/profile/update-email?email=alice.new@company.test">Test GET update</a>
    <form method="post" action="/profile/update-email" class="safe-form"><input type="hidden" name="csrf" value="${session.csrfToken}"><label>Safe POST update<input type="email" name="email" value="alice.safe@company.test"></label><button class="button secondary" type="submit">Update with CSRF token</button></form>
  </section>
  <section class="callout"><span class="callout-number">01</span><div><b>What to watch</b><p>Open <a href="http://localhost:${ATTACKER_PORT}/attacker.html">Attack lab</a> in another tab. The attacker page sends a GET request while this session is signed in.</p></div></section>`);
}

function attackerPage() {
  return pageShell('Attack lab · Northstar', `<section class="hero"><div><div class="eyebrow">SIMULATED ATTACK ORIGIN</div><h1>CSRF Attack Lab</h1><p class="muted">This page represents content controlled by an attacker.</p></div><span class="pill red">● attacker page</span></section>
  <div class="attack-layout"><article class="card attack-card"><div class="terminal-head"><span class="traffic"><i></i><i></i><i></i></span><span>attacker.example / lure.html</span><span>HTML</span></div>
    <div class="code"><span class="comment">&lt;!-- disguised as an image request --&gt;</span><br><span class="tag">&lt;img</span> <span class="attr">src</span>=<span class="string">"http://localhost:3000/profile/update-email?email=attacker@evil.test"</span><span class="tag">&gt;</span><br><span class="comment">&lt;!-- the browser sends Alice's cookie automatically --&gt;</span></div>
    <div class="attack-controls"><button id="fire" class="button danger-button">Fire forged GET request <span>↗</span></button><span id="result" class="muted">Waiting to fire…</span></div>
  </article><article class="card explanation"><div class="eyebrow">WHY IT WORKS</div><h2>Implicit trust in cookies</h2><ol><li><b>Alice is logged in.</b><small>The browser stores the session cookie.</small></li><li><b>She visits attacker content.</b><small>The page embeds a state-changing URL.</small></li><li><b>The browser sends the cookie.</b><small>The server mistakes the forged request for Alice's action.</small></li></ol></article></div>
  <div class="alert warning"><b>Training note:</b> this is a local, intentionally vulnerable demonstration. Do not reuse the endpoint in a real application.</div>
  <script>document.getElementById('fire').addEventListener('click',()=>{const i=new Image();i.src='http://localhost:${APP_PORT}/profile/update-email?email=attacker@evil.test';document.getElementById('result').textContent='Request sent — return to Portal to observe the changed email.';document.getElementById('result').className='success-text';});</script>`,'attacker');
}

function aboutPage() {
  return pageShell('About CSRF · Northstar', `<section class="hero"><div><div class="eyebrow">SECURITY CONCEPT</div><h1>CSRF in one minute</h1><p class="muted">Cross-Site Request Forgery tricks a browser into sending an authenticated request the user did not intend.</p></div></section>
  <div class="grid two"><article class="card"><div class="eyebrow red-text">VULNERABLE</div><h2>GET changes state</h2><pre><code>app.get('/profile/update-email', (req, res) =&gt; {
  user.email = req.query.email;
  res.redirect('/');
});</code></pre><p class="muted">A GET should be safe and idempotent. Here it changes the account, so any image, link, or redirect can trigger it.</p></article>
  <article class="card"><div class="eyebrow green-text">MITIGATED</div><h2>POST + CSRF token</h2><pre><code>app.post('/profile/update-email', (req, res) =&gt; {
  if (req.body.csrf !== session.csrfToken) {
    return res.status(403).end();
  }
  user.email = req.body.email;
});</code></pre><p class="muted">Use POST for state changes, validate an unpredictable token, and consider SameSite cookies as defense in depth.</p></article></div>
  <section class="callout"><span class="callout-number">02</span><div><b>Key takeaway</b><p>Authentication proves who sent the request. CSRF protection proves the request was intentionally made by your application.</p></div></section>`,'about');
}

function staticFile(res, file) {
  const ext = path.extname(file);
  const type = ext === '.css' ? 'text/css; charset=utf-8' : 'application/octet-stream';
  fs.readFile(path.join(publicDir, file), (err, data) => err ? send(res, 404, 'Not found', 'text/plain') : send(res, 200, data, type));
}

function appRequest(req, res) {
  const url = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (url.pathname === '/styles.css') return staticFile(res, 'styles.css');
  if (url.pathname === '/attacker.html') return send(res, 200, attackerPage());
  if (url.pathname === '/about.html') return send(res, 200, aboutPage());
  if (url.pathname === '/login' && req.method === 'GET') return send(res, 200, loginPage());
  if (url.pathname === '/login' && req.method === 'POST') return parseBody(req).then((body) => {
    if (body.get('username') !== user.username || body.get('password') !== user.password) return send(res, 401, loginPage('Invalid demo credentials.'));
    const session = newSession();
    return redirect(res, '/', { 'Set-Cookie': `sid=${session.id}; HttpOnly; Path=/` });
  });

  const session = sessionFor(req);
  if (!session) return redirect(res, '/login');
  if (url.pathname === '/' && req.method === 'GET') {
    const notice = url.searchParams.get('notice') === 'updated'
      ? { type: 'danger', text: `Email changed by a GET request. Previous value: ${url.searchParams.get('from') || 'unknown'}` }
      : url.searchParams.get('notice') === 'safe'
        ? { type: 'success', text: 'Email updated with POST + a valid CSRF token.' }
        : '';
    return send(res, 200, portalPage(session, notice));
  }
  if (url.pathname === '/profile/update-email' && req.method === 'GET') {
    const previous = user.email;
    user.email = url.searchParams.get('email') || user.email;
    return redirect(res, `/?notice=updated&from=${encodeURIComponent(previous)}`);
  }
  if (url.pathname === '/profile/update-email' && req.method === 'POST') return parseBody(req).then((body) => {
    if (body.get('csrf') !== session.csrfToken) return send(res, 403, pageShell('Blocked · Northstar', '<section class="auth-card"><div class="eyebrow red-text">403 / BLOCKED</div><h1>CSRF token rejected</h1><p class="muted">The request did not contain the session-bound token expected by the server.</p><a class="button primary" href="/">Return to portal</a></section>'));
    user.email = body.get('email') || user.email;
    return redirect(res, '/?notice=safe');
  });
  return send(res, 404, 'Not found', 'text/plain');
}

function start() {
  const app = http.createServer(appRequest);
  const attacker = http.createServer((req, res) => {
    if (req.url === '/styles.css') return staticFile(res, 'styles.css');
    if (req.url === '/' || req.url === '/attacker.html') return send(res, 200, attackerPage());
    return send(res, 404, 'Not found', 'text/plain');
  });
  app.listen(APP_PORT, 'localhost', () => console.log(`Employee Portal: http://localhost:${APP_PORT}`));
  attacker.listen(ATTACKER_PORT, 'localhost', () => console.log(`Attacker origin: http://localhost:${ATTACKER_PORT}`));
}

start();
