"""
Web Server Security Lab: OS Command Injection (IT-30001)
Indian Institute of Information Technology Allahabad (IIITA)
Course: Cyber Security (IT-30001) | Autumn Semester 2026
Instructor: Dr. Soumyadev Maity

Variant 1: In-Band OS Command Injection (Command Output Returned)
Author: Student Submission
"""

import os
import re
import subprocess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/ping", methods=["POST"])
def ping():
    data = request.get_json(silent=True) or request.form
    target = data.get("target", "").strip()
    mode = data.get("mode", "vulnerable")

    if not target:
        return jsonify({
            "status": "error",
            "message": "Target host cannot be empty."
        }), 400

    if mode == "vulnerable":
        # =========================================================================
        # (a) VULNERABLE IMPLEMENTATION
        # =========================================================================
        # ROOT CAUSE:
        # 1. Untrusted user input (`target`) is concatenated directly into a shell command string.
        # 2. `shell=True` passes the string to `/bin/sh -c`, enabling shell metacharacters
        #    such as `;`, `&`, `|`, `$()`, or ``` ` ``` to terminate `ping` and execute arbitrary OS commands.
        # 3. In-band: stdout and stderr are captured and returned directly to the user response.
        # =========================================================================
        command = f"ping -c 2 {target}"
        try:
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=6
            )
            output = process.stdout + process.stderr
            return jsonify({
                "status": "success",
                "mode": "vulnerable",
                "executed_command": command,
                "output": output,
                "returncode": process.returncode
            })
        except subprocess.TimeoutExpired:
            return jsonify({
                "status": "error",
                "mode": "vulnerable",
                "executed_command": command,
                "output": "Command execution timed out (possible sleep or long-running injection)."
            }), 408
        except Exception as e:
            return jsonify({
                "status": "error",
                "mode": "vulnerable",
                "executed_command": command,
                "output": str(e)
            }), 500

    elif mode == "mitigated":
        # =========================================================================
        # (d) IMPLEMENTED MITIGATION
        # =========================================================================
        # FIX 1: Strict Allow-list Input Validation
        # Validates that the input strictly matches standard IP or FQDN characters.
        # Any metacharacter (; & | ` $ > < \n) causes immediate rejection before execution.
        # =========================================================================
        allowlist_regex = r"^[a-zA-Z0-9.-]+$"
        if not re.match(allowlist_regex, target):
            return jsonify({
                "status": "blocked",
                "mode": "mitigated",
                "executed_command": None,
                "message": "SECURITY ALERT: Request blocked by allow-list filter. Shell metacharacters or invalid hostnames are strictly prohibited.",
                "output": f"[SECURITY_FILTER_TRIGGERED] Input '{target}' rejected by allow-list pattern r'{allowlist_regex}'."
            }), 400

        # =========================================================================
        # FIX 2: Parameterized Execution via Argument Vector (Avoid the Shell)
        # Bypasses the shell interpreter entirely (shell=False).
        # Arguments are passed as an isolated vector directly to the OS `execve` syscall.
        # Even if a malicious string bypassed the regex, it would be treated strictly as
        # literal data (a single hostname argument to ping), preventing arbitrary execution.
        # =========================================================================
        cmd_args = ["ping", "-c", "2", target]
        try:
            process = subprocess.run(
                cmd_args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=6
            )
            output = process.stdout + process.stderr
            return jsonify({
                "status": "success",
                "mode": "mitigated",
                "executed_command": " ".join(cmd_args),
                "output": output,
                "returncode": process.returncode
            })
        except subprocess.TimeoutExpired:
            return jsonify({
                "status": "error",
                "mode": "mitigated",
                "executed_command": " ".join(cmd_args),
                "output": "Ping command timed out."
            }), 408
        except Exception as e:
            return jsonify({
                "status": "error",
                "mode": "mitigated",
                "executed_command": " ".join(cmd_args),
                "output": str(e)
            }), 500

    else:
        return jsonify({"status": "error", "message": "Invalid mode specified."}), 400

if __name__ == "__main__":
    print("=" * 70)
    print("  IIITA Cyber Security Lab (IT-30001) - OS Command Injection")
    print("  Server starting on http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host="0.0.0.0", port=5000, debug=True)
