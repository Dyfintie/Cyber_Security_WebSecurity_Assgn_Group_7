"""
Web Server Security Assignment - Autumn Semester 2026
Department of Information Technology, IIIT Allahabad
Course: Cyber Security (IT-30001) | Instructor: Dr. Soumyadev Maity

Category: Cross-Site Scripting (XSS)
Variant: Reflected XSS (Variant 2)
Implemented by: Aman
"""

from flask import Flask, render_template, request, make_response, redirect, url_for
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)


@app.before_request
def ensure_demo_session_cookie():
    """
    Sets a simulated user session cookie for demonstration purposes.
    When a working XSS payload executes 'document.cookie', this token is exposed,
    vividly showing the impact of session hijacking.
    """
    pass


@app.after_request
def set_demo_cookies(response):
    """Attach demo session cookie if not already present."""
    if "session_token" not in request.cookies:
        response.set_cookie(
            "session_token",
            "IIITA_SEC_TOKEN_9847238491823",
            httponly=False,  # Intentionally left accessible for XSS demonstration
            samesite="Lax"
        )
        response.set_cookie(
            "user",
            "aman_student",
            httponly=False,
            samesite="Lax"
        )
    return response


@app.route("/")
def index():
    """Assignment home dashboard and Table 3 ownership overview."""
    return render_template("index.html")


# ==============================================================================
# VARIANT 2: REFLECTED CROSS-SITE SCRIPTING (XSS)
# ==============================================================================

@app.route("/reflected-xss/vulnerable", methods=["GET"])
def vulnerable_reflected_xss():
    """
    VULNERABLE IMPLEMENTATION (Table 2a):
    The search query parameter 'q' is read directly from the GET request
    and passed unsanitized into the template, which uses Jinja2's '| safe' filter.
    
    Root Cause (Table 2c):
    User-controlled input is directly reflected into the HTML response stream
    without context-aware output encoding. The browser's HTML parser cannot
    distinguish application markup from attacker-supplied script tags,
    executing the script under the site's origin.
    """
    query = request.args.get("q", "")
    return render_template("reflected_vulnerable.html", raw_query=query)


@app.route("/reflected-xss/mitigated", methods=["GET"])
def mitigated_reflected_xss():
    """
    MITIGATED IMPLEMENTATION (Table 2d):
    User input is safely rendered through context-aware HTML entity encoding
    (Jinja2 default auto-escaping without '| safe').
    
    Mitigation Effect:
    Characters with special meaning in HTML (<, >, &, ", ') are replaced with
    safe HTML entities (&lt;, &gt;, &amp;, &quot;, &#x27;). The browser treats the
    payload as inert text data, completely neutralizing code execution.
    """
    query = request.args.get("q", "")
    return render_template("reflected_mitigated.html", safe_query=query)


@app.route("/reset-cookie")
def reset_cookie():
    """Helper route to reset the demonstration session cookie."""
    resp = make_response(redirect(url_for("vulnerable_reflected_xss")))
    resp.set_cookie("session_token", f"IIITA_SEC_TOKEN_{secrets.token_hex(6).upper()}", httponly=False)
    resp.set_cookie("user", "aman_student", httponly=False)
    return resp


if __name__ == "__main__":
    print("==================================================================")
    print(" IIIT Allahabad - Cyber Security (IT-30001) Lab Application")
    print(" Reflected Cross-Site Scripting (XSS) - Implemented by Aman")
    print(" Running at: http://127.0.0.1:8080")
    print("==================================================================")
    app.run(host="127.0.0.1", port=8080, debug=True)

