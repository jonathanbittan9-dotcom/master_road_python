"""
14_web_fundamentals.py

Section 14: Adjacent Web Fundamentals
    - HTTP deeply: status codes, headers, caching, cookies vs. sessions
    - A minimal Flask app to inspect these live
    - WebSocket basics (notes) — relevant given the Discord bot work
      already happening in this workspace

Run: python 14_web_fundamentals.py
Then visit: http://127.0.0.1:5050/  and  http://127.0.0.1:5050/whoami
"""

from flask import Flask, request, make_response, session
# New words in this line (beyond testlearn.py's Flask basics —
# Flask/@app.route/render_template/url_for):
#   request        -> the incoming HTTP request (headers, cookies, form data, ...)
#   make_response  -> builds a Response object explicitly, so you can add
#        headers/cookies to it before returning (used in whoami()/cached_data() below)
#   session        -> a dict-like object backed by a signed cookie, for
#        storing small bits of data tied to one visitor across requests


# ---------------------------------------------------------------------------
# HTTP status codes — reference (not something to memorize, but recognize)
# ---------------------------------------------------------------------------
STATUS_CODE_NOTES = """
2xx Success
  200 OK               - standard success
  201 Created          - a new resource was created (e.g. after POST /books)
  204 No Content        - success, but nothing to return (e.g. after DELETE)

3xx Redirection
  301 Moved Permanently - resource moved, update bookmarks/links
  302 Found              - temporary redirect
  304 Not Modified       - cached version is still valid, don't re-send the body

4xx Client Error (the CALLER did something wrong)
  400 Bad Request        - malformed request (bad JSON, missing field)
  401 Unauthorized        - not authenticated (no/invalid credentials)
  403 Forbidden            - authenticated, but not ALLOWED to do this
  404 Not Found             - resource doesn't exist
  409 Conflict               - request conflicts with current state (e.g. borrowing an already-borrowed book)
  429 Too Many Requests       - rate limited

5xx Server Error (the SERVER did something wrong)
  500 Internal Server Error - unhandled exception
  502 Bad Gateway            - upstream server returned an invalid response
  503 Service Unavailable     - server temporarily can't handle the request (e.g. failed health check)

401 vs 403, the common mix-up:
  401 = "I don't know who you are" (log in)
  403 = "I know who you are, and you're not allowed" (permissions)
"""


def demo_status_codes():
    print("\n--- HTTP Status Codes ---")
    print(STATUS_CODE_NOTES)


# ---------------------------------------------------------------------------
# HTTP Methods — what each one PROMISES, not just what it does
# ---------------------------------------------------------------------------
HTTP_METHODS_NOTES = """
GET     - fetch a resource. SAFE (no side effects) and IDEMPOTENT (calling
          it 5 times has the same effect as calling it once — nothing
          changes further each time).
POST    - create something / trigger an action with side effects. NEITHER
          safe nor idempotent — calling it twice can create two of
          something. This is exactly why 15_flask_architecture_and_requests.py's
          Post/Redirect/Get pattern exists: refreshing a page should never
          silently re-run a POST.
PUT     - replace a resource ENTIRELY with the given representation.
          IDEMPOTENT (though not safe): PUT-ing the exact same body twice
          leaves the resource in the same end state either time — unlike
          POST, calling it again doesn't create a second copy.
PATCH   - partially update a resource (e.g. just one field). Not
          guaranteed idempotent in general, though many APIs design their
          PATCH endpoints to behave that way in practice.
DELETE  - remove a resource. IDEMPOTENT by convention: deleting an
          already-deleted resource should report success (or 404), not
          error out as if something new went wrong.

"Idempotent" is the load-bearing word here: a client (or a proxy, or a
retry-with-backoff helper like 11_system_design.py's) can safely resend an
idempotent request if it's unsure whether the first one arrived — resending
a POST without knowing that is how "I clicked buy once but got charged
twice" bugs happen.
"""


def demo_http_methods():
    print("\n--- HTTP Methods ---")
    print(HTTP_METHODS_NOTES)


# ---------------------------------------------------------------------------
# Cookies vs. Sessions
# ---------------------------------------------------------------------------
COOKIES_VS_SESSIONS_NOTES = """
Cookie: a small piece of data the SERVER asks the BROWSER to store and
send back on every subsequent request to that domain.

Session: server-side state, usually IDENTIFIED by a cookie. Flask's
`session` object stores data server-side (or signed/encrypted in the
cookie itself, for Flask's default), keyed by a session ID cookie the
browser sends back automatically.

  request.cookies       -> read cookies the browser sent
  response.set_cookie()  -> ask the browser to store a NEW cookie
  session['user_id'] = 1  -> Flask handles the cookie plumbing for you

Security notes:
  - Set cookies with `httponly=True` so JavaScript can't read them (XSS mitigation)
  - Set `secure=True` so they're only sent over HTTPS
  - Set `samesite='Lax'` or `'Strict'` to reduce CSRF risk
"""


# ---------------------------------------------------------------------------
# A tiny live Flask app to actually SEE headers/cookies/sessions in the browser
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config["SECRET_KEY"] = "demo-only-not-for-production"   # fine here: throwaway learning app


