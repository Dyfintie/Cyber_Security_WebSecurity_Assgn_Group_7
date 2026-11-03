# CSRF: GET-Based Forged Action

**Variant 1.** The Northstar Employee Portal demonstrates how a state-changing `GET` request can be forged from attacker-controlled content, then shows a POST plus CSRF-token mitigation.

See the [group README](../README.md) for team ownership and assignment context.

## Run locally

Requires Node.js and npm. From the repository root:

```powershell
cd csrf-get-variant_1
npm start
```

Open the portal at `http://localhost:3000/login` and the attacker origin at `http://localhost:4000/attacker.html`.

Use the demo credentials:

```text
Username: alice
Password: password123
```

The application state is held in memory and resets when the server restarts.

## Vulnerable implementation and root cause (a, c)

The vulnerable handler is in [`server.js`](server.js):

```javascript
if (url.pathname === '/profile/update-email' && req.method === 'GET') {
  user.email = url.searchParams.get('email') || user.email;
  return redirect(res, '/');
}
```

The endpoint changes Alice's account email using GET. A browser can send this request because of an image, link, redirect, or other attacker-controlled content. If Alice is logged in, the browser automatically includes her session cookie. The server trusts the cookie for authentication but does not verify that Alice intended the action.

## Exploit and verification (b, d)

1. Open `http://localhost:3000/login` and sign in as `alice / password123`.
2. Open `http://localhost:4000/attacker.html` in another tab.
3. Click **Fire forged GET request**. The attacker page creates this request:

   ```html
   <img src="http://localhost:3000/profile/update-email?email=attacker@evil.test">
   ```

4. Return to the portal and refresh it. The email becomes `attacker@evil.test`, with a message explaining that the value was changed by a GET request.

The attacker page does not need to read the response. It only needs the victim's browser to send the authenticated request.

## Implemented mitigation (d)

The same portal includes a protected form using POST and a session-bound CSRF token:

```javascript
if (url.pathname === '/profile/update-email' && req.method === 'POST') {
  if (body.get('csrf') !== session.csrfToken) return send(res, 403, ...);
  user.email = body.get('email') || user.email;
}
```

Use **Update with CSRF token** on the portal to verify the safe flow. A request with an invalid token returns HTTP 403.

## Other mitigations (e)

- Keep GET requests safe and idempotent; use POST or another appropriate method for state changes.
- Validate an unpredictable synchronizer token bound to the authenticated session.
- Set session cookies with an appropriate `SameSite` policy as defense in depth.
- Validate `Origin` or `Referer` where suitable, without relying on those headers as the only control.
- Require re-authentication or an OTP for especially sensitive account changes.
