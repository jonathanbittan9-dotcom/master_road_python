"""
04_software_architecture.py

Section 4: Software Architecture
    - Layered architecture (routes -> services -> data access)
    - Dependency injection
    - Domain modeling (real objects instead of raw dicts)
    - Monolith vs. microservices tradeoffs (notes)
    - Event-driven basics (simple pub/sub)
    - API design conventions
    - Config management (env vars, not hardcoded secrets)

This file simulates a tiny "Books" feature the way it SHOULD be layered,
as a contrast to cramming routes + queries + logic into one 14,000-line file.

Run: python 04_software_architecture.py
"""

import os
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Layer 1: Domain models (what a "Book" IS — not what a route needs today)
# ---------------------------------------------------------------------------
@dataclass
class Book:
    id: str
    title: str
    author: str
    available: bool = True

    def borrow(self):
        if not self.available:
            raise ValueError(f"'{self.title}' is already borrowed")
        self.available = False

    def return_book(self):
        self.available = True


# ---------------------------------------------------------------------------
# Layer 2: Data access (Repository pattern — hides HOW data is stored)
# ---------------------------------------------------------------------------
class BookRepository:
    """
    Today this is an in-memory dict. Tomorrow it could be MongoDB or SQL.
    Nothing above this layer needs to know or care which.
    """
    def __init__(self):
        self._books: dict[str, Book] = {}

    def add(self, book: Book):
        self._books[book.id] = book

    def get(self, book_id: str) -> Book | None:
        # (`X | None` union-type syntax already introduced in
        # 02_oop_design_principles.py's BookRepository.get — same idea here,
        # just returning a Book instead of a plain dict.)
        return self._books.get(book_id)

    def all(self) -> list[Book]:
        return list(self._books.values())
        # New words in this line:
        #   .values()  -> dict method returning a view of just the VALUES
        #        (ignoring the keys) — list(...) then turns that view into
        #        a plain list


# ---------------------------------------------------------------------------
# Layer 3: Services (business logic — the "rules" of the app live here,
# NOT in the route handler)
# ---------------------------------------------------------------------------
class BookService:
    def __init__(self, repository: BookRepository):   # dependency injection:
        self.repository = repository                   # the service doesn't
                                                          # create its own repo,
                                                          # it's handed one

    def borrow_book(self, book_id: str) -> str:
        book = self.repository.get(book_id)
        if book is None:
            raise LookupError(f"No book with id {book_id}")
            # New words in this line:
            #   LookupError  -> a built-in exception (like TypeError/ValueError
            #        seen earlier) meaning "tried to look something up by a
            #        key/index and it wasn't there" — KeyError and IndexError
            #        are actually more specific subclasses of this same exception
        book.borrow()
        return f"You borrowed '{book.title}'"

    def list_available(self) -> list[Book]:
        return [b for b in self.repository.all() if b.available]


# ---------------------------------------------------------------------------
# Layer 4: Routes / controllers (THIN — just translate HTTP <-> service calls)
# ---------------------------------------------------------------------------
def fake_route_borrow(service: BookService, book_id: str):
    """
    This is what a Flask route SHOULD look like: a couple lines that
    delegate to a service, with no business logic or DB queries inline.

        @app.route("/borrow/<book_id>")
        def borrow(book_id):
            try:
                message = book_service.borrow_book(book_id)
                return jsonify({"message": message}), 200
            except LookupError:
                return jsonify({"error": "not found"}), 404
            except ValueError as e:
                return jsonify({"error": str(e)}), 409
    """
    try:
        message = service.borrow_book(book_id)
        return {"status": 200, "body": {"message": message}}
    except LookupError:
        return {"status": 404, "body": {"error": "not found"}}
    except ValueError as e:
        return {"status": 409, "body": {"error": str(e)}}


