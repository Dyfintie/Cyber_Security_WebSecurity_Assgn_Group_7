# Web Server Security: OS Command Injection (In-Band)

**Indian Institute of Information Technology Allahabad (IIITA)**  
**Department of Information Technology**  
**Course:** Cyber Security (IT-30001) | Autumn Semester 2026  
**Instructor:** Dr. Soumyadev Maity  
**Assignment:** Web Server Security — Exploitation and Mitigation  

---

## 📋 Table 3: Ownership Declaration

| Member Name | Roll Number | Vulnerability Category | Variant Implemented | Exclusive Ownership Confirmation |
| :--- | :--- | :--- | :--- | :--- |
| **Varun** *(Update if needed)* | **IIT2024150** *(Update if needed)* | **OS Command Injection** | **Variant 1: In-Band (Command output returned)** | Personally implemented and defended |
| *[Member 2 Name]* | *[Roll No]* | SQL Injection | *[Variant 1 or 2]* | Personally implemented and defended |
| *[Member 3 Name]* | *[Roll No]* | Cross-Site Scripting (XSS) | *[Variant 1 or 2]* | Personally implemented and defended |
| *[Member 4 Name]* | *[Roll No]* | Cross-Site Request Forgery (CSRF) | *[Variant 1 or 2]* | Personally implemented and defended |

> **Declaration:** This variant was exclusively implemented by the assigned member named above. No two members have implemented the same variant of this category. The member is prepared to demonstrate this implementation live and answer individual questions at the viva.

---

## 🎯 Project Overview

This repository demonstrates the vulnerability lifecycle for **In-Band Operating System (OS) Command Injection**:
1. **Flawed Implementation:** A diagnostic network ping tool vulnerable to arbitrary command injection.
2. **Exploitation:** Executing arbitrary OS commands (`whoami`, `id`, `uname -a`, `cat /etc/passwd`) via in-band output capture.
3. **Mitigation:** Defending against command injection using **Strict Allow-List Regex Validation** combined with **Parameterized Execution via Argument Vectors (`shell=False`)**.
4. **Theoretical Alternatives:** Comparative breakdown of alternative defense mechanisms presented in lecture slides.

---

## 🔍 Section (a): Vulnerable Implementation

The vulnerable code path is located in [`app.py`](app.py) inside the `/api/ping` route handler when `mode == "vulnerable"`:

```python
# VULNERABLE CODE PATH:
command = f"ping -c 2 {target}"
process = subprocess.run(
    command,
    shell=True,          # Flaw: invokes system shell (/bin/sh -c)
    capture_output=True, # In-band: stdout and stderr captured
    text=True,
    timeout=6
)
output = process.stdout + process.stderr
return jsonify({"status": "success", "executed_command": command, "output": output})
```

