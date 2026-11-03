// ──────────────────────────────────────────────────────────────
// db.js — Initialises an in-memory SQLite database with seed data
//         using sql.js (pure JS, no native compilation needed).
// ──────────────────────────────────────────────────────────────

const initSqlJs = require('sql.js');

async function initDatabase() {
  const SQL = await initSqlJs();
  const db = new SQL.Database(); // in-memory

  // Create the users table
  db.run(`
    CREATE TABLE IF NOT EXISTS users (
      id       INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT    NOT NULL UNIQUE,
      password TEXT    NOT NULL,
      role     TEXT    NOT NULL DEFAULT 'user',
      email    TEXT
    );
  `);

  // Seed some demo users
  const insert = db.prepare(
    'INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)'
  );

  const seedUsers = [
    ['admin',   'SuperSecret@123',  'admin', 'admin@iiita.ac.in'],
    ['alice',   'alice_pass',        'user',  'alice@iiita.ac.in'],
    ['bob',     'bob_pass',          'user',  'bob@iiita.ac.in'],
    ['charlie', 'charlie_pass',      'user',  'charlie@iiita.ac.in'],
  ];

  for (const u of seedUsers) {
    insert.bind(u);
    insert.step();
    insert.reset();
  }
  insert.free();

  console.log('[db] In-memory database initialised with 4 users.');
  return db;
}

module.exports = { initDatabase };
