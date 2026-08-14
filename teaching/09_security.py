"""
09_security.py

Section 9: Security
    - OWASP Top 10 basics (injection, XSS, CSRF, broken auth)
    - Secrets management (no hardcoded fallback keys)
    - Password hashing best practices (salting, timing)
    - Input validation/sanitization
    - Rate limiting

Several examples here directly mirror real lines found in this project's
main.py, shown as BAD -> GOOD pairs.

Run: python 09_security.py
"""

import os
import re
import secrets
# New words in this line:
#   secrets  -> standard library module specifically for SECURITY-sensitive
#        randomness (tokens, passwords, session ids). Different from the
#        `random` module (random.randint/random.uniform, seen elsewhere in
#        this course): `random` is fast but PREDICTABLE if an attacker
#        learns its internal state — fine for simulations/games, wrong for
#        anything security-related. `secrets` is slower but cryptographically
#        unpredictable, which is what actually matters here.
# New words in this line:
#   re  -> standard library module for regular expressions (a mini
#        pattern-matching language for text) — see USERNAME_PATTERN below
#        for what it looks like
import sqlite3
import time
from werkzeug.security import generate_password_hash, check_password_hash
# New words in this line:
#   generate_password_hash(password)  -> salts and hashes a password with a
#        slow algorithm (scrypt by default)
#   check_password_hash(hash, guess)   -> verifies a plaintext guess against
#        that hash, without you ever needing to store or compare plaintext
#        directly — see demo_password_hashing() below for what "salted" and
#        "slow" actually buy you


# ---------------------------------------------------------------------------
# Injection (SQL injection example, and the fix)
# ---------------------------------------------------------------------------
def demo_sql_injection():
    print("\n--- SQL Injection ---")

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (username TEXT, password_hash TEXT)")
    conn.execute("INSERT INTO users VALUES ('alice', 'hash123')")
    conn.commit()

    malicious_input = "alice' OR '1'='1"

    # BAD: string-formatting user input directly into SQL
    bad_query = f"SELECT * FROM users WHERE username = '{malicious_input}'"
    rows = conn.execute(bad_query).fetchall()
    print("BAD  query returned rows:", rows, "<- leaked ALL users with one crafted input")

    # GOOD: parameterized query — the driver escapes it safely, `?` is never
    # interpreted as SQL syntax no matter what the user types
    good_rows = conn.execute(
        "SELECT * FROM users WHERE username = ?", (malicious_input,)
    ).fetchall()
    print("GOOD query returned rows:", good_rows, "<- correctly finds nothing")

    conn.close()


# ---------------------------------------------------------------------------
# XSS (Cross-Site Scripting)
# ---------------------------------------------------------------------------
def demo_xss():
    print("\n--- XSS ---")

    user_comment = "<script>alert('stolen cookies')</script>"

    # BAD: rendering raw user input directly into HTML (e.g. Jinja `| safe`,
    # or building HTML strings by hand)
    bad_html = f"<p>{user_comment}</p>"
    print("BAD  (renders as executable script if sent to a browser):", bad_html)

    # GOOD: escape it. Flask/Jinja does this automatically UNLESS you
    # explicitly opt out with `| safe` — the danger is usually a developer
    # adding `| safe` to "fix" a display bug without realizing why it's unsafe
    import html
    # New words in this line:
    #   html (module)  -> standard library module for working with HTML text
    good_html = f"<p>{html.escape(user_comment)}</p>"
    # New words in this line:
    #   html.escape(str)  -> converts special HTML characters (<, >, &,
    #        quotes) into their harmless text equivalents (&lt;, &gt;, etc.)
    #        so a browser displays them as literal text instead of
    #        interpreting them as markup/script
    print("GOOD (renders as inert text):", good_html)


