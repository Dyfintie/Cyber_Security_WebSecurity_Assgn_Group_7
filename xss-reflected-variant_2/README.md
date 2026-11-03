# Web Server Security: Exploitation and Mitigation Lab

**Course**: Cyber Security (IT-30001) — Autumn Semester 2026  
**Department**: Department of Information Technology  
**Institution**: Indian Institute of Information Technology Allahabad (IIIT Allahabad)  
**Instructor**: Dr. Soumyadev Maity  

---

## Quick Start & Installation

### 1. Requirements
* Python 3.10+
* Flask (`pip install -r requirements.txt`)

### 2. Running the Application
```bash
# Clone or navigate to the repository
cd cyber-sec

# Install dependencies
pip install -r requirements.txt

# Start the Flask web application
python3 app.py
```
Open your browser and navigate to:
**`http://127.0.0.1:5000`**

### 3. Automated Verification Tests
We provide an automated test suite verifying that the vulnerable endpoint reflects raw script markup and the mitigated endpoint safely encodes HTML entities:
```bash
python3 exploits/test_reflected_xss.py
```

---

## Detailed Variant Documentation: Reflected XSS

### (a) Vulnerable Implementation (Table 2a)
The application implements an e-commerce product search endpoint located at `/reflected-xss/vulnerable`. The vulnerable code path is identified below:

* **Backend Controller (`app.py`)**:
  ```python
  @app.route("/reflected-xss/vulnerable", methods=["GET"])
  def vulnerable_reflected_xss():
      # Reads untrusted user input directly from the URL query string
      query = request.args.get("q", "")
      # Passes raw query directly to the Jinja2 template
      return render_template("reflected_vulnerable.html", raw_query=query)
  ```

* **Frontend Template (`templates/reflected_vulnerable.html`)**:
  ```html
  <!-- Flawed template line: '| safe' disables Jinja's auto-escaping mechanism -->
  <h4>Search results for: {{ raw_query | safe }}</h4>
  ```

---

### (b) Working Exploit (Table 2b)

Reflected XSS is an indirect attack delivered via social engineering or phishing. An attacker crafts a URL containing a malicious JavaScript payload and tricks the victim into clicking it.

#### Exploit Payloads:
1. **Standard Proof-of-Concept Alert**:
   * **Payload**: `<script>alert('Reflected XSS PoC by Aman (IIIT-A)')</script>`
   * **Target URL**:
     ```
     http://127.0.0.1:5000/reflected-xss/vulnerable?q=%3Cscript%3Ealert('Reflected+XSS+PoC+by+Aman+(IIIT-A)')%3C%2Fscript%3E
     ```
   * **Result**: The browser executes the injected script and triggers an alert pop-up window.

2. **Session Hijacking / Credential Theft PoC**:
   * **Payload**: `<script>alert('Session Hijack PoC!\n\nVictim Cookies:\n' + document.cookie)</script>`
   * **Target URL**:
     ```
     http://127.0.0.1:5000/reflected-xss/vulnerable?q=%3Cscript%3Ealert('Session+Hijack+PoC!%5Cn%5CnVictim+Cookies%3A+%5Cn'+document.cookie)%3C%2Fscript%3E
     ```
   * **Result**: Alerts active session tokens (`session_token=IIITA_SEC_TOKEN_...`). In a real exploit, this data is exfiltrated to an attacker's listener server.

3. **Event-Handler Filter Bypass**:
   * **Payload**: `<img src=x onerror="alert('Reflected XSS via <img> onerror: ' + document.domain)">`
   * **Target URL**:
     ```
     http://127.0.0.1:5000/reflected-xss/vulnerable?q=%3Cimg+src%3Dx+onerror%3D%22alert('Reflected+XSS+via+Image+OnError+Handler!+Origin%3A+'+document.domain)%22%3E
     ```
   * **Result**: Bypasses naive filters looking only for `<script>` tags by utilizing the `onerror` event of an invalid image tag.

---

### (c) Root Cause (Table 2c)
> **Root Cause**: Untrusted user input supplied via the HTTP GET parameter `q` is directly reflected and concatenated into the HTTP response HTML stream without context-aware output encoding or sanitization. Because the browser's HTML parser cannot distinguish trusted developer markup from attacker-injected markup, it parses the input as executable JavaScript code and runs it within the security context of the victim's session.

---

### (d) Mitigation Implemented (Table 2d)
* **Chosen Fix**: **Context-Aware HTML Entity Encoding / Framework Auto-Escaping**.
* **Code Modification**:
  * In `templates/reflected_mitigated.html`, the unsafe bypass filter `| safe` was removed:
    ```html
    <!-- Mitigated Template: Jinja2 auto-escapes user input by default -->
    <h4>Search results for: {{ safe_query }}</h4>
    ```
* **How It Blocks the Exploit**:
  When the exact same malicious payload `<script>alert(1)</script>` is submitted to `/reflected-xss/mitigated`, the template engine encodes the sensitive HTML delimiter characters:
  * `<` becomes `&lt;`
  * `>` becomes `&gt;`
  * `&` becomes `&amp;`
  * `"` becomes `&quot;`
  * `'` becomes `&#x27;`
* **Verification**:
  The wire HTML response becomes:
  ```html
  <h4>Search results for: &lt;script&gt;alert(1)&lt;/script&gt;</h4>
  ```
  The browser treats this strictly as inert text data, displaying literal characters on screen rather than executing code.

---

### (e) Other Mitigations in Theory (Table 2e)

As discussed in lecture slides, defense against Cross-Site Scripting relies on defense-in-depth across multiple layers:

1. **Context-Aware Output Encoding & Framework Auto-Escaping**:
   Different parts of a web document require different encoding schemes (e.g. HTML body encoding, HTML attribute encoding, JavaScript variable encoding, URL parameter encoding). Modern templating frameworks (Jinja2, React JSX, Angular) provide contextual auto-escaping out of the box, converting characters like `<`, `>`, `&`, `"`, `'` into safe entities so that untrusted input can never alter document structure.
2. **Content Security Policy (CSP)**:
   An HTTP response header (`Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-...'; object-src 'none'`) configured on the server. CSP instructs the browser to restrict script execution exclusively to authorized sources. Strict CSP disables inline `<script>` tags and JavaScript execution via event handlers (`onerror`, `onload`), rendering reflected payloads benign even if injected into HTML.
3. **HttpOnly Cookie Flag**:
   Sensitive session cookies should be marked with the `HttpOnly` directive (`Set-Cookie: session_id=...; HttpOnly; Secure; SameSite=Strict`). This prevents client-side scripts from reading session identifiers through `document.cookie`. While HttpOnly does not stop the XSS execution itself, it neutralizes session hijacking.
4. **Rich HTML Sanitizers**:
   When applications must allow users to post formatted HTML (e.g., markdown or rich-text editors), simple entity encoding is insufficient. In such cases, robust sanitization libraries such as **DOMPurify** (client-side) or **Bleach/nh3** (server-side) parse the HTML tree against strict allow-lists, stripping malicious tags (`<script>`, `<iframe>`, `<object>`) and dangerous attributes (`onload`, `onerror`) while permitting safe formatting tags (`<b>`, `<i>`, `<p>`).
5. **Safe DOM Sinks**:
   In client-side single-page applications, developers must avoid dangerous JavaScript execution sinks such as `element.innerHTML`, `document.write()`, and `eval()`. Instead, safe properties like `element.textContent` or `element.innerText` must be used, which instruct the browser to treat values strictly as text rather than executable markup.

---
