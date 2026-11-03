# 🎬 4-Minute Video Script + Final Audit
## Reflected XSS · Aman · IT-30001 · IIIT Allahabad

---

## ✅ Final Audit — What You Have to Show

> [!IMPORTANT]
> These are the **5 graded criteria** from the assignment (Table 2a–e). Every point is fully implemented. Tick each off while recording.

| # | Criterion | What's in the app | Where on screen |
|---|-----------|-------------------|-----------------|
| **2a** | Vulnerable Implementation | `app.py` route reads `?q=` and passes it raw; template uses `\| safe` | **Vulnerable page → "Flawed Code" panel** (bottom-left) |
| **2b** | Working Exploit | 4 clickable payloads — alert, cookie theft, `onerror` bypass, defacement | **Vulnerable page → payload list** (right column) |
| **2c** | Root Cause | Explained in code panel: "unencoded GET param echoed into HTML stream" | **Vulnerable page → "Flawed Code" panel** (bottom text) |
| **2d** | Implemented Mitigation | Template without `\| safe`; wire HTML box shows `&lt;` encoding | **Mitigated page → "The Fix" panel + Wire HTML box** |
| **2e** | Theoretical Mitigations | CSP, HttpOnly, DOMPurify, safe DOM sinks listed with code | **Mitigated page → "Other Mitigations" panel** (right column) |

---

## 🛠 Before You Hit Record

```bash
# Terminal — start the server
cd /Users/amankashyap/Documents/cyber-sec
python3 app.py
```

**Browser setup:**
1. Open **`http://127.0.0.1:5000`** — confirm dashboard loads
2. Open **DevTools** (F12) → Application tab → Cookies → `127.0.0.1`
   - Confirm `session_token = IIITA_SEC_TOKEN_...` is there
3. Zoom browser to **120%** (Cmd + twice) so text is readable in recording
4. Put DevTools in a **side panel** (not bottom), so cookies stay visible
5. Click **↺ Reset Cookie** in navbar to get a fresh token value

---

## 🎙 4-Minute Script

---

### SCENE 1 — Introduction & Dashboard `(0:00 – 0:35)`

**Show:** Home page `http://127.0.0.1:5000` — let the camera breathe on it for 3–4 seconds.

> *"Hi, I'm Aman. This video demonstrates **Reflected Cross-Site Scripting**, which is my assigned variant — Category 3, Variant 2 — for the Web Server Security assignment at IIIT Allahabad under Dr. Soumyadev Maity.*
>
> *I've built a Flask web application with two versions of the same product-search feature — one that is intentionally vulnerable and one that is properly fixed. You can see both options on the home page. Let me start with the vulnerable one."*

**Action:** Click **⚠ Vulnerable Endpoint** button.

---

### SCENE 2 — What the Victim Sees (the App) `(0:35 – 1:05)`

**Show:** Vulnerable page loads. Point to left column.

> *"This looks like a normal e-commerce product search page. A user types a query, hits Search, and the server reflects that search term back in the response — 'Search results for: your query here'.*
>
> *This is exactly the pattern that Reflected XSS attacks exploit. The user's input goes into the URL query string... the server puts it straight into the HTML page... and the browser renders it. Let me show you the flawed code first before running the attack."*

**Action:** Point to the **"Flawed Code (Table 2a)"** panel at the bottom-left. Hover cursor over the red `| safe` text.

> *"In `app.py`, the query parameter is read with `request.args.get('q')` and passed directly to the template with no sanitization. In the template, the Jinja2 filter `| safe` explicitly disables automatic escaping. This is the vulnerability — this one filter is what allows the attack."*

---

### SCENE 3 — Run the Basic Alert Exploit `(1:05 – 1:35)`

**Show:** Right column — payload list.

> *"Now the attack. I've pre-built these payload links. Imagine the attacker sends Payload 1 as a phishing link to the victim."*

**Action:** Click **① Basic Alert PoC**. Let the alert box appear. **Pause 3 seconds on the alert.**

> *"The browser just executed JavaScript. The alert popped. This proves that code from the URL is running in the browser's context — not in a sandbox, not in the attacker's machine — inside the victim's own browser session, under this site's origin."*

**Action:** Click OK on the alert.

---

