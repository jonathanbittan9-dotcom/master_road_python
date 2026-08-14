"""
core_language_mastery.py

Companion file to testlearn.py — walks through Section 1 (Core Language
Mastery) mini-subjects one at a time, each in its own function so you can
run them individually and see the output for each concept in isolation.

Run the whole file top to bottom:
    python core_language_mastery.py
"""

import time
import functools
from contextlib import contextmanager
from dataclasses import dataclass
from collections import Counter, defaultdict
from itertools import chain
from typing import Optional, Union


# ---------------------------------------------------------------------------
# 1. Mutability & `is` vs `==`
# ---------------------------------------------------------------------------
def demo_mutability():
    print("\n--- Mutability & is/== ---")

    a = [1, 2, 3]
    b = a          # no new words here — plain assignment. The CONCEPT is new
                   # (b now refers to the same list object as a) but the
                   # syntax itself is identical to `x = 5` in testlearn.py.
    c = a.copy()
    # New words in this line:
    #   .copy()  -> list method: returns a brand-new list containing the
    #               same items, instead of pointing at the original list

    b.append(4)
    print("a:", a)  # [1, 2, 3, 4]  <- changed! b and a are the same object
    print("c:", c)  # [1, 2, 3]     <- unaffected, it's a separate copy

    print("a is b:", a is b)
    # New words in this line:
    #   is  -> identity operator: True only if both sides are literally the
    #          SAME object in memory (not just equal-looking values)
    print("a == c:", a == c)
    # New words in this line:
    #   ==  -> equality operator: True if both sides have the same VALUE,
    #          even if they're different objects in memory
    print("a is a:", a is a)   # True


# ---------------------------------------------------------------------------
# 2. Comprehensions — and when NOT to use them
# ---------------------------------------------------------------------------
def demo_comprehensions():
    print("\n--- Comprehensions ---")

    numbers = [1, 2, 3, 4, 5, 6]

    squares = [n ** 2 for n in numbers]
    # New words in this line:
    #   [ expr for item in iterable ]  -> list comprehension syntax: builds
    #                                     a new list by evaluating `expr`
    #                                     once per item
    #   **                              -> exponentiation operator (n to the
    #                                     power of 2)

    evens = [n for n in numbers if n % 2 == 0]
    # New words in this line:
    #   if (inside the brackets)  -> a comprehension filter: only items
    #                                where this is True get included
    #   %                          -> modulo operator: remainder after
    #                                integer division

    square_map = {n: n ** 2 for n in numbers}
    # New words in this line:
    #   { key_expr: value_expr for item in iterable }  -> dict comprehension
    #                                                     syntax: same idea
    #                                                     as a list
    #                                                     comprehension, but
    #                                                     builds a dict

    remainders = {n % 3 for n in numbers}
    # New words in this line:
    #   { expr for item in iterable }  -> set comprehension syntax: like a
    #                                     list comprehension, but the result
    #                                     auto-removes duplicate values

    lazy_squares = (n ** 2 for n in numbers)
    # New words in this line:
    #   ( expr for item in iterable )  -> generator expression: identical
    #                                     syntax to the others but with ()
    #                                     instead of [] — computes one value
    #                                     at a time instead of building the
    #                                     whole list upfront (see
    #                                     demo_generators() below for why
    #                                     that matters)

    print("squares:", squares)
    print("evens:", evens)
    print("square_map:", square_map)
    print("remainders (deduped):", remainders)
    print("lazy_squares (not computed yet):", lazy_squares)
    print("lazy_squares consumed:", list(lazy_squares))

    # When NOT to use a comprehension: if the logic needs multiple steps
    # or side effects, a comprehension makes it LESS readable, not more.
    # Prefer a plain loop when there's real logic per item:
    result = []
    for n in numbers:
        doubled = n * 2
        result.append(doubled)
    print("plain loop result:", result)


# ---------------------------------------------------------------------------
# 3. Iterators & Generators
# ---------------------------------------------------------------------------
def countdown(n):
    while n > 0:
        yield n
        # New words in this line:
        #   yield  -> pauses the function right here and hands `n` back to
        #             whoever is iterating; unlike `return`, everything the
        #             function was doing (including the value of `n`) stays
        #             frozen and picks back up right after this line the
        #             next time a value is requested. A function containing
        #             `yield` anywhere becomes a "generator function" —
        #             calling it doesn't run the body at all, it just
        #             creates a generator object (proven in
        #             demo_generators() below).
        n -= 1
    print("Liftoff!")


