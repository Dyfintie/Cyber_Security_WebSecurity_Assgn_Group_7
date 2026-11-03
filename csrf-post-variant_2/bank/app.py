"""
NimbusBank — deliberately vulnerable demo application
Category : Cross-Site Request Forgery (CSRF)
Variant  : POST-based forged action (auto-submitting form)
Course   : Cyber Security (IT-30001) | Assignment: Web Server Security

Run (VULNERABLE — the shipped state):
    python3 bank/app.py        (or ./run.sh from the csrf-post-variant_2/ folder)

HOW TO SECURE IT BY HAND (this is the mitigation the assignment asks for):
    Scroll to the ⚠️ VULNERABLE CODE PATH inside `POST /transfer` below and
    UNCOMMENT the token-check block marked with it. That single edit turns the
    floating comment into real code, and the exact same attacker payload
    (attacker page at http://localhost:3001) is now rejected with HTTP 403.
    COMMENT it back out to fall back to the compromised state.

THE VULNERABILITY
-----------------
`POST /transfer` changes account state (moves money) but verifies only the
session cookie. Browsers attach that cookie automatically to EVERY request
to the bank — including requests a third-party page tricks the browser into
sending. An attacker's page (csrf-post-variant_2/attacker/app.py) can therefore auto-submit
a hidden <form method="POST"> targeting http://localhost:3000/transfer and
the browser will dutifully attach the victim's session cookie and drain
their account.
"""

import secrets
import threading
from datetime import datetime
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # per-process signing key

# The session cookie is declared `SameSite=None; Secure`. On http://localhost
# browsers treat the origin as trustworthy, so the Secure flag is accepted.
# ⚠️ Note for the viva: `SameSite=None` is exactly what lets the cookie ride
# on a cross-site POST. In the real world `SameSite=Lax` (the modern default)
# would suppress the cookie on cross-site POSTs — one of the "other
# mitigations" discussed in README.md. We deliberately do NOT use it here so
# the stolen-funds exploit is reproducible at least once.
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True

# ---------------------------------------------------------------------------
# Toy "database". In-memory so the demo always resets to a clean state on
# restart: Alice has Rs 50,000, the attacker has Rs 500.
# ----------------------------------------------------------------------------

USERS = {
    "alice": {
        "password": "nimbus123",
        "name": "Alice Fernandes",
        "account": "100122334455",
        "balance": 50_000.00,
    },
    "attacker": {
        "password": "evil123",
        "name": "M. SPECTRE",
        "account": "666600000000",
        "balance": 500.00,
    },
}

# (timestamp, from_account, to_account, amount) — seed line so the history
# table is never empty
TRANSACTIONS = [
    (datetime(2026, 10, 30, 14, 5), "alice", "alice", 150_000.00, "Payroll credit — Nimbus Labs Pvt. Ltd."),
]

_LOCK = threading.Lock()


def money(x: float) -> str:
    return f"₹{x:,.2f}"


def acct(value) -> str:
    """Accepts a user key ('alice') or a raw account number; formats for display."""
    raw = str(USERS[value]["account"]) if value in USERS else str(value)
    raw = raw.replace(" ", "")
    return " ".join(raw[i : i + 4] for i in range(0, len(raw), 4))


app.jinja_env.filters["money"] = money
app.jinja_env.filters["acct"] = acct


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def user_txns(user_key: str):
    me = USERS[user_key]["account"]
    out = []
    for ts, sender, recip, amount, note in reversed(
        [t for t in TRANSACTIONS if t[1] == user_key or t[2] == user_key]
    ):
        if sender == user_key and recip == user_key:
            label = note
            delta = amount
        elif sender == user_key:
            label = f"Outgoing transfer → {acct(recip)}"
            delta = -amount
        else:
            label = f"Incoming transfer ← {acct(sender)}"
            delta = amount
        out.append({"ts": ts, "label": label, "delta": delta})
    return out[:8]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and secrets.compare_digest(user["password"], password):
            session["user"] = username
            # A fresh unpredictable synchronizer token is minted per session.
            # This only becomes *meaningful* once the token check inside
            # POST /transfer below is uncommented; while it remains commented
            # the token is generated but never verified, i.e. zero protection.
            session["csrf_token"] = secrets.token_hex(16)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials. Try alice / nimbus123", "error")
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    u = USERS[session["user"]]
    return render_template(
        "dashboard.html",
        user=u,
        key=session["user"],
        txns=user_txns(session["user"]),
        protect=False,  # set to True AFTER uncommenting the fix in /transfer
    )


@app.route("/transfer", methods=["POST"])
@login_required
def transfer():

    # ------------------------------------------------------------------------
    # token   = request.form.get("csrf_token", "")
    # expected = session.get("csrf_token", "")
    # if not token or not secrets.compare_digest(token, expected):
    #     return render_template(
    #         "blocked.html", protect=True, user=USERS[session["user"]], session=session
    #     ), 403
    # ------------------------------------------------------------------------

    to = request.form.get("to_account", "").replace(" ", "")
    try:
        amount = float(request.form.get("amount", "0"))
    except ValueError:
        amount = 0.0

    with _LOCK:
        sender = USERS[session["user"]]
        if amount <= 0:
            flash("Enter a valid amount.", "error")
        elif amount > sender["balance"]:
            flash("Insufficient balance.", "error")
        else:
            recipient = next((k for k, v in USERS.items() if v["account"] == to), None)
            sender["balance"] -= amount
            if recipient:
                USERS[recipient]["balance"] += amount
            note = request.form.get("note", "").strip() or (
                f"Transfer from {acct(session['user'])}"
            )
            TRANSACTIONS.append((datetime.now(), session["user"], recipient or to, amount, note))
            if recipient:
                flash(f"{money(amount)} sent to {acct(to)} successfully.", "success")
            else:
                flash(f"{money(amount)} debited — beneficiary {acct_by_number(to)} not on NimbusBank.", "error")

    return redirect(url_for("dashboard"))


def acct_by_number(number: str) -> str:
    """'666600000000' -> '6666 0000 0000' for display."""
    return " ".join(number[i : i + 4] for i in range(0, len(number), 4)) if number else number


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3000, debug=False)