### SCENE 4 — Session Cookie Theft (High Impact) `(1:35 – 2:15)`

> *"That alert was just a proof of concept. Let me show the real impact."*

**Action:** Click **② Session Cookie Theft**. Let alert appear showing the cookie.

> *"Look at that. The alert is displaying `session_token = IIITA_SEC_TOKEN_...` and `user = aman_student`. These are the victim's active session cookies.*
>
> *In a real attack, the script would silently send this to the attacker's server using a `fetch()` request — no alert, completely invisible to the victim. Once the attacker has this token, they can impersonate the user on this site — no password needed."*

**Action:** Click OK, then **switch to DevTools → Application → Cookies** panel.

> *"You can see these cookies right here in the browser. `httponly` is set to false — which is exactly why JavaScript can read them. A proper defence would flip this to `httponly: true`, which I'll mention in the mitigations."*

---

### SCENE 5 — Filter Bypass Payload `(2:15 – 2:40)`

**Action:** Go back to the page. Click **③ img onerror Filter Bypass**.

> *"One more exploit — this one matters for understanding why simple defences fail. This payload uses an `<img>` tag instead of `<script>`. A naive filter that only blocks the word 'script' would miss this entirely.*
>
> *The browser tries to load an image from `src=x`, which obviously fails, and the `onerror` event fires — running our JavaScript. Same result, different tag."*

**Action:** Click OK on the alert.

---

### SCENE 6 — Switch to Mitigated, Show the Fix `(2:40 – 3:20)`

**Action:** Click **✓ Switch to Mitigated →** at top-right.

> *"Now the fixed version. Same application, same route, one change in the template."*

**Action:** Paste this into the search bar manually and click Search:
```
<script>alert(document.cookie)</script>
```

> *"Same payload. No alert. Nothing executed. Let me show you why."*

**Action:** Point to the **"Wire HTML sent to browser"** box that appeared.

> *"This is the actual HTML that the server sent. The angle bracket `<` became the entity `&lt;`, and `>` became `&gt;`. The browser receives these as **character data** — it displays them as literal text on screen, it never interprets them as an HTML tag or a script block.*
>
> *The code change was literally removing two words — `| safe` — from the template. Jinja2 applies escaping by default. That filter was the only thing turning this off."*

**Action:** Scroll down and point to the **"The Fix"** panel showing the before/after diff.

---

### SCENE 7 — Other Mitigations (Table 2e) `(3:20 – 3:55)`

**Action:** Scroll to the **"Other Mitigations — Theory"** panel on the right.

> *"The fix we implemented — output encoding — is the primary defence. But a proper production application uses multiple layers:*
>
> *First, **Content Security Policy** — an HTTP header that tells the browser: only run scripts from trusted sources, block all inline scripts. Even if an attacker injects a `<script>` tag, the browser refuses to run it.*
>
> *Second, **HttpOnly cookies** — we saw the cookies were readable by JavaScript. Setting `HttpOnly` prevents that, so even if XSS runs, the session token can't be stolen.*
>
> *Third, **HTML sanitizers like DOMPurify** — when you genuinely need to accept HTML from users, sanitizers strip dangerous tags while keeping safe ones like bold or italic.*
>
> *And fourth, on the client side, use **safe DOM sinks** — `textContent` instead of `innerHTML` — so JavaScript never parses user input as markup."*

---

### SCENE 8 — Closing `(3:55 – 4:00)`

> *"That's the full demonstration — vulnerable implementation, working exploits, root cause, and mitigations. Thank you."*

---

## 📋 Pause Guide (What to Hold On-Screen)

| Moment | Hold for |
|--------|----------|
| Alert box after Payload 1 | **3 sec** |
| Alert box showing cookie token | **4–5 sec** |
| DevTools showing cookie names | **3 sec** |
| Wire HTML box with `&lt;` encoding | **4 sec** |
| Before/After fix code diff | **3 sec** |

---

## 🚫 Common Mistakes to Avoid

- Don't dismiss alerts immediately — let the viewer read them
- Don't skip the Wire HTML box — it's your clearest visual proof of the fix
- Don't forget to say "root cause" out loud — graders listen for that phrase
- Don't call it "Stored XSS" — it is **Reflected** (non-persistent, URL-delivered)