def squares_list(n):
    return [i ** 2 for i in range(n)]   # builds ALL of it in memory now


def squares_gen(n):
    for i in range(n):
        yield i ** 2                     # computes one at a time, on demand


def demo_generators():
    print("\n--- Iterators & Generators ---")

    for number in countdown(3):
        print(number)  # 3, 2, 1, then "Liftoff!"

    # Generators are lazy: nothing runs until you iterate
    gen = countdown(5)     # instant — no work done yet (proves yield above:
                           # if this were a normal function, calling it would
                           # already have started executing the while loop)
    first_value = next(gen)
    # New words in this line:
    #   next(x)  -> built-in function: manually pulls ONE value out of a
    #               generator/iterator, running the body only up to the
    #               next `yield`
    print("first_value:", first_value)

    print("squares_list(5):", squares_list(5))
    print("squares_gen(5):", list(squares_gen(5)))


# ---------------------------------------------------------------------------
# 4. Decorators — writing your own
# ---------------------------------------------------------------------------
def timer(func):
    @functools.wraps(func)
    # New words in this line:
    #   @                -> decorator syntax: applies whatever follows to
    #                       the function/method defined directly below it
    #   functools        -> standard library module full of tools for
    #                       working with functions themselves
    #   .wraps(func)     -> a decorator FACTORY (a function that returns a
    #                       decorator): copies func's __name__ and docstring
    #                       onto the function being decorated (`wrapper`
    #                       below) — without it, wrapper would masquerade as
    #                       a function literally named "wrapper", breaking
    #                       debugging/introspection tools
    def wrapper(*args, **kwargs):
        # New words in this line:
        #   *args     -> collects any number of extra POSITIONAL arguments
        #               into a tuple named `args`
        #   **kwargs  -> collects any number of extra KEYWORD arguments
        #               into a dict named `kwargs`
        start = time.perf_counter()
        # New words in this line:
        #   time.perf_counter()  -> stdlib function returning a
        #                          high-resolution timestamp meant for
        #                          measuring ELAPSED time between two calls
        #                          (not the actual date/clock time)
        result = func(*args, **kwargs)
        # New words in this line:
        #   *args (here)    -> UNPACKS the args tuple back into individual
        #                      positional arguments when calling func
        #   **kwargs (here) -> UNPACKS the kwargs dict back into individual
        #                      keyword arguments when calling func
        elapsed = time.perf_counter() - start
        print(f"{func.__na0me__} took {elapsed:.4f}s")
        # New words in this line:
        #   f"...{expr}..."  -> f-string: a string literal prefixed with f;
        #                       anything inside {curly braces} is evaluated
        #                       as a Python expression and inserted
        #   func.__name__    -> every function object automatically has a
        #                       __name__ attribute holding its name as text
        #   :.4f              -> a FORMAT SPEC inside the {}: display the
        #                       number as fixed-point with 4 digits after
        #                       the decimal point
        return result
    return wrapper


@timer
# New words in this line:
#   @timer  -> applies the `timer` function (defined above) as a decorator
#              to slow_add — shorthand for writing `slow_add = timer(slow_add)`
#              right after the function definition below
def slow_add(a, b):
    time.sleep(0.1)
    return a + b


def demo_decorators():
    print("\n--- Decorators ---")
    result = slow_add(2, 3)
    print("result:", result)
    # This is the same as: slow_add = timer(slow_add)
    # Flask's @app.route is doing exactly this kind of wrapping under the hood.


# ---------------------------------------------------------------------------
# 5. Context Managers — writing your own
# ---------------------------------------------------------------------------
class Timer:
    """Custom context manager using __enter__/__exit__"""
    def __enter__(self):
        # New words in this line:
        #   __enter__  -> a "dunder" (double-underscore) method Python calls
        #                automatically the moment a `with` block starts, on
        #                whatever object follows `with`
        self.start = time.perf_counter()
        return self   # this becomes the `as x` value

    def __exit__(self, exc_type, exc_value, traceback):
        # New words in this line:
        #   __exit__                              -> the dunder method
        #        Python calls automatically when a `with` block ends,
        #        whether it ended normally or because of an exception
        #   exc_type, exc_value, traceback  -> three parameters describing
        #        any exception that happened inside the `with` block — all
        #        three are None if nothing went wrong
        elapsed = time.perf_counter() - self.start
        print(f"Block took {elapsed:.4f}s")
        return False
        # New words in this line:
        #   return False (specifically from __exit__)  -> tells Python "do
        #        NOT swallow the exception" — it keeps propagating normally
        #        after this method returns. Returning True here would
        #        silently suppress any exception that occurred.