def demo_layered_architecture():
    print("\n--- Layered Architecture + Dependency Injection ---")

    repo = BookRepository()
    repo.add(Book(id="1", title="1984", author="Orwell"))
    repo.add(Book(id="2", title="Dune", author="Herbert", available=False))

    service = BookService(repo)   # inject the repo into the service

    print(fake_route_borrow(service, "1"))   # succeeds
    print(fake_route_borrow(service, "2"))   # already borrowed -> 409
    print(fake_route_borrow(service, "99"))  # doesn't exist -> 404

    print("still available:", [b.title for b in service.list_available()])


# ---------------------------------------------------------------------------
# Domain modeling: dicts vs real objects
# ---------------------------------------------------------------------------
def demo_dict_vs_domain_model():
    print("\n--- Dicts vs. Domain Models ---")

    # This is what main.py does everywhere: pass raw dicts around.
    # Nothing stops you from typo-ing a key, and there's no validation.
    book_dict = {"titel": "1984", "availble": True}   # typos silently "work"
    print("dict version (typos go unnoticed):", book_dict)

    # A real domain model catches this at the boundary instead of at 2am in prod.
    try:
        Book(id="1", titel="1984")   # type: ignore  # TypeError: unexpected keyword
    except TypeError as e:
        print("Expected error (dataclass caught the typo):", e)


# ---------------------------------------------------------------------------
# Immutable domain models: frozen=True
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
# New words in this line:
#   @dataclass(frozen=True)  -> same @dataclass decorator, but this option
#        makes every instance IMMUTABLE after __init__ runs: any attempt to
#        assign to an attribute afterward raises an error instead of quietly
#        succeeding. Compare to Book above, an ordinary (mutable) dataclass —
#        Book.borrow() is ALLOWED to do self.available = False specifically
#        because Book isn't frozen.
class Money:
    """A value object: two Money(10, 'USD') are interchangeable, so nothing
    should ever need to mutate one in place — replacing it is always correct
    instead."""
    amount: int
    currency: str

    def add(self, other: "Money") -> "Money":
        # New words in this line:
        #   "Money" (as a type hint, in quotes)  -> a "forward reference" —
        #        needed because Money isn't fully DEFINED yet at the point
        #        this line is read (we're still inside its own class body),
        #        so the type has to be given as a string for now
        if other.currency != self.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)
        # New words in this line:
        #   return Money(...) (a NEW instance)  -> since Money can't be
        #        mutated, "adding" money means building and returning a
        #        brand-new Money instead of changing self.amount in place


def demo_frozen_dataclass():
    print("\n--- Immutable Domain Models (frozen=True) ---")

    price = Money(1000, "USD")
    tax = Money(80, "USD")
    total = price.add(tax)
    print("price:", price, "-> unchanged")
    print("total:", total, "-> a NEW object")

    try:
        price.amount = 9999   # type: ignore
    except Exception as e:
        # dataclasses raises dataclasses.FrozenInstanceError here, which IS
        # a subclass of AttributeError — catching the broader Exception type
        # keeps this demo simple without needing a new import just to name it
        print("Expected error (frozen instance rejects mutation):", type(e).__name__, e)
    # Why bother: a mutable Book being passed around several functions can be
    # silently changed by any of them, which is a common source of "who
    # changed this?!" bugs. An immutable Money can't be — every function that
    # touches it either uses it as-is or hands back a new one, so nothing
    # else holding a reference to the original is ever surprised.


# ---------------------------------------------------------------------------
# Feature flags: ship code disabled, turn it on without a redeploy
# ---------------------------------------------------------------------------
class FeatureFlags:
    """
    Real systems (LaunchDarkly, Flagsmith, or even just a config table in the
    DB) let you flip this at runtime without redeploying. This in-memory
    version exists only to show the SHAPE of the pattern.
    """
    def __init__(self, flags: dict[str, bool] | None = None):
        self._flags = flags or {}

    def is_enabled(self, name: str) -> bool:
        return self._flags.get(name, False)


