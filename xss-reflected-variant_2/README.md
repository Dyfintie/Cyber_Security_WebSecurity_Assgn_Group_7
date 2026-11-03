# Web Server Security: Exploitation and Mitigation Lab

**Course**: Cyber Security (IT-30001) — Autumn Semester 2026  
**Department**: Department of Information Technology  
**Institution**: Indian Institute of Information Technology Allahabad (IIIT Allahabad)  
**Instructor**: Dr. Soumyadev Maity  

---

## Table 3. Ownership Declaration

| Member Name | Roll Number | Category | Variant Implemented | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Aman** | `IIT2024140` | **Cross-Site Scripting (XSS)** | **Variant 2: Reflected XSS** | **Complete** |
| *[Member 2]* | *[Roll No]* | SQL Injection | Variant 1: Auth Bypass / Variant 2: UNION Data Extraction | Group Member |
| *[Member 3]* | *[Roll No]* | OS Command Injection | Variant 1: In-band / Variant 2: Blind | Group Member |
| *[Member 4]* | *[Roll No]* | Cross-Site Request Forgery | Variant 1: GET-based / Variant 2: POST-based | Group Member |

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

## Detailed Variant Documentation: Reflected XSS (Aman)

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

## Video Demonstration Script (2–3 Minutes for Aman)

* **[0:00 - 0:35] Introduction & Vulnerable Code Path (Table 2a)**:
  > *"Hello everyone and respected instructor Dr. Soumyadev Maity. I am Aman, Roll Number `IIT2024140`. In this video demonstration for our Web Server Security assignment, I will demonstrate Category 3: Cross-Site Scripting, specifically Variant 2: Reflected XSS.  
  > In our Flask application, we have an e-commerce product search endpoint at `/reflected-xss/vulnerable`. Looking at the code in `app.py`, the server takes the GET parameter `q` and passes it directly to `reflected_vulnerable.html`. In the template, the line `{{ raw_query | safe }}` explicitly disables auto-escaping, reflecting user input verbatim into the response."*

* **[0:35 - 1:15] Demonstrating the Working Exploit (Table 2b)**:
  > *"Now I will demonstrate the attack. As an attacker, I craft a URL containing this payload: `<script>alert('Session Hijack PoC!\n' + document.cookie)</script>`.  
  > I send this link to a victim. When the victim clicks the link, the server immediately reflects the query in the response. As you can see on the screen, the browser executes the script under the site's origin and pops up an alert displaying the victim's active session cookie `IIITA_SEC_TOKEN`. We also verify tag bypass using `<img src=x onerror=...>`, which fires immediately."*

* **[1:15 - 1:45] Root Cause Explanation (Table 2c)**:
  > *"The root cause of this vulnerability is that untrusted user input from an HTTP GET parameter is directly rendered into the HTML document context without context-aware output encoding. The browser's HTML parser cannot distinguish application markup from attacker-supplied script tags, executing the payload in the context of the user's session."*

* **[1:45 - 2:25] Implemented Mitigation Demonstration (Table 2d)**:
  > *"To fix this, we switch to our mitigated endpoint `/reflected-xss/mitigated`. In the code, we removed the `| safe` bypass, allowing Jinja2's context-aware output encoding to take effect.  
  > When I submit the exact same malicious payload `<script>alert(...)`, notice that no alert pops up. Inspecting the page source, characters like `<` and `>` have been safely encoded into `&lt;` and `&gt;`. The browser renders the payload harmlessly as text."*

* **[2:25 - 2:50] Other Mitigations in Theory (Table 2e) & Conclusion**:
  > *"Beyond output encoding, defense-in-depth mitigations from lecture slides include Content Security Policy (CSP) to restrict inline script execution, HttpOnly cookie flags to prevent session hijacking via `document.cookie`, sanitizers like DOMPurify for rich HTML, and using safe DOM sinks like `textContent`. Thank you."*

---

## Viva Preparation Cheat Sheet

1. **What is the difference between Reflected XSS and Stored XSS?**
   * *Answer*: Reflected XSS is non-persistent; the payload is included in the immediate HTTP request (typically URL parameter) and reflected back in that single response. It requires tricking a victim into clicking a malicious link. Stored XSS is persistent; the payload is stored in a database or server storage and executed whenever any user views the affected page.
2. **Why does HTML entity encoding stop Reflected XSS?**
   * *Answer*: Browsers identify HTML tags using delimiter characters (`<` and `>`). When these characters are replaced with entities (`&lt;` and `&gt;`), the browser's HTML parser interprets them as literal character data rather than tokenizing them as HTML tags or script blocks.
3. **Does setting `HttpOnly` on cookies prevent XSS?**
   * *Answer*: No. `HttpOnly` only prevents JavaScript from accessing `document.cookie`. An attacker with XSS can still perform unauthorized actions on behalf of the user (e.g. submitting forms, transferring funds, stealing CSRF tokens, logging keystrokes, or modifying page DOM). It is a defense-in-depth measure, not a root fix for XSS.
4. **How does Content Security Policy (CSP) protect against XSS?**
   * *Answer*: CSP is an HTTP response header that restricts the locations and types of scripts the browser will execute. By setting `script-src 'self'` or using cryptographic nonces (`'nonce-xyz'`), CSP causes the browser to reject injected inline `<script>` tags and event handlers (`onerror`), even if an attacker successfully injects them into HTML.