@contextmanager
# New words in this line:
#   @contextmanager  -> a decorator imported from the contextlib module;
#        turns an ordinary generator function into something usable with
#        `with`, without having to write a whole class with
#        __enter__/__exit__ like Timer above
def timer_cm():
    start = time.perf_counter()
    yield
    # New words in this line:
    #   yield (with no value)  -> marks the dividing line between "setup"
    #        code (everything above, acting like __enter__) and "teardown"
    #        code (everything below, acting like __exit__). The code inside
    #        the `with` block runs during this exact pause.
    print(f"Took {time.perf_counter() - start:.4f}s")


def demo_context_managers():
    print("\n--- Context Managers ---")

    with Timer():
        # New words in this line:
        #   with EXPR:  -> starts a context-managed block. Calls
        #        EXPR.__enter__() (or runs the generator up to its first
        #        `yield`) when the block starts, and __exit__() (or resumes
        #        after `yield`) when it ends — even if an exception occurs
        #        inside the block.
        time.sleep(0.15)

    with timer_cm():
        time.sleep(0.15)


# ---------------------------------------------------------------------------
# 6. *args, **kwargs
# ---------------------------------------------------------------------------
def describe(*args, **kwargs):
    # (Same *args/**kwargs syntax already introduced above, in the timer
    # decorator — no new words on this line; this function exists purely to
    # show what ends up INSIDE args/kwargs when you print them.)
    print("positional:", args)      # tuple: (1, 2, 3)
    print("keyword:", kwargs)       # dict: {'name': 'Bob'}


def add(a, b, c):
    return a + b + c


def demo_args_kwargs():
    print("\n--- *args / **kwargs ---")

    describe(1, 2, 3, name="Bob")

    # Unpacking when CALLING a function
    nums = [1, 2, 3]
    print("add(*nums):", add(*nums))
    # New words in this line:
    #   *nums (when CALLING)  -> unpacks the list `nums` into three separate
    #        positional arguments — add(*nums) runs exactly like add(1, 2, 3)

    info = {"a": 1, "b": 2, "c": 3}
    print("add(**info):", add(**info))
    # New words in this line:
    #   **info (when CALLING)  -> unpacks the dict `info` into keyword
    #        arguments matching its keys — add(**info) runs exactly like
    #        add(a=1, b=2, c=3)


# ---------------------------------------------------------------------------
# 7. Closures (global, nonlocal)
# ---------------------------------------------------------------------------
def make_counter():
    count = 0                    # this variable is "closed over" — the
                                  # inner function below keeps a reference to
                                  # it even after make_counter() has returned

    def increment():
        nonlocal count
        # New words in this line:
        #   nonlocal  -> tells Python "the `count` I'm about to modify
        #        belongs to the ENCLOSING function's scope, not a new local
        #        variable." Without this line, `count += 1` below would
        #        raise UnboundLocalError, because assigning to a name inside
        #        a function normally creates a brand-new local variable by
        #        that name.
        count += 1
        return count

    return increment   # this "closure" — a function bundled with the
                        # variables it needs from its enclosing scope — is
                        # what lets each call to make_counter() produce an
                        # independent counter with its own private `count`


def demo_closures():
    print("\n--- Closures ---")

    counter = make_counter()
    print(counter())  # 1
    print(counter())  # 2
    print(counter())  # 3 — each call remembers state, no class needed


# ---------------------------------------------------------------------------
# 8. Exception Hierarchy — custom exceptions
# ---------------------------------------------------------------------------
class BookNotFoundError(Exception):
    # New words in this line:
    #   Exception       -> the built-in base class that nearly every
    #        exception (built-in or custom) ultimately inherits from
    #   (Exception) here -> ordinary inheritance syntax (same as testlearn.py's
    #        Ebook(Book)) — BookNotFoundError IS-A Exception
    """Raised when a requested book doesn't exist."""
    pass
    # New words in this line:
    #   pass  -> a statement that does literally nothing — used here as a
    #        placeholder body because this class needs no extra code beyond
    #        what it inherits from Exception


class BookUnavailableError(Exception):
    """Raised when a book exists but is already borrowed."""
    def __init__(self, title):
        self.title = title
        super().__init__(f"'{title}' is currently borrowed")
        # New words in this line:
        #   super()        -> refers to the parent class (Exception) so you
        #        can call ITS version of a method
        #   .__init__(...)  -> calling the parent class's constructor
        #        directly, here to store the message so str(e)/print(e)
        #        shows it automatically


