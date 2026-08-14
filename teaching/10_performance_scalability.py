"""
10_performance_scalability.py

Section 10: Performance & Scalability
    - Profiling (cProfile)
    - The N+1 query problem
    - asyncio (async/await)
    - Concurrency vs. parallelism (threading vs multiprocessing, the GIL)

Run: python 10_performance_scalability.py
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# New words in this line:
#   sys.stdout               -> the standard-output stream every print()
#        call writes to
#   .reconfigure(encoding=..., errors=...)  -> changes how that stream
#        encodes text going forward. Needed here because cProfile's stats
#        output below includes this file's own path, and Windows consoles
#        often default to a codepage (cp1252) that can't encode non-ASCII
#        characters that might appear in a file path — without this,
#        printing the profiler output could crash with a UnicodeEncodeError
#        unrelated to the actual lesson
#   errors="replace"          -> if a character still can't be encoded,
#        substitute a placeholder instead of crashing

import asyncio
import cProfile
import pstats
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from io import StringIO


# ---------------------------------------------------------------------------
# Profiling — measure before you optimize, don't guess
# ---------------------------------------------------------------------------
def slow_function():
    total = 0
    for i in range(500_000):
        total += i ** 2
    return total


def demo_profiling():
    print("\n--- Profiling (cProfile) ---")

    profiler = cProfile.Profile()
    # New words in this line:
    #   cProfile.Profile()  -> a profiler object: records exactly how much
    #        time is spent in every function call between .enable() and
    #        .disable(), instead of you guessing where the slow part is
    profiler.enable()
    slow_function()
    profiler.disable()

    stream = StringIO()
    # New words in this line:
    #   io.StringIO()  -> an in-memory, file-like object you can .write() to
    #        and read back, without ever touching the real filesystem — used
    #        here just to capture pstats' output as a string instead of
    #        letting it print straight to the console
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    # New words in this line:
    #   pstats.Stats(profiler, stream=stream)  -> turns the raw profiler data
    #        into a readable report, writing it to `stream` instead of stdout
    #   .sort_stats("cumulative")  -> sorts functions by total time,
    #        including everything they called
    stats.print_stats(3)
    # New words in this line:
    #   .print_stats(3)  -> writes only the top 3 rows of the report
    print(stream.getvalue())
    # New words in this line:
    #   .getvalue()  -> reads everything written to the StringIO so far, as
    #        a normal string
    # In a real app: profile the actual slow route, don't optimize by
    # instinct — the bottleneck is often somewhere surprising (e.g. a
    # template render, not the query you assumed was slow).


# ---------------------------------------------------------------------------
# timeit — micro-benchmarking two specific implementations against each other
# ---------------------------------------------------------------------------
def demo_timeit():
    print("\n--- timeit: comparing two implementations ---")
    import timeit
    # New words in this line:
    #   timeit (module)  -> different JOB than cProfile above: cProfile
    #        answers "where in this whole PROGRAM is time going?" — timeit
    #        answers "which of these two specific SNIPPETS is faster, and by
    #        how much?" It also runs the snippet many times and reports the
    #        best result, smoothing out noise a single time.perf_counter()
    #        measurement (used elsewhere in this course) can't average away.

    concat_with_plus = timeit.timeit(
        'result = ""\nfor i in range(1000):\n    result += str(i)',
        number=1000,
    )
    # New words in this line:
    #   timeit.timeit(code_string, number=N)  -> runs `code_string` N times
    #        back-to-back and returns the TOTAL elapsed seconds for all N
    #        runs combined (not per-run) — the code is passed as a STRING,
    #        deliberately isolated from this file's own variables/imports,
    #        so the measurement isn't polluted by anything else going on

    concat_with_join = timeit.timeit(
        'result = "".join(str(i) for i in range(1000))',
        number=1000,
    )

    print(f"string += in a loop:     {concat_with_plus:.4f}s for 1000 runs")
    print(f"''.join(generator):      {concat_with_join:.4f}s for 1000 runs")
    print("(join is faster: += rebuilds a new string object on every iteration;")
    print(" join builds the result once, from all the pieces at the same time)")


# ---------------------------------------------------------------------------
# Memory footprint — sys.getsizeof()
# ---------------------------------------------------------------------------
def demo_memory_footprint():
    print("\n--- Memory footprint: sys.getsizeof() ---")

    small_list = [1, 2, 3]
    big_list = list(range(100_000))
    a_generator = (i for i in range(100_000))

    print("sys.getsizeof(small_list):", sys.getsizeof(small_list), "bytes")
    # New words in this line:
    #   sys.getsizeof(obj)  -> the number of bytes obj itself occupies in
    #        memory right now — useful for confirming a suspicion ("is this
    #        object actually as big as I think?") rather than guessing
    print("sys.getsizeof(big_list):  ", sys.getsizeof(big_list), "bytes")
    print("sys.getsizeof(a_generator):", sys.getsizeof(a_generator), "bytes")
    print("""
