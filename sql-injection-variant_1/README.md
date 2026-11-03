# SQL Injection: Authentication Bypass

**Variant 1.** An employee portal demonstrates how SQL injection bypasses authentication and how parameter binding blocks the same payload. See the [group README](../README.md) for ownership and submission details.

The application uses Node.js, Express, and an in-memory SQLite database through `sql.js`. The database is seeded on startup and resets whenever the server restarts; no separate database server is needed.

## Run locally

Requires Node.js and npm. From the repository root, in PowerShell:

```powershell
cd sql-injection-variant_1
npm ci
$env:SECURE_MODE = "false"
npm start
```

Open http://localhost:3000. The login page displays the current mode and the query used for each login attempt.

To enable the parameterised query, stop the server with **Ctrl+C**, then restart it:

```powershell
$env:SECURE_MODE = "true"
npm start
```

In Bash, use `SECURE_MODE=false npm start` or `SECURE_MODE=true npm start`. The mode is read at startup; changing it requires a server restart.

A valid baseline login is username `admin`, password `SuperSecret@123`. The seeded accounts are defined in [`db.js`](db.js). Password storage and query display are simplified for the lab.

## Vulnerable implementation and root cause (a, c)

The vulnerable branch of `POST /login` in [`server.js`](server.js) constructs SQL directly from the submitted username and password:

```javascript
const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
const rows = db.exec(query);
```

Input is parsed as SQL syntax because it is inserted into the query text. A closing quote and SQL comment can remove the password condition, so the application authenticates a user without checking their password.

## Exploit and verification (b, d)

Use this exact payload:

| Field | Value |
| --- | --- |
| Username | `admin' --` |
| Password | `anything` |

The vulnerable query becomes:

```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = 'anything'
```

The quote closes the username value, and `--` comments out the password check.

1. In **Vulnerable** mode, try `admin` / `anything` first and confirm the incorrect password is rejected.
2. Submit `admin' --` / `anything`. Expect a successful admin login and a redirect to the dashboard.
3. Sign out, stop the server, and restart with `SECURE_MODE` set to `true` using the commands above.
4. Resubmit `admin' --` / `anything`. Expect `Invalid username or password.` and no authenticated session.
5. Confirm that `admin` / `SuperSecret@123` still succeeds in the parameterised mode.

Failed credentials return HTTP 200 with `success: false` in this demo. Capture the successful bypass and a screenshot of the rejected attempt for the submission.

## Implemented mitigation (d)

The parameterised branch in [`server.js`](server.js) prepares a fixed query and binds the credentials separately:

```javascript
const query = 'SELECT * FROM users WHERE username = ? AND password = ?';
const stmt = db.prepare(query);
stmt.bind([username, password]);
while (stmt.step()) {
  user = stmt.getAsObject();
}
stmt.free();
```

SQLite treats `admin' --` as a literal username. The quote and comment characters cannot alter the query structure, and no seeded account matches that username.

## Other mitigations (e)

Allow-list validation limits usernames to the application's expected format. Least-privilege database access limits the damage a compromised query can cause, while generic client-facing errors avoid revealing database internals. These supplement parameterised queries; the implemented fix in this project is parameter binding.
