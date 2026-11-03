// ──────────────────────────────────────────────────────────────
// server.js — Express server for the SQL Injection Auth Bypass demo
//
// MODE SELECTION:
//   By default, the server runs in VULNERABLE mode (SECURE_MODE=false).
//   To start in SECURE mode (parameterised queries):
//     PowerShell:  $env:SECURE_MODE="true"; npm start
//     CMD:         set SECURE_MODE=true && npm start
//     Linux/macOS: SECURE_MODE=true npm start
// ──────────────────────────────────────────────────────────────

const express = require('express');
const session = require('express-session');
const path = require('path');
const { initDatabase } = require('./db');

const app = express();
const PORT = 3000;
const isSecure = process.env.SECURE_MODE === 'true';

// ── Middleware ────────────────────────────────────────────────
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use(
  session({
    secret: 'cybersec-lab5-secret',
    resave: false,
    saveUninitialized: false,
  })
);

// ── Start server after async DB init ─────────────────────────
(async () => {
  const db = await initDatabase();

  // ── Serve the login page ─────────────────────────────────
  app.get('/', (_req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'login.html'));
  });

  // ── Check current security mode ──────────────────────────
  app.get('/api/mode', (_req, res) => {
    res.json({
      secure: isSecure,
      mode: isSecure ? 'secure' : 'vulnerable',
    });
  });

  // ────────────────────────────────────────────────────────────
  // POST /login — The login route
  //
  // *** VULNERABILITY: SQL Injection — Authentication Bypass ***
  //
  // ROOT CAUSE (item c):
  //   User-supplied values (username & password) are directly
  //   concatenated into the SQL query string.  An attacker can
  //   inject SQL syntax to alter the query logic so that it
  //   always returns a row, bypassing authentication without
  //   knowing a valid password.
  //
  // EXPLOIT PAYLOAD (item b):
  //   Username: admin' --
  //   Password: anything
  //
  //   The resulting query becomes:
  //     SELECT * FROM users
  //      WHERE username = 'admin' --' AND password = 'anything'
  //
  //   Everything after -- is a SQL comment, so the password
  //   check is completely ignored.
  //
  //   Alternative payload (bypass without knowing any username):
  //     Username: ' OR 1=1 --
  //     Password: anything
  // ────────────────────────────────────────────────────────────
  app.post('/login', (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
      return res.status(400).json({
        success: false,
        message: 'Username and password are required.',
      });
    }

    try {
      let user = null;
      let executedQuery = '';

      if (!isSecure) {
        // ╔═══════════════════════════════════════════════════════╗
        // ║  🔓  VULNERABLE CODE  (item a)                       ║
        // ║  String concatenation — open to SQL injection         ║
        // ╚═══════════════════════════════════════════════════════╝
        const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
        executedQuery = query;
        console.log('[VULNERABLE] Executing concatenated query:', query);
        const rows = db.exec(query);
        if (rows.length > 0 && rows[0].values.length > 0) {
          const cols = rows[0].columns;
          const vals = rows[0].values[0];
          user = {};
          cols.forEach((col, i) => { user[col] = vals[i]; });
        }
      } else {
        // ╔═══════════════════════════════════════════════════════╗
        // ║  🔒  FIX: Parameterised / prepared statement (item d) ║
        // ║  The ? placeholders ensure that user input is always  ║
        // ║  treated as DATA, never as SQL syntax.  The same      ║
        // ║  injection payload is now compared literally against   ║
        // ║  the username column and will not match any row.       ║
        // ╚═══════════════════════════════════════════════════════╝
        const query = 'SELECT * FROM users WHERE username = ? AND password = ?';
        executedQuery = `${query}  [Bound: ? = '${username}', ? = '${password}']`;
        const stmt = db.prepare(query);
        stmt.bind([username, password]);
        while (stmt.step()) {
          user = stmt.getAsObject();
        }
        stmt.free();
        console.log('[SECURE] Executing parameterised query with bound params:', [username, password]);
      }

      if (user) {
        req.session.user = {
          id: user.id,
          username: user.username,
          role: user.role,
          email: user.email,
        };
        return res.json({
          success: true,
          mode: isSecure ? 'secure' : 'vulnerable',
          query: executedQuery,
          message: `Welcome, ${user.username}! (role: ${user.role})`,
          user: { username: user.username, role: user.role, email: user.email },
        });
      } else {
        return res.json({
          success: false,
          mode: isSecure ? 'secure' : 'vulnerable',
          query: executedQuery,
          message: 'Invalid username or password.',
        });
      }
    } catch (err) {
      console.error('[ERROR]', err.message);
      return res.status(500).json({
        success: false,
        message: `Server error: ${err.message}`,
      });
    }
  });

  // ── Dashboard (post-login) ────────────────────────────────
  app.get('/dashboard', (req, res) => {
    if (!req.session.user) {
      return res.redirect('/');
    }
    res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
  });

  app.get('/api/me', (req, res) => {
    if (!req.session.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    res.json(req.session.user);
  });

  // ── Logout ────────────────────────────────────────────────
  app.post('/logout', (req, res) => {
    req.session.destroy();
    res.json({ success: true });
  });

  // ── Start ─────────────────────────────────────────────────
  app.listen(PORT, () => {
    console.log(`\n🚀  Server running at  http://localhost:${PORT}`);
    console.log(`   Mode: ${isSecure ? '🔒 SECURE (parameterised queries)' : '🔓 VULNERABLE (SQL concatenation)'}\n`);
  });
})();