The generator stays tiny no matter how many items it WILL eventually
produce, because it doesn't hold them all at once — this is the same
laziness from core_language_mastery.py's generator section, now shown as
an actual memory-size difference instead of just a timing one. Prefer a
generator over a list whenever you're going to consume something once,
in order, and don't need random access (list[500]) or len() on it.
""")


# ---------------------------------------------------------------------------
# The N+1 query problem
# ---------------------------------------------------------------------------
def setup_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER)")
    for i in range(20):
        conn.execute("INSERT INTO authors (name) VALUES (?)", (f"Author {i}",))
        conn.execute("INSERT INTO books (title, author_id) VALUES (?, ?)", (f"Book {i}", i + 1))
    conn.commit()
    return conn


def n_plus_1_version(conn):
    """BAD: 1 query for books, then N more queries — one per book — for authors."""
    query_count = 0
    books = conn.execute("SELECT title, author_id FROM books").fetchall()
    query_count += 1
    results = []
    for title, author_id in books:
        author = conn.execute("SELECT name FROM authors WHERE id = ?", (author_id,)).fetchone()
        query_count += 1
        results.append((title, author[0]))
    return results, query_count


def single_join_version(conn):
    """GOOD: 1 query total, using a JOIN."""
    query_count = 1
    rows = conn.execute("""
        SELECT books.title, authors.name
        FROM books JOIN authors ON books.author_id = authors.id
    """).fetchall()
    return rows, query_count


def demo_n_plus_1():
    print("\n--- The N+1 Query Problem ---")

    conn = setup_db()
    _, bad_count = n_plus_1_version(conn)
    # New words in this line:
    #   _ (underscore as a variable name)  -> a widely-used CONVENTION
    #        (not special syntax) meaning "I'm required to unpack this
    #        value, but I don't actually need it" — here, the function
    #        returns (results, query_count) and only query_count is wanted
    _, good_count = single_join_version(conn)
    print(f"N+1 version:  {bad_count} queries for 20 books")
    print(f"JOIN version: {good_count} query for the same 20 books")
    conn.close()
    # This is exactly the kind of thing an ORM can hide from you if you
    # loop over a relationship without eager-loading it (e.g. accessing
    # book.author inside a for-loop without .join() or selectinload()).


# ---------------------------------------------------------------------------
# asyncio — concurrency for I/O-bound work
# ---------------------------------------------------------------------------
async def fetch_simulated(name: str, delay: float):
    # New words in this line:
    #   async def  -> marks this function as a "coroutine" — calling it
    #        doesn't run it immediately, it creates an awaitable object
    #        (similar in spirit to how calling a generator function doesn't
    #        run its body until iterated — Section 1). It only actually
    #        runs when you `await` it or hand it to something like
    #        asyncio.run()/asyncio.gather().
    await asyncio.sleep(delay)
    # New words in this line:
    #   await  -> pauses THIS coroutine (without blocking the whole program)
    #        until asyncio.sleep(delay) finishes — other coroutines can run
    #        during that wait
    #   asyncio.sleep(delay)  -> an async version of time.sleep(); stands in
    #        for a real network call here
    return f"{name} done"


async def run_sequentially():
    results = []
    for name, delay in [("A", 0.2), ("B", 0.2), ("C", 0.2)]:
        results.append(await fetch_simulated(name, delay))   # waits for EACH
        # one to fully finish before starting the next — no overlap
    return results


async def run_concurrently():
    return await asyncio.gather(
        # New words in this line:
        #   asyncio.gather(coro1, coro2, coro3)  -> starts all of them and
        #        lets them run CONCURRENTLY — while one is paused inside
        #        `await asyncio.sleep`, the others get a chance to make
        #        progress, instead of waiting in a strict queue
        fetch_simulated("A", 0.2),
        fetch_simulated("B", 0.2),
        fetch_simulated("C", 0.2),
    )


def demo_asyncio():
    print("\n--- asyncio: sequential vs concurrent ---")

    start = time.perf_counter()
    asyncio.run(run_sequentially())
    # New words in this line:
    #   asyncio.run(coroutine)  -> the entry point: creates an event loop,
    #        runs the given coroutine to completion, then shuts the loop
    #        down. Call this ONCE, at the top level of a script.
    print(f"sequential: {time.perf_counter() - start:.2f}s (~0.6s: 0.2+0.2+0.2)")

    start = time.perf_counter()
    asyncio.run(run_concurrently())
    print(f"concurrent: {time.perf_counter() - start:.2f}s (~0.2s: all three overlap)")
    # asyncio helps when work is I/O-bound (waiting on network/disk), NOT
    # CPU-bound — see the GIL note below for why.


# ---------------------------------------------------------------------------
# Concurrency vs. parallelism: threading vs multiprocessing, and the GIL
# ---------------------------------------------------------------------------
def cpu_bound_work(n):
    total = 0
    for i in range(n):
        total += i ** 2
    return total


def demo_threading_vs_multiprocessing():
    print("\n--- Threading vs. Multiprocessing (the GIL) ---")

    n = 2_000_000

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as executor:
        # New words in this line:
        #   ThreadPoolExecutor(max_workers=4)  -> runs work across multiple
        #        THREADS (same process, shared memory); `with ... as
        #        executor:` is a context manager (Section 1) that shuts the
        #        pool down automatically afterward
        list(executor.map(cpu_bound_work, [n] * 4))
        # New words in this line:
        #   .map(fn, list)  -> runs `fn` once per item in the list,
        #        distributed across the worker threads
        #   [n] * 4          -> list repetition via `*`: builds [n, n, n, n]
    threading_time = time.perf_counter() - start

    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        # New words in this line:
        #   ProcessPoolExecutor  -> has the IDENTICAL interface to
        #        ThreadPoolExecutor above, but runs work across separate OS
        #        PROCESSES (each with its own memory and its own GIL)
        #        instead of threads
        list(executor.map(cpu_bound_work, [n] * 4))
    multiprocessing_time = time.perf_counter() - start

    print(f"threading (CPU-bound):      {threading_time:.2f}s")
    print(f"multiprocessing (CPU-bound): {multiprocessing_time:.2f}s")
    print("""
Python's GIL (Global Interpreter Lock) means only ONE thread runs Python
bytecode at a time, even with multiple threads. For CPU-bound work,
threading often gives little/no speedup — multiprocessing (separate
processes, separate GILs) actually uses multiple cores.

Threading DOES help for I/O-bound work (waiting on network/disk), because
threads release the GIL while waiting. Rule of thumb:
  - I/O-bound  -> asyncio or threading
  - CPU-bound  -> multiprocessing (or a different language for the hot path)
""")


if __name__ == "__main__":
    demo_profiling()
    demo_timeit()
    demo_memory_footprint()
    demo_n_plus_1()
    demo_asyncio()
    demo_threading_vs_multiprocessing()