# ---------------------------------------------------------------------------
# CSRF (Cross-Site Request Forgery)
# ---------------------------------------------------------------------------
def demo_csrf():
    print("\n--- CSRF ---")
    print("""
The attack: a browser attaches cookies to EVERY request to a domain, even
requests a DIFFERENT page silently triggered. If bank.com/transfer trusts
"the session cookie is present" as proof the real user meant to do this, a
hidden auto-submitting form sitting on evil.com can POST to
bank.com/transfer using the victim's own browser — the cookie rides along
for free, no password needed:

    <!-- sitting on evil.com, auto-submits the instant the page loads -->
    <form action="https://bank.com/transfer" method="POST">
      <input type="hidden" name="to" value="attacker-account">
      <input type="hidden" name="amount" value="1000">
    </form>
    <script>document.forms[0].submit()</script>
""")

    session_csrf_tokens: dict[str, str] = {}

    def issue_csrf_token(session_id: str) -> str:
        token = secrets.token_hex(16)
        # New words in this line:
        #   secrets.token_hex(n)  -> returns a random string of n BYTES worth
        #        of randomness, shown as 2*n hex characters — used here as an
        #        unguessable, per-session token embedded in every form
        session_csrf_tokens[session_id] = token
        return token

    def handle_transfer(session_id: str, submitted_token: str) -> bool:
        """GOOD: requires proof the request came from a page the server itself rendered."""
        expected = session_csrf_tokens.get(session_id)
        return expected is not None and submitted_token == expected

    real_token = issue_csrf_token("session-123")
    print("GOOD: legit request (token matches the one WE issued):", handle_transfer("session-123", real_token))
    print("GOOD: forged request (attacker's form never saw the real token):",
          handle_transfer("session-123", "attacker-has-no-way-to-know-this"))
    # The forged form on evil.com CAN send the victim's cookie automatically,
    # but it CANNOT read bank.com's page to steal the real csrf_token value —
    # the browser's same-origin policy blocks that. That gap is the entire
    # defense: proving the request came from a page the server itself sent,
    # not just "some browser that happens to have our cookie."

    print("""
Flask-WTF's FlaskForm bakes this in automatically (see this file's sibling,
16_flask_data_auth_apis.py's FLASK_WTF_NOTES) — every form gets a hidden
csrf_token field, and form.validate_on_submit() rejects the submission if
it's missing or wrong, without you writing the check by hand as above.
""")


# ---------------------------------------------------------------------------
# Secrets management
# ---------------------------------------------------------------------------
def demo_secrets_management():
    print("\n--- Secrets Management ---")

    # BAD — this exact pattern is in main.py:
    #   app.config['SECRET_KEY'] = os.environ.get(
    #       'SECRET_KEY', 'your-secret-key-here-change-in-production')
    # If SECRET_KEY is ever unset (a misconfigured deploy), the app
    # silently runs with a secret that's now sitting in a public repo —
    # anyone can forge session cookies.

    def bad_get_secret():
        return os.environ.get("DEMO_SECRET_KEY", "hardcoded-fallback-do-not-do-this")

    def good_get_secret():
        value = os.environ.get("DEMO_SECRET_KEY")
        if not value:
            raise RuntimeError("DEMO_SECRET_KEY is required and was not set — refusing to start")
        return value

    print("BAD  (silently uses a public, guessable key):", bad_get_secret())
    try:
        good_get_secret()
    except RuntimeError as e:
        print("GOOD (fails loudly instead of running insecurely):", e)


