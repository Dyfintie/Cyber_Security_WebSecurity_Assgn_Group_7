# 🎬 2.5-Minute Video Demonstration Script
## IIITA IT-30001: Web Server Security — In-Band OS Command Injection

- **Target Duration:** 2 minutes 30 seconds (Requirement: 2 to 3 minutes per member)
- **Role:** Individual demonstration of **OS Command Injection (Variant 1: In-Band)**
- **Presenter:** Varun (Roll: IIT2024150) — *Update with your actual name/roll if needed*

---

## ⏱️ Video Timeline Overview

| Time | Segment | What to Show on Screen | Key Points to Speak |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:25** | Introduction & Ownership | Terminal showing `./run.sh` & Browser opening `http://127.0.0.1:5000` | State your name, roll no, course IT-30001, category (OS Command Injection), variant (In-Band). |
| **0:25 - 0:55** | Vulnerable Code & Root Cause | Split screen or tab showing `app.py` vulnerable code path | Point out string concatenation `f"ping -c 2 {target}"`, `shell=True`, and stdout captured in HTTP response. |
| **0:55 - 1:35** | Working Exploit Demonstration | Browser on Vulnerable mode | 1. Run `127.0.0.1` (normal ping).<br>2. Run `127.0.0.1; whoami; id; uname -a`.<br>3. Highlight in-band output (`uid=1000`, kernel version). |
| **1:35 - 2:10** | Implemented Mitigation | Switch to Mitigated mode in UI and show code in `app.py` | 1. Submit exact same payload `127.0.0.1; whoami; id; uname -a`.<br>2. Show "SECURITY ALERT: Request blocked".<br>3. Explain allow-list regex + `shell=False` parameterization. |
| **2:10 - 2:35** | Alternative Mitigations & Conclusion | UI "Mitigation Alternatives" Tab or Slide | Summarize 4 defenses from lecture: Avoid shell, Parameterized execution, Allow-list, Least privilege. |

---

## 🎙️ Word-for-Word Narration Script

### [0:00 - 0:25] Introduction & Ownership Declaration
> *(Screen: Show desktop with terminal starting `./run.sh` and browser displaying the Network Host Diagnostic Tool at `http://127.0.0.1:5000`)*
>
> **Speak:**  
> "Hello everyone and respected instructor Dr. Soumyadev Maity.  
> My name is **Varun**, Roll Number **IIT2024150**, from the Department of Information Technology at IIITA.  
> As part of our IT-30001 Cyber Security assignment on Web Server Security, I have personally implemented and defended the vulnerability category: **OS Command Injection**, specifically **Variant 1: In-Band Command Injection, where command output is returned in the response**."

---

### [0:25 - 0:55] Vulnerable Implementation & Root Cause
> *(Screen: Switch to VS Code or the web page's "Code Comparison" tab, highlighting the vulnerable code block in `app.py`)*
>
> **Speak:**  
> "Let us first examine the vulnerable implementation in `app.py`.  
> Here, our web server provides a network diagnostics ping utility. Notice the code on lines 36 to 45:  
> The variable `target` received from the user's HTTP POST request is concatenated directly into a shell command string using Python f-strings: `f'ping -c 2 {target}'`.  
> Crucially, it is executed using `subprocess.run` with `shell=True`.  
> **The root cause:** Calling the system shell through `shell=True` causes the shell interpreter (`/bin/sh`) to parse metacharacters like semicolon, ampersand, or pipe as syntax command separators. Because the standard output and standard error are piped directly into the JSON response, any injected command's output is returned in-band to the client."

---

### [0:55 - 1:35] Live Exploit Demonstration
> *(Screen: Switch to the web interface. Ensure "⚠️ Vulnerable Service (shell=True)" is active)*
>
> **Speak:**  
> "Now let's see the exploit in action.  
> First, if I submit a normal host like `127.0.0.1`, the server runs `ping -c 2 127.0.0.1` and returns standard ping statistics.  
> Now, as an attacker, I will append an arbitrary OS command using a semicolon separator:  
> `127.0.0.1; whoami; id; uname -a`  
> Let's send the request.  
> *(Click Send Diagnostic Request, wait 1-2 seconds)*  
> As you can see right here in the terminal output: the ping command finishes, and immediately following it, the server executes our injected commands!  
> We have `whoami` returning the current user, `id` returning `uid=1000 gid=982`, and `uname -a` printing the full Linux kernel version and architecture.  
> This proves successful in-band remote code execution."

---

### [1:35 - 2:10] Implemented Mitigation & Verification
> *(Screen: Click on "🛡️ Mitigated Service" mode button on the web page, then briefly show the mitigated code snippet)*
>
> **Speak:**  
> "Now let us turn to the mitigation.  
> To defend against this, I implemented a two-tier defense:  
> First, a strict allow-list regular expression `^[a-zA-Z0-9.-]+$` that strictly restricts input to alphanumeric characters, dots, and hyphens—immediately rejecting any shell metacharacters before execution.  
> Second, parameterized execution using an argument vector: `['ping', '-c', '2', target]` with `shell=False`. This invokes the OS kernel `execve` system call directly without invoking `/bin/sh`, ensuring arguments are treated purely as literal data.  
> Let us verify this live. I will submit the **exact same exploit payload**:  
> `127.0.0.1; whoami; id; uname -a`  
> *(Click Send Diagnostic Request)*  
> Notice that the request is immediately intercepted with HTTP 400 Bad Request:  
> *'SECURITY ALERT: Request blocked by allow-list filter.'*  
> The exploit payload is completely neutralized and no command is executed."

---

### [2:10 - 2:35] Theory of Alternative Mitigations & Conclusion
> *(Screen: Switch to "Mitigation Alternatives (Theory)" tab on the page)*
>
> **Speak:**  
> "Finally, according to our course slides, the four core mitigations for command injection are:  
> 1. **Avoid the shell:** Use native APIs like Python's `socket` or `ping3` libraries so no external process is ever spawned.  
> 2. **Parameterized execution:** Segregate arguments into vectors with `shell=False` so metacharacters are never parsed as syntax.  
> 3. **Allow-list validation:** Whitelist only known-safe characters at the perimeter.  
> 4. **Principle of Least Privilege:** Run the server under an unprivileged user like `www-data` inside a sandbox or container to constrain blast radius.  
> This concludes my demonstration for OS Command Injection. Thank you!"

---

## 🎥 Recording Instructions on Arch Linux

You can record your screen and microphone easily using one of these options:

### Option 1: OBS Studio (Recommended)
1. Install if needed: `sudo pacman -S obs-studio`
2. Open OBS -> Add "PipeWire Audio Capture" (Microphone) and "Screen Capture (PipeWire)" (Display).
3. Start Recording, speak the script while doing the clicks, and Stop Recording.

### Option 2: Browser Extension / Web Recorder (Zero Install)
Open [https://screenapp.io](https://screenapp.io) or [https://loom.com](https://loom.com) in your browser, select your screen + microphone, and record.

### Option 3: Hyprland / Wayland CLI (`wf-recorder`)
```bash
wf-recorder --audio -f demonstration_varun.mp4
# Press Ctrl+C when finished
```
