"""
15_flask_architecture_and_requests.py

Section 15: Flask Architecture & Request Handling
    - Application factory pattern (create_app())
    - Config classes (one per environment: dev/prod)
    - Blueprints — grouping related routes, attached to the app later
    - request.method, methods=["GET", "POST"]
    - redirect() + the Post/Redirect/Get pattern
    - flash() + get_flashed_messages()
    - abort() and @app.errorhandler
    - before_request / after_request hooks, flask.g

Run: python 15_flask_architecture_and_requests.py
Then visit: http://127.0.0.1:5051/
"""
import time
from flask import (
    Flask, Blueprint, request, redirect, url_for, flash,
    render_template_string, abort, g, jsonify, current_app,
)
# New words in this line (beyond testlearn.py's Flask basics and
# 14_web_fundamentals.py's request/make_response/session):
#   Blueprint              -> a way to group related routes in their own
#        object, then attach them to an app later with register_blueprint()
#   redirect               -> builds a response telling the browser "go
#        fetch this OTHER url instead"
#   flash                  -> stashes a one-time message in the session, to
#        be shown on the NEXT page rendered (e.g. "Book borrowed!")
#   render_template_string -> like render_template(), but the template text
#        is a Python string instead of a file in templates/ — used here so
#        this file has no external template-file dependency
#   abort                  -> immediately stops the request and returns an
#        HTTP error status (e.g. abort(404))
#   g                      -> "global" per-REQUEST storage; a blank object
#        Flask resets before every request, for passing data between
#        before_request and the view function that handles the request


# ---------------------------------------------------------------------------
# Config classes — one class per environment
# ---------------------------------------------------------------------------
class BaseConfig:
    SECRET_KEY = "demo-only-not-for-production"   # needed for session/flash
    SITE_NAME = "Senior Path Library"


class DevConfig(BaseConfig):
    DEBUG = True


class ProdConfig(BaseConfig):
    DEBUG = False
    # In real code: SECRET_KEY = os.environ["SECRET_KEY"], a real DB url, etc.
    # New words in this line:
    #   os.environ["NAME"] (square brackets, not .get())  -> raises KeyError
    #        if the variable is missing, instead of silently returning None —
    #        deliberate here for a required production secret, unlike
    #        04_software_architecture.py's os.environ.get("NAME")


# ---------------------------------------------------------------------------
# A Blueprint — a self-contained group of routes
# ---------------------------------------------------------------------------
books_bp = Blueprint("books", __name__, url_prefix="/books")
# New words in this line:
#   Blueprint(name, import_name, url_prefix=...)  -> `name` is what url_for
#        uses internally (url_for("books.list_books")); url_prefix is
#        prepended to every route defined on this blueprint

BOOKS = {1: {"title": "1984", "available": True}, 2: {"title": "Dune", "available": False}}


@books_bp.route("/")
def list_books():
    rows = "".join(
        f"<li>{b['title']} — {'available' if b['available'] else 'borrowed'}</li>"
        for b in BOOKS.values()
    )
    site_name = current_app.config["SITE_NAME"]
    # New words in this line:
    #   current_app  -> a PROXY that always points at whichever Flask app is
    #        handling the CURRENT request, without this module needing to
    #        import `app` directly. That matters specifically here: this
    #        function lives in books_bp, a Blueprint — it has no `app`
    #        variable in scope at all (create_app() builds `app` in a
    #        DIFFERENT function, further down this file), yet current_app
    #        still resolves correctly, because Flask tracks which app is
    #        "active" per-request behind the scenes.
    return f"<h3>{site_name}</h3><ul>{rows}</ul>"


@books_bp.route("/<int:book_id>/borrow", methods=["GET", "POST"])
# New words in this line:
#   methods=["GET", "POST"]  -> without this, a route only answers GET.
#        Listing POST here lets the SAME url show a confirm page (GET) and
#        process the form submit (POST).
def borrow_book(book_id):
    book = BOOKS.get(book_id)
    if book is None:
        abort(404)   # short-circuits here; nothing below this line runs

    if request.method == "POST":
        if not book["available"]:
            flash("That book is already borrowed.", "error")
        else:
            book["available"] = False
            flash(f"You borrowed {book['title']}!", "success")
        return redirect(url_for("books.list_books"))
        # New words in this line:
        #   redirect(url_for(...))  -> the Post/Redirect/Get pattern: after a
        #        POST that changes state, send the browser a redirect to a
        #        GET url instead of rendering a page directly. Refreshing the
        #        resulting page re-runs the GET, not the POST — no "resubmit
        #        form?" browser warning.

    return render_template_string(
        "<p>Borrow '{{ book.title }}'?</p>"
        "<form method='post'><button type='submit'>Confirm</button></form>"
        "{% with messages = get_flashed_messages(with_categories=true) %}"
        "{% for category, msg in messages %}<p>[{{ category }}] {{ msg }}</p>{% endfor %}"
        "{% endwith %}",
        book=book,
    )