def list_available_books_v2(books: list[Book]) -> list[Book]:
    """A rewritten version of BookService.list_available(), guarded by a flag."""
    return sorted((b for b in books if b.available), key=lambda b: b.title)
    # New words in this line:
    #   sorted(generator, key=...)  -> sorted() accepts any iterable, not
    #        just a list — this generator expression feeds it lazily


def demo_feature_flags():
    print("\n--- Feature Flags ---")

    books = [Book(id="1", title="1984", author="Orwell"),
             Book(id="2", title="Animal Farm", author="Orwell")]

    flags_off = FeatureFlags({"sorted_book_listing": False})
    flags_on = FeatureFlags({"sorted_book_listing": True})

    for flags in (flags_off, flags_on):
        if flags.is_enabled("sorted_book_listing"):
            result = list_available_books_v2(books)
            print("v2 (sorted) listing:", [b.title for b in result])
        else:
            result = [b for b in books if b.available]
            print("v1 (original) listing:", [b.title for b in result])
    # The payoff: the NEW code path shipped to production already, disabled.
    # Turning it on for 5% of users, or instantly rolling it back if it
    # misbehaves, is a config change — not a deploy.


# ---------------------------------------------------------------------------
# Event-driven basics: simple pub/sub instead of tightly coupled calls
# ---------------------------------------------------------------------------
class EventBus:
    def __init__(self):
        self._handlers: dict[str, list] = {}

    def on(self, event_name: str, handler):
        self._handlers.setdefault(event_name, []).append(handler)
        # New words in this line:
        #   .setdefault(key, default)  -> dict method: "if key exists,
        #        return its current value; otherwise SET it to `default`
        #        and return that." Replaces the more verbose:
        #            if event_name not in self._handlers:
        #                self._handlers[event_name] = []
        #            self._handlers[event_name].append(handler)
        #        with one line. (defaultdict, from Section 1, solves the
        #        same problem a different way — prefer defaultdict for a
        #        dict you use everywhere; setdefault is handy for one-off cases.)

    def emit(self, event_name: str, **payload):
        for handler in self._handlers.get(event_name, []):
            handler(**payload)


def demo_event_driven():
    print("\n--- Event-Driven (pub/sub) ---")

    bus = EventBus()
    bus.on("book_borrowed", lambda title: print(f"[email service] Sending receipt for '{title}'"))
    bus.on("book_borrowed", lambda title: print(f"[analytics] Logging borrow event for '{title}'"))

    bus.emit("book_borrowed", title="1984")
    # The borrowing code doesn't need to know email/analytics exist at all —
    # this is how you avoid one giant function that does 10 unrelated things.


# ---------------------------------------------------------------------------
# Config management: env vars instead of hardcoded secrets
# ---------------------------------------------------------------------------
def demo_config_management():
    print("\n--- Config Management ---")

    # Bad (seen in main.py):
    #   app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
    # The fallback string means prod silently runs with a KNOWN, public secret
    # if the env var is ever missing.

    secret_key = os.environ.get("SECRET_KEY")
    # New words in this line:
    #   os.environ  -> a dict-like object holding the current process's
    #        environment variables
    #   .get("SECRET_KEY")  -> same .get(key) method dicts have — returns
    #        None if that environment variable isn't set, instead of raising
    #        an error. Environment variables are how config/secrets get INTO
    #        a process without hardcoding them in source code — set via the
    #        shell, a `.env` file, or the hosting platform.
    if not secret_key:
        raise RuntimeError("SECRET_KEY is not set — refuse to start rather than use a guessable default")
        # New words in this line:
        #   RuntimeError  -> a built-in exception used as a catch-all for
        #        "something is wrong with the state of the program" when no
        #        more specific built-in exception fits

    print("This branch only prints if SECRET_KEY is actually set in the environment.")


if __name__ == "__main__":
    demo_layered_architecture()
    demo_dict_vs_domain_model()
    demo_frozen_dataclass()
    demo_feature_flags()
    demo_event_driven()

    try:
        demo_config_management()
    except RuntimeError as e:
        print("\n--- Config Management ---")
        print("Expected error (this is the point):", e)