@app.route("/")
def index():
    return """
    <h2>14_web_fundamentals demo</h2>
    <p>Open your browser dev tools -> Network tab, then reload this page.</p>
    <p>Look at the Response Headers for this request.</p>
    <p><a href="/whoami">/whoami</a> — sets a cookie and a session value</p>
    <p><a href="/cached-data">/cached-data</a> — demonstrates a Cache-Control header</p>
    <p><a href="/api/cors-demo">/api/cors-demo</a> — demonstrates a CORS header</p>
    """


@app.route("/whoami")
def whoami():
    visit_count = session.get("visits", 0) + 1
    # New words in this line:
    #   session  -> behaves like a dict (.get() with a default, same as any
    #        dict) — but Flask transparently signs and stores it in a
    #        cookie on the response, and reads it back from the request's
    #        cookie on the next visit
    session["visits"] = visit_count

    response = make_response(f"<p>This is visit #{visit_count} in your session.</p>")
    # New words in this line:
    #   make_response(body)  -> wraps a response body in a Response object
    #        you can still modify (add cookies/headers) before it's actually
    #        sent — returning a plain string from a route does this same
    #        wrapping automatically, but without giving you a variable to
    #        attach a cookie to
    response.set_cookie(
        "last_seen", "just now",
        httponly=True,   # JavaScript can't read this cookie
        samesite="Lax",  # reduces CSRF exposure
    )
    # New words in this line:
    #   .set_cookie(name, value, **options)  -> tells the BROWSER to store
    #        this cookie and send it back on future requests
    return response


@app.route("/cached-data")
def cached_data():
    response = make_response('{"leaderboard": ["Alice", "Bob"]}')
    response.headers["Content-Type"] = "application/json"
    # New words in this line:
    #   response.headers[...] = ...  -> .headers behaves like a dict —
    #        assigning a key sets that HTTP response header
    response.headers["Cache-Control"] = "public, max-age=60"   # browser can reuse this for 60s
    return response


@app.route("/api/cors-demo")
def cors_demo():
    response = make_response('{"message": "cross-origin request allowed"}')
    response.headers["Content-Type"] = "application/json"
    response.headers["Access-Control-Allow-Origin"] = "https://trusted-frontend.example.com"
    # New words in this line:
    #   Access-Control-Allow-Origin  -> a response header telling the
    #        BROWSER "javascript running on this listed origin is allowed to
    #        read this response." Without it, a browser (not the server!)
    #        blocks frontend JS on a different origin from reading the
    #        response body at all, even though the request itself succeeded.
    return response


def demo_cors_notes():
    print("\n--- CORS (Cross-Origin Resource Sharing) ---")
    print("""
"Origin" = scheme + domain + port. https://app.example.com and
https://api.example.com are DIFFERENT origins, even though they share a
parent domain — as are http://localhost:3000 and http://localhost:5000.

The browser's SAME-ORIGIN POLICY blocks JavaScript on one origin from
reading responses from a different origin BY DEFAULT — this is a browser
security feature, not something the server can bypass by trying harder,
and it's exactly what makes the CSRF defense in 09_security.py's demo_csrf()
possible in the first place (an attacker's page can't read YOUR site's
real CSRF token).

CORS is the server explicitly OPTING BACK IN for specific origins, via
response headers — see /api/cors-demo above:
    Access-Control-Allow-Origin: https://trusted-frontend.example.com
    Access-Control-Allow-Methods: GET, POST
    Access-Control-Allow-Headers: Content-Type, Authorization

This matters constantly in real Flask apps: a React/Vue frontend running
on localhost:3000 during development calling a Flask API on localhost:5000
IS a cross-origin request — "CORS error" in the browser console the first
time you wire up a separate frontend is one of the most common early
integration bugs. In real Flask projects, Flask-CORS (`pip install
flask-cors`, then `CORS(app)`) handles the headers for you instead of
setting them by hand on every single route like the demo above does.
""")


def demo_websocket_notes():
    print("\n--- WebSockets (notes) ---")
    print("""
HTTP is request/response: the client always initiates. A WebSocket is a
persistent, two-way connection — either side can push a message anytime
without the other having asked first.

Relevant here: a Discord bot (see discord_bot.py elsewhere in this
workspace) is built on exactly this idea — discord.py holds one
long-lived WebSocket connection to Discord's gateway, so Discord can
PUSH events (a message was sent, a role changed) to the bot instantly,
instead of the bot having to poll "did anything happen yet?" every second.

For a Flask app wanting the same push behavior to a browser (e.g. a live
leaderboard that updates without refreshing), you'd reach for
Flask-SocketIO or plain `websockets`, rather than HTTP polling.
""")


if __name__ == "__main__":
    demo_status_codes()
    demo_http_methods()
    print(COOKIES_VS_SESSIONS_NOTES)
    demo_cors_notes()
    demo_websocket_notes()
    print("\nStarting demo Flask server on http://127.0.0.1:5050 (Ctrl+C to stop)...")
    app.run(port=5050, debug=True, use_reloader=False)
    # New words in this line:
    #   use_reloader=False  -> normally debug=True ALSO starts a background
    #        process that restarts the server whenever a file changes. That
    #        reloader doesn't play well with running this file
    #        non-interactively (as a demo/test run), so it's switched off
    #        here; in everyday dev work you'd usually leave the reloader on