# ---------------------------------------------------------------------------
# before_request / after_request + g
# ---------------------------------------------------------------------------
def register_hooks(app):
    @app.before_request
    # New words in this line:
    #   @app.before_request  -> registers a function that runs before EVERY
    #        request, for every route, without decorating each one by hand
    def start_timer():
        g.start = time.perf_counter()
        # New words in this line:
        #   g.start = ...  -> g is reset fresh for each request, so this
        #        can't leak between different visitors' requests

    @app.after_request
    # New words in this line:
    #   @app.after_request  -> runs after the view function returns, and
    #        receives the response object — must return it (possibly
    #        modified) so Flask can actually send it
    def log_duration(response):
        elapsed_ms = (time.perf_counter() - g.start) * 1000
        response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.2f}"
        return response

    @app.errorhandler(404)
    # New words in this line:
    #   @app.errorhandler(404)  -> replaces Flask's default HTML 404 page
    #        with whatever this function returns, for every abort(404) and
    #        every genuinely unmatched url
    def not_found(error):
        return jsonify(error="not found", detail=str(error)), 404
        # New words in this line:
        #   return (body, status)  -> returning a tuple from a view sets the
        #        HTTP status code explicitly (it's always 200 otherwise)


# ---------------------------------------------------------------------------
# The application factory
# ---------------------------------------------------------------------------
def create_app(config_class=DevConfig):
    # New words in this line:
    #   create_app(...)  -> the "application factory" pattern: instead of one
    #        module-level `app = Flask(__name__)` (as in hello.py/testlearn.py),
    #        wrap creation in a function. Lets you build MULTIPLE app
    #        instances with different configs — one for tests, one for dev,
    #        one for prod — with none of them a shared global.
    app = Flask(__name__)
    app.config.from_object(config_class)
    # New words in this line:
    #   app.config.from_object(SomeClass)  -> copies every UPPERCASE
    #        attribute off the class onto app.config

    app.register_blueprint(books_bp)
    # New words in this line:
    #   register_blueprint(bp)  -> actually attaches the blueprint's routes
    #        to THIS app instance

    register_hooks(app)

    @app.route("/")
    def index():
        return "<p>Section 15 demo. Try <a href='/books/'>/books/</a></p>"

    return app


# ---------------------------------------------------------------------------
# Application Context vs. Request Context
# ---------------------------------------------------------------------------
APP_VS_REQUEST_CONTEXT_NOTES = """
Flask actually tracks TWO separate stacks, not one:

  Application context  -> makes current_app and g valid. Pushed whenever
      Flask needs to know "which app is this?" — automatically during a
      real request, but also manually when you need app-aware code OUTSIDE
      of one (16_flask_data_auth_apis.py's `with app.app_context():` at
      startup, before any request has happened, is exactly this case).

  Request context      -> makes request and session valid. Only exists
      while an actual HTTP request is being handled — pushing a request
      context ALSO pushes an application context along with it, since you
      can't have a request without knowing which app it's for, but not the
      other way around.

Why this distinction matters in practice: current_app works during
db.create_all() at startup in 16_flask_data_auth_apis.py, because
app.app_context() was pushed — but request would NOT work there, because
there's no actual incoming request at startup. Reaching for `request` or
`session` outside of an active view function (e.g. in a background job,
or a script run at import time) raises RuntimeError: Working outside of
request context — current_app / g are the ones that also work at startup.
"""


def demo_context_notes():
    print("\n--- Application Context vs. Request Context ---")
    print(APP_VS_REQUEST_CONTEXT_NOTES)


# ---------------------------------------------------------------------------
# Exercise every piece above without a real browser
# ---------------------------------------------------------------------------
def demo_client(app):
    print("\n--- Exercising routes with app.test_client() ---")
    client = app.test_client()
    # New words in this line:
    #   app.test_client()  -> a fake HTTP client that calls your routes
    #        directly in-process — no real server/socket needed, which is why
    #        tests using it run in milliseconds

    resp = client.get("/books/")
    print("GET /books/ ->", resp.status_code)
    assert resp.status_code == 200
    assert b"Senior Path Library" in resp.data   # proves current_app.config resolved correctly

    resp = client.get("/books/1/borrow")
    print("GET /books/1/borrow ->", resp.status_code)
    assert resp.status_code == 200

    resp = client.post("/books/1/borrow", follow_redirects=True)
    # New words in this line:
    #   follow_redirects=True  -> the test client normally stops AT the
    #        redirect response (302); this makes it automatically follow it
    #        and return the FINAL page, the way a real browser would
    print("POST /books/1/borrow (followed) ->", resp.status_code)
    assert resp.status_code == 200
    assert b"borrowed" in resp.data

    resp = client.get("/nope")
    print("GET /nope ->", resp.status_code, resp.get_json())
    assert resp.status_code == 404


if __name__ == "__main__":
    demo_context_notes()
    app = create_app(DevConfig)
    demo_client(app)
    print("\nStarting demo Flask server on http://127.0.0.1:5051 (Ctrl+C to stop)...")
    app.run(port=5051, debug=True, use_reloader=False)
