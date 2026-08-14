"""
12_debugging_tooling.py

Section 12: Debugging & Tooling
    - Using a real debugger (pdb / breakpoint()) instead of print-driven debugging
    - Reading stack traces fluently
    - Log-based debugging (for when you can't attach a debugger — e.g. prod)
    - Linting/formatting tools as habit

Run: python 12_debugging_tooling.py
"""

import sys
# (sys.stdout.reconfigure already introduced in 10_performance_scalability.py
# — needed again here because the traceback printed below also includes
# this file's own path)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import logging
import traceback
import warnings
# New words in this line:
#   warnings (module)  -> see demo_warnings() near the end of this file for
#        what it's for — imported up here with the rest, unlike some
#        earlier files' habit of importing something right where it's
#        first used (e.g. 09_security.py's `import html` inside a function)


# ---------------------------------------------------------------------------
# Using a real debugger instead of print()
# ---------------------------------------------------------------------------
def calculate_total(items):
    total = 0
    for item in items:
        # Uncomment the next line and re-run this file to drop into an
        # interactive debugger AT THIS EXACT POINT — inspect `item`,
        # `total`, step line-by-line, all without adding a single print():
        #
        #     breakpoint()
        #
        total += item["price"] * item["quantity"]
    return total


def demo_debugger():
    print("\n--- Debugger (pdb / breakpoint()) ---")
    print("""
print-driven debugging:
    print("item:", item)          # add this
    print("total so far:", total) # and this
    # ...run, read output, remove the prints, repeat when you need more info

Real debugger — one line, then INTERACTIVE:
    breakpoint()   # built into Python 3.7+, no import needed
    # Program pauses here. At the (Pdb) prompt:
    #   p item          -> print a variable
    #   n                -> next line
    #   s                -> step into a function call
    #   c                -> continue running
    #   l                -> list surrounding code
    #   item["price"] = 5   -> you can even MODIFY state live and continue

Why this matters: print-debugging only shows what you thought to log
in advance. A debugger lets you ask NEW questions after seeing what's
actually happening — which is most of real debugging.
""")
    items = [{"price": 10, "quantity": 2}, {"price": 5, "quantity": 3}]
    print("calculate_total result:", calculate_total(items))


# ---------------------------------------------------------------------------
# Post-mortem debugging — inspecting a crash AFTER the fact
# ---------------------------------------------------------------------------
def demo_post_mortem_debugging():
    print("\n--- Post-Mortem Debugging ---")
    print("""
breakpoint() above requires knowing IN ADVANCE where to pause. Sometimes a
crash happens somewhere you didn't think to add one. Post-mortem debugging
drops you into the debugger AT THE POINT OF THE CRASH, after it's already
happened:

Option 1 — run the whole script under pdb, drop in automatically on any
uncaught exception:
    python -m pdb -c continue my_script.py

Option 2 — from inside an except block, or right after a crash in the
same interactive session:
    import pdb
    pdb.post_mortem()   # or the shorter pdb.pm() right after a traceback

Option 3 — inside a Jupyter/IPython session specifically:
    %debug              # drops into the debugger at the last unhandled exception

Once inside, it's the SAME (Pdb) prompt as breakpoint() above (p, n, s, c,
l) — except now you're standing exactly where the exception was raised,
with every local variable at that moment still inspectable, instead of
having to guess where to place a breakpoint() ahead of time.
""")


# ---------------------------------------------------------------------------
# Reading stack traces fluently
# ---------------------------------------------------------------------------
def layer_three():
    data = {"title": "1984"}
    return data["author"]   # KeyError — 'author' doesn't exist


def layer_two():
    return layer_three()


def layer_one():
    return layer_two()


def demo_reading_stack_traces():
    print("\n--- Reading Stack Traces ---")
    try:
        layer_one()
    except KeyError:
        tb = traceback.format_exc()
        # New words in this line:
        #   traceback.format_exc()  -> grabs the traceback of the exception
        #        CURRENTLY being handled (must be called inside an except
        #        block) and returns it as a plain string, so you can print
        #        it, log it, or send it somewhere, instead of letting Python
        #        print it automatically and crash the program
        print(tb)
        print("""
How to read this, top to bottom:
  1. The LAST line ("KeyError: 'author'") is the actual error.
  2. The traceback ABOVE it shows the call chain that led there, in
     order: layer_one() called layer_two() called layer_three().
  3. The bottom-most frame (layer_three, "data["author"]") is almost
     always where to start looking — that's where the error was RAISED,
     even though layer_one() is where you called into the broken chain.
  4. Beginners often stare at the top of the trace; the useful line is
     usually near the bottom, closest to the actual error message.
""")