def borrow_book(book, catalog):
    if book not in catalog:
        raise BookNotFoundError(f"No such book: {book}") 
        # New words in this line:
        #   raise  -> immediately stops normal execution and hands control
        #        to the nearest enclosing `except` clause that matches this
        #        exception's type (or crashes the program if none does)
    if not catalog[book]:
        raise BookUnavailableError(book)
    return f"You borrowed {book}"


def demo_exceptions():
    print("\n--- Custom Exceptions ---")

    try:
        borrow_book("1984", {"1984": False})
    except BookUnavailableError as e:
        # New words in this line:
        #   except TYPE as e  -> catches an exception of this specific type
        #        (or a subclass of it) and binds it to the local name `e`
        #        so you can inspect/print it
        #   (multiple except clauses, as used here) -> Python checks them
        #        top to bottom and runs only the FIRST one whose type matches
        print(f"Handled: {e}")
    except BookNotFoundError as e:
        print(f"Handled: {e}")
    finally:
        # New words in this line:
        #   finally  -> a block that runs no matter what happened above —
        #        exception, return, or neither — typically used for cleanup
        print("Always runs, cleanup goes here")


# ---------------------------------------------------------------------------
# 9. Type Hints
# ---------------------------------------------------------------------------
def find_book(title: str, catalog: dict[str, bool]) -> Optional[bool]:
    # New words in this line:
    #   title: str               -> a type hint: documents that `title` is
    #        expected to be a string (Python does NOT enforce this at
    #        runtime — it's for readers and tools like mypy)
    #   dict[str, bool]           -> a generic type hint meaning "a dict
    #        whose keys are strings and whose values are bools"
    #   -> Optional[bool]         -> a return-type hint
    #   Optional[bool] (from typing)  -> means "a bool value, or None"
    """Returns availability, or None if not found."""
    return catalog.get(title)


def format_id(book_id: Union[int, str]) -> str:
    # New words in this line:
    #   Union[int, str] (from typing)  -> a type hint meaning "either an int
    #        or a str is acceptable here"
    return str(book_id).zfill(4)
    # New words in this line:
    #   .zfill(4)  -> string method: pads the string with leading zeros
    #        until it's 4 characters long


def demo_type_hints():
    print("\n--- Type Hints ---")
    print("find_book:", find_book("1984", {"1984": True}))
    print("find_book (missing):", find_book("Dune", {"1984": True}))
    print("format_id(7):", format_id(7))
    # Run `mypy core_language_mastery.py` to catch type errors before runtime


# ---------------------------------------------------------------------------
# 10. Standard Library: dataclasses, collections, itertools
# ---------------------------------------------------------------------------
@dataclass
# New words in this line:
#   @dataclass (from the dataclasses module)  -> a decorator that inspects
#        the type-annotated fields below and auto-generates __init__,
#        __repr__, and __eq__ for you — compare to testlearn.py's Book
#        class, which had to write __init__ and __repr__ by hand
class Book:
    title: str
    author: str
    available: bool = True   # default value — same idea as a normal
                              # function's default argument, just on a
                              # class field instead


def demo_stdlib():
    print("\n--- Standard Library (dataclasses, collections, itertools) ---")

    book = Book("1984", "Orwell")
    print(book)   # auto-generated __repr__: Book(title='1984', author='Orwell', available=True)

    genres = ["scifi", "drama", "scifi", "scifi", "drama"]
    print("Counter:", Counter(genres))
    # New words in this line:
    #   Counter(iterable) (from collections)  -> counts how many times each
    #        distinct item appears, returning a dict-like object of
    #        {item: count}

    by_author = defaultdict(list)
    # New words in this line:
    #   defaultdict(list) (from collections)  -> a dict subclass where
    #        looking up a MISSING key doesn't raise KeyError — it
    #        auto-creates a value using the function you passed in (here,
    #        `list`, so missing keys get a fresh empty list)
    by_author["Orwell"].append("1984")
    by_author["Orwell"].append("Animal Farm")
    print("defaultdict:", dict(by_author))

    all_titles = list(chain(["1984"], ["Animal Farm"], ["Homage to Catalonia"]))
    # New words in this line:
    #   chain(iter1, iter2, ...) (from itertools)  -> lazily joins multiple
    #        iterables into a single sequence, without building a combined
    #        list in memory first
    print("chained titles:", all_titles)