# ---------------------------------------------------------------------------
# Password hashing — this project already does the basics right, here's why
# ---------------------------------------------------------------------------
def demo_password_hashing():
    print("\n--- Password Hashing ---")

    password = "correct horse battery staple"

    # BAD: storing plaintext, or a fast unsalted hash like plain md5/sha256
    import hashlib
    # New words in this line:
    #   hashlib (module)  -> general-purpose cryptographic hashing (sha256,
    #        md5, etc.) — fine for checksums, WRONG for passwords, as shown below
    bad_hash = hashlib.sha256(password.encode()).hexdigest()
    # New words in this line:
    #   .encode()    -> converts a str into bytes (hash functions operate on
    #        bytes, not text)
    #   .hexdigest()  -> converts the resulting hash bytes into a readable
    #        hex string
    print("BAD  sha256 (fast, unsalted — crackable at billions/sec on a GPU):", bad_hash[:20], "...")
    # New words in this line:
    #   bad_hash[:20]  -> string SLICING: takes just the first 20 characters
    #        (index 0 up to, not including, 20), purely to keep the printed
    #        output short — different from the slice ASSIGNMENT (history[:] = ...)
    #        seen later in this file, which replaces contents rather than reading them

    # GOOD: werkzeug's generate_password_hash uses a slow, salted algorithm
    # (scrypt by default) — same password hashes DIFFERENTLY each time
    # because of the random salt, and it's deliberately slow to brute-force
    good_hash_1 = generate_password_hash(password)
    good_hash_2 = generate_password_hash(password)
    print("GOOD hash 1:", good_hash_1[:30], "...")
    print("GOOD hash 2:", good_hash_2[:30], "...")
    print("Same password, different hashes (salted):", good_hash_1 != good_hash_2)
    # New words in this line:
    #   !=  -> "not equal to" operator — the inverse of == (already taught
    #        in core_language_mastery.py)
    print("Both still verify correctly:", check_password_hash(good_hash_1, password))


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------
USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
# New words in this line:
#   re.compile(pattern)  -> pre-builds a regex pattern once, so it can be
#        reused efficiently instead of re-parsing the pattern string every time
#   r"..."                -> a "raw string": backslashes are treated
#        literally instead of as escape sequences, which regex patterns
#        rely on heavily
#   Pattern breakdown: ^ = start of string, [a-zA-Z0-9_] = any letter/digit/
#        underscore, {3,20} = repeated 3 to 20 times, $ = end of string


def validate_username(username: str) -> bool:
    return bool(USERNAME_PATTERN.match(username))
    # New words in this line:
    #   .match(string)  -> checks the compiled pattern against the string,
    #        returning a "match object" (truthy) if it matches from the
    #        start, or None (falsy) if it doesn't
    #   bool(x)          -> built-in function: converts any value to a plain
    #        True/False based on its truthiness


def demo_input_validation():
    print("\n--- Input Validation ---")
    for candidate in ["alice", "a", "alice'; DROP TABLE users;--", "valid_user123", ""]:
        print(f"'{candidate}' valid? {validate_username(candidate)}")
    # Validate/whitelist expected shape BEFORE the value ever reaches a
    # query, template, or filesystem path — don't rely on downstream
    # escaping alone to save you.


# ---------------------------------------------------------------------------
# Rate limiting — slows down brute-force login attempts
# ---------------------------------------------------------------------------
class RateLimiter:
    def __init__(self, max_attempts: int, window_seconds: float):
        self.max_attempts = max_attempts
        self.window = window_seconds
        self._attempts: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        # New words in this line:
        #   time.time()  -> the current wall-clock time (seconds since a
        #        fixed reference point) — different from time.perf_counter()
        #        (Section 1), which is only meaningful for measuring
        #        ELAPSED time between two calls, not an actual timestamp
        history = self._attempts.setdefault(key, [])   # (setdefault taught in 04_software_architecture.py)
        history[:] = [t for t in history if now - t < self.window]
        # New words in this line:
        #   history[:] = [...]  -> slice assignment: replaces the CONTENTS
        #        of the existing list in place (same object, new items),
        #        rather than `history = [...]`, which would just point
        #        `history` at a brand-new list and leave the original list
        #        (still referenced by self._attempts[key]) unchanged. This
        #        distinction matters here specifically because `history` is
        #        a reference to a list living INSIDE self._attempts — only
        #        in-place mutation actually updates it there too.
        if len(history) >= self.max_attempts:
            return False
        history.append(now)
        return True


def demo_rate_limiting():
    print("\n--- Rate Limiting ---")

    limiter = RateLimiter(max_attempts=3, window_seconds=10)
    for attempt in range(1, 6):
        allowed = limiter.allow("ip:127.0.0.1")
        print(f"login attempt {attempt}: {'allowed' if allowed else 'BLOCKED'}")
    # Without this, /login is wide open to unlimited password guessing.


if __name__ == "__main__":
    demo_sql_injection()
    demo_xss()
    demo_csrf()
    demo_secrets_management()
    demo_password_hashing()
    demo_input_validation()
    demo_rate_limiting()