# ---------------------------------------------------------------------------
# Log-based debugging — for production, where you can't attach a debugger
# ---------------------------------------------------------------------------
def demo_log_based_debugging():
    print("\n--- Log-Based Debugging (production) ---")

    logger = logging.getLogger("prod_demo")
    logger.setLevel(logging.DEBUG)
    logger.handlers = [logging.StreamHandler()]

    def process_order(order_id, items):
        logger.debug("processing order %s with %d items", order_id, len(items))
        try:
            total = calculate_total(items)
            logger.info("order %s total: %s", order_id, total)
            return total
        except Exception:
            # log.exception() includes the full traceback in the log output —
            # critical for debugging something you can't reproduce locally
            logger.exception("order %s failed to process", order_id)
            raise

    try:
        process_order("A1", [{"price": 10, "quantity": "oops"}])   # will raise TypeError
    except TypeError:
        pass   # already logged above; this demo just shows the logging happened

    print("""
In production you generally can't attach breakpoint() to a live server.
Good logging is how you reconstruct what happened AFTER the fact:
  - log.debug()    -> verbose, dev-only detail
  - log.info()     -> normal operation milestones
  - log.warning()  -> something recoverable but worth knowing about
  - log.exception()-> inside an except block, logs the FULL traceback
This is why 09_devops's structured JSON logging matters — searchable
context beats a wall of print() output when you're debugging at 2am.
""")


# ---------------------------------------------------------------------------
# Linting/formatting as habit
# ---------------------------------------------------------------------------
def demo_linting_notes():
    print("\n--- Linting & Formatting ---")
    print("""
    pip install ruff black mypy

    ruff check .        # catches unused imports, undefined names, bugs
    black .              # auto-formats code to one consistent style
    mypy .               # catches type errors before runtime

Run these in CI (see 08_devops/ci.yml) so style/bug arguments in code
review disappear — the tool decides, not opinions. Also catches real
bugs early: ruff would have flagged the unused `format` variable that
shadows the builtin in testlearn.py before it ever ran.
""")


# ---------------------------------------------------------------------------
# The warnings module — softer than raising, louder than a comment
# ---------------------------------------------------------------------------
def old_calculate_total(items):
    """Still works, but callers should migrate to calculate_total() instead."""
    warnings.warn(
        "old_calculate_total() is deprecated, use calculate_total() instead",
        DeprecationWarning,
        stacklevel=2,
        # New words in this line:
        #   DeprecationWarning  -> a built-in warning CATEGORY (there are
        #        others: UserWarning, RuntimeWarning) — lets code that reads
        #        warnings filter/handle different kinds differently
        #   stacklevel=2  -> points the warning at whoever CALLED this
        #        function, instead of at this line inside it — so the
        #        reported location is the code that needs to change, not
        #        this deprecated function's own internals
    )
    return calculate_total(items)


def demo_warnings():
    print("\n--- warnings module ---")

    items = [{"price": 10, "quantity": 2}]

    with warnings.catch_warnings(record=True) as caught:
        # New words in this line:
        #   warnings.catch_warnings(record=True)  -> a context manager
        #        (same `with` syntax from core_language_mastery.py) that
        #        captures warnings into a list instead of just printing them
        #        — used here so this demo can show you what got caught,
        #        rather than relying on you noticing console output
        warnings.simplefilter("always")
        # New words in this line:
        #   .simplefilter("always")  -> without this, Python's default
        #        filter shows each DISTINCT warning only ONCE per location,
        #        to avoid flooding output — "always" overrides that for
        #        this demo so it's guaranteed to show up
        old_calculate_total(items)

    for w in caught:
        print(f"Caught: {w.category.__name__}: {w.message}")
    # Real-world use: mark an old function/API deprecated with a warning
    # instead of deleting it outright, giving other code time to migrate
    # before a future release removes it for real. ruff/mypy (see linting
    # notes above) can also be configured to flag DeprecationWarning usages
    # across a codebase automatically.


if __name__ == "__main__":
    demo_debugger()
    demo_post_mortem_debugging()
    demo_reading_stack_traces()
    demo_log_based_debugging()
    demo_linting_notes()
    demo_warnings()
