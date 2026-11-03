# NimbusBank — CSRF Demonstration (POST-based forged action, auto-submitting form)

**Course:** Cyber Security (IT-30001) · **Assignment:** Web Server Security · **Category:** Cross-Site Request Forgery (CSRF) · **Variant:** POST-based forged action (auto-submitting form)

A deliberately vulnerable mini banking app plus an attacker-owned web page that silently drains the victim's account. **The bank ships in the compromised state: the anti-CSRF fix is present but commented out inside the source — uncomment it to secure the site.**

---

## 1. Quick start

```bash
cd csrf-post
./run.sh        # starts both servers; bank runs VULNERABLE (the shipped state)
```

| URL | What it is |
|---|---|
| `http://localhost:3000` | **NimbusBank** (victim app). Log in as `alice / nimbus123` (balance ₹50,000) or `attacker / evil123` |
| `http://localhost:3001` | **Attacker page** — looks like an innocent "NimbusPerks weekly deals" shopping page. The silent attack fires on page load |
| `http://localhost:3001/visible` | The **same auto-submitting attack made visible** — the hidden-showing form and the normally-invisible iframe are drawn on screen and fire on page load (no button); the bank's reply (success dashboard or the blocked 403 page) renders live in the frame |

First run creates a local `.venv` and installs Flask automatically (`pip install flask` manually if you prefer).

## 2. Two-minute video demo script

1. `./run.sh` → open `localhost:3000`, log in as **alice**, show the balance: **₹50,000.00**.
2. Transfer ₹1,000 normally from the dashboard → works fine (the app itself is functional).
3. Show the **vulnerable code path** in `bank/app.py` → `POST /transfer` (search for `⚠️ VULNERABLE CODE PATH`): the only proof of intent is the session cookie — and scroll past the comment labelled `🔧 THE FIX` to show it is deliberately commented out.
4. Open a new tab → `localhost:3001`. The page is a normal-looking shopping site; nothing visibly happens. **The hidden auto-submitting form has already fired** — a cross-site `POST /transfer` with `to_account=666600000000` and `amount=35000`. The victim's browser attached her session cookie (the cookie is `SameSite=None`), so the bank executed it *as Alice*. The response is swallowed by a hidden iframe, so the victim never sees anything.
5. Switch back to the bank tab, refresh → balance now **₹15,000.00**. Log in as `attacker / evil123` if you want to see the ₹35,000 received.
6. **Mitigation, demonstrated live:** stop the bank, **uncomment the `🔧 THE FIX` block** inside `POST /transfer` in `bank/app.py` (and set `protect=True` in the `dashboard()` route so the green "ACTIVE" badge is honest), rerun `./run.sh`, log in as alice again, and fire the **exact same payload** (open `localhost:3001`, or its `/visible` page for the on-screen version) → the bank answers **HTTP 403 — Request blocked**, while a normal in-app transfer (which carries the token from the dashboard form) still succeeds.

## 3. Assignment mapping

| Table-2 item | Where |
|---|---|
| (a) Vulnerable implementation | `bank/app.py` → `POST /transfer`, marked `⚠️ VULNERABLE CODE PATH — CSRF (POST-based forged action)` |
| (b) Working exploit | `attacker/app.py` → the auto-submitting hidden `<form method="POST" action="http://localhost:3000/transfer">` + hidden iframe that swallows the response |
| (c) Root cause | `POST /transfer` changes account state based **only on ambient credentials** — the session cookie the browser attaches to every request to the bank, including forged ones. A state-changing request is accepted **without proof of intent**; nothing links the request to the page the user actually saw. |
| (d) Mitigation implemented | Synchronizer (anti-CSRF) token, present in the source but **commented out** so the app ships compromised. Inside `bank/app.py` → `POST /transfer`, under `🔧 THE FIX`, uncomment the block: a random `secrets.token_hex(16)` value minted per session (`/login`) and embedded in the dashboard transfer form is then verified with `secrets.compare_digest`. Missing/incorrect token → `403 blocked.html`. Forged requests cannot know the token (the browser's same-origin policy keeps attacker JS from reading the bank's pages), so the same payload now fails — screenshot from `/visible`. |
| (e) Other mitigations (theory) | See §4. |
| State-changing GET | N/A — the transfer is already POST-only (`GET /transfer` is not routed), avoiding the separate "GET-based forged action" variant. |

### Code map

```
csrf-post/
├── bank/
│   ├── app.py                  # vulnerable Flask app, port 3000
│   ├── templates/              # base / login / dashboard / blocked(403)
│   └── static/style.css
├── attacker/
│   └── app.py                  # attacker pages, port 3001 (silent + /visible evidence)
└── run.sh                      # starts both servers
```

## 4. Other mitigations for CSRF (theory — part e)

- **SameSite cookies.** Cookies marked `SameSite=Lax` (or `Strict`) are *not* attached to cross-site requests — `Lax` preserves them only on ordinary top-level navigations, not on a hostile form POST. The `hit-frame` iframe POST from `localhost:3001` would then reach the bank *without* Alice's session and be rejected as unauthenticated. (Modern browsers actually apply `Lax` by default; this demo deliberately declares `SameSite=None` so the exploit works, and the app comments call this out.) Deployment note: site owners should set `SameSite` explicitly rather than relying on browser defaults.
- **Synchronizer tokens (implemented here).** Since the attack rides on the cookie, the server demands additional per-session proof that the request passed through the bank's own HTML. The token bound to the session is one avenue; binding an **encrypted value of the user's session id** inside the form (double-submit/hashed-token variants) is another family member. All reject one-time forged requests because the attacker cannot read that value across origins.
- **Re-authentication for sensitive actions.** For high-impact operations (payment confirmation, password/email change) require the password or an OTP again. Even a perfectly forged POST carries no proof of *knowledge of the secret credential*, so the action stalls until the human re-authenticates — the strongest defence for irreversible operations, at the cost of friction (why it's reserved for high-value actions).
- **Avoiding state-changing GETs.** GETs pre-date the token era and are easily forged by `<img src="...">`/link embeds as well. A strict POST-only policy for state changes (as `POST /transfer` already is) keeps every mutation behind a channel where anti-CSRF defences can be enforced at all: `GET /transfer` is not even routed.
- **(+ request-side checks, defense in depth).** Origin/Referer header validation would also have rejected this exact payload; note that Referer can be absent or stripped, so it's best combined with tokens, not used alone.