# ---------------------------------------------------------------------------
# 11. enumerate(), zip(), any(), all()
# ---------------------------------------------------------------------------
def demo_enumerate_zip_any_all():
    print("\n--- enumerate, zip, any, all ---")

    titles = ["1984", "Dune", "Foundation"]

    for index, title in enumerate(titles):
        # New words in this line:
        #   enumerate(iterable)  -> wraps an iterable so each item comes out
        #        paired with its position: (0, "1984"), (1, "Dune"), ... The
        #        alternative, `for i in range(len(titles)): titles[i]`, works
        #        but is considered unidiomatic Python — enumerate says the
        #        same thing more directly.
        print(f"  {index}: {title}")

    authors = ["Orwell", "Herbert", "Asimov"]
    for title, author in zip(titles, authors):
        # New words in this line:
        #   zip(iter1, iter2, ...)  -> walks multiple iterables IN PARALLEL,
        #        yielding one tuple per position: ("1984", "Orwell"), ("Dune",
        #        "Herbert"), ... Stops as soon as the SHORTEST input runs out,
        #        even if the others have more items left.
        print(f"  {title} by {author}")

    availability = [True, False, True]
    print("any available:", any(availability))
    # New words in this line:
    #   any(iterable)  -> built-in function: True if AT LEAST ONE item is
    #        truthy, False if every item is falsy (an empty iterable -> False)
    print("all available:", all(availability))
    # New words in this line:
    #   all(iterable)  -> built-in function: True only if EVERY item is
    #        truthy (an empty iterable -> True, perhaps surprisingly — there's
    #        no item to fail the check)


# ---------------------------------------------------------------------------
# 12. The Walrus Operator (:=)
# ---------------------------------------------------------------------------
def demo_walrus():
    print("\n--- Walrus operator := ---")

    catalog = {"1984": True, "Dune": False, "Foundation": True}

    # Without walrus: .get() gets called, then checked, as two separate steps
    result = catalog.get("1984")
    if result is not None:
        print("without walrus:", result)

    # With walrus: assign AND test the value in the same expression
    if (result := catalog.get("Dune")) is not None:
        # New words in this line:
        #   (name := expr)  -> the walrus operator (Python 3.8+): evaluates
        #        expr, assigns it to `name`, AND the whole parenthesized thing
        #        evaluates to that same value — so it can sit directly inside
        #        an `if` condition instead of needing a separate assignment
        #        line above it. The parentheses around it are required syntax
        #        here, not optional style.
        print("with walrus:", result)

    # Common real use: avoid calling an expensive function twice
    long_titles = [t for t in catalog if (length := len(t)) > 5]
    print("titles longer than 5 chars:", long_titles, "(len computed once per title, not twice)")


# ---------------------------------------------------------------------------
# 13. functools.lru_cache — automatic memoization
# ---------------------------------------------------------------------------
@functools.lru_cache(maxsize=None)
# New words in this line:
#   @functools.lru_cache(maxsize=...)  -> a decorator (same @ syntax as
#        @timer above) that automatically remembers this function's return
#        value for each distinct set of arguments it's called with — the
#        SAME idea as the hand-written `cache = {}` dict you'll build
#        yourself in 03_data_structures_algorithms.py's fib_memo(), except
#        the standard library does the caching for you
#   maxsize=None  -> no limit on how many distinct argument-combinations get
#        cached (pass a number instead to cap it, evicting least-recently-used
#        entries once full — the same idea as 11_system_design.py's LRUCache)
def slow_square(n):
    time.sleep(0.1)   # pretend this is expensive
    return n * n


def demo_lru_cache():
    print("\n--- functools.lru_cache ---")

    start = time.perf_counter()
    slow_square(5)
    first_call = time.perf_counter() - start

    start = time.perf_counter()
    slow_square(5)   # same argument as before -> returns the cached result instantly
    second_call = time.perf_counter() - start

    print(f"first call:  {first_call:.4f}s (actually ran)")
    print(f"second call: {second_call:.4f}s (served from cache)")
    print("cache info:", slow_square.cache_info())
    # New words in this line:
    #   .cache_info()  -> every lru_cache-wrapped function gets this method
    #        for free, reporting hits/misses/current size — useful for
    #        confirming the cache is actually doing something


# ---------------------------------------------------------------------------
# Run everything
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    demo_mutability()
    demo_comprehensions()
    demo_generators()
    demo_decorators()
    demo_context_managers()
    demo_args_kwargs()
    demo_closures()
    demo_exceptions()
    demo_type_hints()
    demo_stdlib()
    demo_enumerate_zip_any_all()
    demo_walrus()
    demo_lru_cache()