### Why it is vulnerable:
1. **Unsanitized Input Concatenation:** Untrusted user input (`target`) is directly formatted into a shell command string without validation or escaping.
2. **Shell Interpreter Execution (`shell=True`):** The string is dispatched to `/bin/sh -c`, enabling the shell parser to interpret metacharacters (`;`, `&`, `|`, `$()`, ``` ` ```) as control operators rather than literal data.
3. **In-Band Response:** The web server pipes both `stdout` and `stderr` directly into the HTTP response body returned to the client browser.

---

## 💥 Section (b): Working Exploit Payloads

### Tested Payloads & Evidence

| Payload Tested | Purpose | Injected Command | Result / In-Band Output |
| :--- | :--- | :--- | :--- |
| `127.0.0.1; whoami` | User Identification | `whoami` | Returns current user name (e.g. `varun`) appended to ping statistics. |
| `127.0.0.1; id; uname -a` | System Reconnaissance | `id`, `uname -a` | Returns user ID, group ID (`uid=1000 gid=982...`), and Linux kernel version. |
| `127.0.0.1; cat /etc/passwd \| head -n 5` | Sensitive File Extraction | `cat /etc/passwd` | Dumps the first 5 lines of the system password registry. |
| `127.0.0.1 && ps aux \| head -n 6` | Process List Enumeration | `ps aux` | Returns active running system processes. |
| `127.0.0.1; sleep 3` | Time-Based Blind Check | `sleep 3` | Delays HTTP response by 3 seconds (verifies time-based execution). |

### Exploit Demonstration Output:
```text
PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.061 ms
64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.064 ms

--- 127.0.0.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1014ms
rtt min/avg/max/mdev = 0.061/0.062/0.064/0.002 ms
uid=1000(varun) gid=982(users) groups=982(users),959(docker),963(ollama),998(wheel)
Linux archlinux 6.12.1-arch1-1 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux
```

---

## 🔬 Section (c): Root Cause Analysis

> **Root Cause Summary:**  
> Untrusted user input is directly concatenated into a system command string and passed to a shell interpreter (`shell=True`). The shell parses metacharacters (such as `;`, `&&`, `|`) as command separators, executing arbitrary secondary commands with the privileges of the web application process and returning their output in-band.

---

## 🛡️ Section (d): Implemented Mitigation

The vulnerability is mitigated using **two layers of defense**:
1. **Strict Whitelist (Allow-list) Input Validation**
2. **Parameterized Execution using Argument Vectors (`shell=False`)**

### Mitigated Code Path ([`app.py`](app.py)):

```python
# Defense Layer 1: Strict Allow-List Regex
allowlist_regex = r"^[a-zA-Z0-9.-]+$"
if not re.match(allowlist_regex, target):
    return jsonify({
        "status": "blocked",
        "message": "SECURITY ALERT: Request blocked by allow-list filter. Shell metacharacters or invalid hostnames are strictly prohibited.",
        "output": f"[SECURITY_FILTER_TRIGGERED] Input '{target}' rejected."
    }), 400

# Defense Layer 2: Parameterized Execution (Avoid the Shell)
cmd_args = ["ping", "-c", "2", target]
process = subprocess.run(
    cmd_args,
    shell=False,          # Directly invokes execve syscall; NO shell parsing
    capture_output=True,
    text=True,
    timeout=6
)
```

### Verification Proof (Blocked Exploit):
Submitting the exact same exploit payload (`127.0.0.1; whoami; id; uname -a`) in mitigated mode yields:
```json
HTTP/1.1 400 BAD REQUEST
{
  "status": "blocked",
  "mode": "mitigated",
  "message": "SECURITY ALERT: Request blocked by allow-list filter. Shell metacharacters or invalid hostnames are strictly prohibited.",
  "output": "[SECURITY_FILTER_TRIGGERED] Input '127.0.0.1; whoami; id; uname -a' rejected by allow-list pattern r'^[a-zA-Z0-9.-]+$'."
}
```
Even if an argument bypasses regex checks, `shell=False` ensures that the argument is passed directly to `ping` as literal data; `ping` simply reports `ping: unknown host 127.0.0.1; whoami; id; uname -a`, completely neutralizing execution.

---

## 📚 Section (e): Theory of Alternative Mitigations

As required by Table 2 item (e) and the course lecture slides, here is the comparative study of all four mitigation alternatives:

### 1. Avoid the Shell (Use Native APIs)
- **Concept:** Rather than invoking external operating system command-line utilities via system shells, the application utilizes native programming language APIs or libraries (e.g., Python's `socket`, `scapy`, or `ping3` packages).
- **Why It Works:** Eliminates process creation and shell dispatch entirely. Since no shell or subprocess is spawned, command injection is rendered architecturally impossible.

### 2. Parameterized Execution with an Argument Vector (`shell=False`)
- **Concept:** Commands and their respective arguments are segregated into discrete array/vector elements (e.g. `["ping", "-c", "2", user_arg]`) and executed with `shell=False`.
- **Why It Works:** The runtime bypasses the command interpreter and dispatches the array directly to kernel system calls (such as `execve()` on POSIX or `CreateProcess()` on Windows). Metacharacters (`;`, `&`, `|`) are treated strictly as literal string parameters to the binary, never as executable grammar.

### 3. Allow-List Input Validation
- **Concept:** Incoming user data is checked against a strict whitelist of permissible patterns (e.g., IP address regex `^[0-9]{1,3}(\.[0-9]{1,3}){3}$` or FQDN pattern `^[a-zA-Z0-9.-]+$`), rejecting any non-matching characters.
- **Why It Works:** It enforces syntactic safety at the application perimeter, rejecting dangerous shell delimiters and control characters before they can interact with execution logic.

### 4. Principle of Least Privilege & Sandboxing
- **Concept:** The web server runs under a dedicated, unprivileged system account (e.g., `www-data` or `nobody`) with no administrative/sudo privileges, restricted file permissions, and inside a container, chroot jail, or seccomp/AppArmor security profile.
- **Why It Works:** Defense-in-depth: if an adversary successfully exploits an unforeseen flaw, their ability to execute privileged commands, read sensitive system files (e.g. `/etc/shadow`), or pivot within the host network is strictly constrained.

---

## 🚀 How to Run the Application

### Prerequisites
- Python 3.10+
- Linux / macOS / WSL

### Quick Start
```bash
# Clone the repository
git clone <your-repo-link>
cd os-command-injection-assignment

# Run the automated verification suite (runs 4 tests)
./run.sh test

# Start the interactive web server
./run.sh
```
Open **`http://127.0.0.1:5000`** in your browser.

---

## 🧪 Automated Test Verification

Run the automated test suite to verify both the vulnerability and mitigation:
```bash
./run.sh test
```

Expected output:
```text
======================================================================
 Running Automated Verification Suite for OS Command Injection Lab
======================================================================
[TEST 1] Vulnerable Mode with Benign Input ('127.0.0.1'):
  -> PASS: Benign ping executed successfully.
[TEST 2] Vulnerable Mode with In-Band Exploit ('127.0.0.1; id; echo '__EXPLOIT_VERIFIED__''):
  -> PASS: In-band OS command injection executed successfully.
[TEST 3] Mitigated Mode with Benign Input ('127.0.0.1'):
  -> PASS: Mitigated endpoint executes valid host successfully.
[TEST 4] Mitigated Mode with Exploit Payload ('127.0.0.1; id; echo '__EXPLOIT_VERIFIED__''):
  -> PASS: Exploit successfully intercepted and blocked by security filter.
======================================================================
 ALL 4 TESTS PASSED! Verification Complete.
======================================================================
```

---

## 🎓 Viva Voce Preparation Guide

### Q1: What is the difference between In-Band and Blind OS command injection?
**Answer:** In **In-Band** command injection, the application returns the output of the injected command directly inside the HTTP response (stdout/stderr). In **Blind** command injection, command output is discarded or not returned; the attacker must infer successful execution using side-channels like time delays (`sleep 5`) or out-of-band network callbacks (DNS/HTTP requests to an attacker-controlled server).

### Q2: Why is `shell=True` dangerous in Python's `subprocess`?
**Answer:** `shell=True` passes the command string to the system shell (`/bin/sh -c`). The shell parses metacharacters such as `;`, `&`, `|`, and backticks as syntax tokens, allowing an attacker to terminate the intended command and execute arbitrary subsequent commands.

### Q3: Why is parameterization (`shell=False`) superior to blacklisting bad characters?
**Answer:** Blacklisting is inherently fragile because attackers can often bypass filters using alternative metacharacters (e.g., `${IFS}`, newline `%0a`, pipes `|`, redirects `<`). Parameterization with `shell=False` fundamentally solves the problem by bypassing the shell interpreter altogether and passing arguments as literal strings directly to the kernel `execve` syscall.
