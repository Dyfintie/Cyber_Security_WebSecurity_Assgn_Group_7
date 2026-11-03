#!/usr/bin/env bash
# NimbusBank CSRF demo launcher.
#
#   ./run.sh        -> starts the bank VULNERABLE (as shipped) + the attacker page
#
# The bank ships compromised. The synchronizer-token fix lives, commented
# out, inside bank/app.py → POST /transfer. Uncomment it to secure the site
#; nothing changes here — rerun and the same attack gets a 403.
#
# Then open:  bank  http://localhost:3000  |  attacker  http://localhost:3001
set -euo pipefail
cd "$(dirname "$0")"

PY="python3"
if [ ! -x "$PY" ] && [ -x /usr/bin/python3 ]; then PY=/usr/bin/python3; fi

# Ensure Flask is available in the repo-local venv (no system pip dependency).
if ! "$PY" -c "import flask" >/dev/null 2>&1; then
  if [ ! -x ".venv/bin/python3" ]; then
    echo "[*] Creating .venv and installing Flask (first run only)…"
    "$PY" -m venv .venv
    .venv/bin/pip install --quiet flask
  fi
  PY=".venv/bin/python3"
fi

# Free the ports from any previous run.
for port in 3000 3001; do
  PIDS="$(fuser ${port}/tcp 2>/dev/null || true)"
  [ -n "$PIDS" ] && kill -9 $PIDS 2>/dev/null || true
done

"$PY" bank/app.py &
BANK_PID=$!
"$PY" attacker/app.py &
ATTACKER_PID=$!

trap "kill $BANK_PID $ATTACKER_PID 2>/dev/null" EXIT

sleep 1.5
echo
echo "────────────────────────────────────────────────────────────"
echo " NimbusBank CSRF demo — mode: VULNERABLE (attack WILL succeed)"
echo
echo "   Bank (victim)   →  http://localhost:3000   [alice / nimbus123]"
echo "   Attacker site   →  http://localhost:3001   (silent iframe attack)"
echo "   Visible replay  →  http://localhost:3001/visible"
echo
echo " Demo: 1) log in as alice, note balance 50,000"
echo "       2) open :3001 in another tab (page looks innocent — the"
echo "          hidden iframe already fired the forged POST)"
echo "       3) switch back to :3000 and refresh → ₹35,000 gone"
echo
echo " To secure: uncomment the 🔧 THE FIX block in bank/app.py"
echo " (inside POST /transfer) and rerun — same attack → 403."
echo "────────────────────────────────────────────────────────────"
echo

wait
