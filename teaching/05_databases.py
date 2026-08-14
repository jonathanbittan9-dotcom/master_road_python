"""
05_databases.py

Section 5: Databases
    - Relational fundamentals: normalization, joins, transactions
    - SQL proficiency (sqlite3 — stdlib, no server needed)
    - ORMs (SQLAlchemy) vs raw driver calls
    - Migrations and schema evolution
    - Connection pooling notes
    - Caching with TTL

Run: python 05_databases.py
"""

import sqlite3
import time


# ---------------------------------------------------------------------------
# Normalization: splitting data into related tables instead of one big blob
# ---------------------------------------------------------------------------
def demo_normalization_and_joins():
    print("\n--- Normalization, Joins, Transactions (raw SQL) ---")

    conn = sqlite3.connect(":memory:")
    # New words in this line:
    #   sqlite3.connect(path)  -> opens (creating if needed) a SQLite
    #        database file and returns a Connection object
    #   ":memory:"  -> a special path meaning "don't use a real file — keep
    #        the database only in RAM," so it disappears when the script ends
    cur = conn.cursor()
    # New words in this line:
    #   .cursor()  -> the object you actually run SQL through and read
    #        results from (the pattern is always: connect() -> cursor() ->
    #        execute() -> fetch results -> commit() -> close())

    # Two normalized tables instead of repeating author info on every book row
    cur.execute("""
        CREATE TABLE authors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES authors(id)
        )
    """)

    cur.execute("INSERT INTO authors (name) VALUES (?)", ("Orwell",))
    # New words in this line:
    #   .execute(sql, params)  -> runs one SQL statement, using `params` to
    #        fill in placeholders
    #   ?  -> a placeholder inside the SQL string; sqlite3 safely substitutes
    #        the matching value from `params` (see 09_security.py for why
    #        this matters vs. string-formatting user input directly into SQL)
    author_id = cur.lastrowid
    # New words in this line:
    #   .lastrowid  -> the auto-generated id of the row just inserted
    cur.execute("INSERT INTO books (title, author_id) VALUES (?, ?)", ("1984", author_id))
    cur.execute("INSERT INTO books (title, author_id) VALUES (?, ?)", ("Animal Farm", author_id))

    # JOIN pulls related rows together at query time
    cur.execute("""
        SELECT books.title, authors.name
        FROM books
        JOIN authors ON books.author_id = authors.id
    """)
    for title, author in cur.fetchall():
        # New words in this line:
        #   .fetchall()  -> gets every matching row from the last executed
        #        query, as a list of tuples
        print(f"{title} by {author}")

    # Transaction: both inserts succeed together, or neither does
    try:
        with conn:
            # New words in this line:
            #   with conn:  -> on a sqlite3 CONNECTION specifically (different
            #        behavior from the __enter__/__exit__ context managers
            #        you wrote yourself in core_language_mastery.py) — wraps
            #        the block in a transaction: commits automatically if the
            #        block finishes cleanly, rolls back automatically if an
            #        exception escapes it. Note this does NOT close the
            #        connection (unlike some other libraries' `with`).
            cur.execute("INSERT INTO authors (name) VALUES (?)", ("Herbert",))
            author_id = cur.lastrowid
            cur.execute("INSERT INTO books (title, author_id) VALUES (?, ?)", ("Dune", author_id))
            # simulate a failure mid-transaction:
            raise RuntimeError("simulated failure before commit")
    except RuntimeError as e:
        print("Transaction rolled back:", e)

    cur.execute("SELECT COUNT(*) FROM books WHERE title = 'Dune'")
    print("Dune rows after rollback (should be 0):", cur.fetchone()[0])
    # New words in this line:
    #   .fetchone()  -> gets just the NEXT single matching row (here, one row
    #        with one column, as a 1-item tuple)
    #   [0]           -> plain indexing, pulling the count value out of that
    #        1-item row-tuple

    conn.close()

    # ALWAYS use parameterized queries (the `?` placeholders above), never:
    #   cur.execute(f"SELECT * FROM books WHERE title = '{user_input}'")
    # That string-formatting version is a SQL injection vulnerability.


# ---------------------------------------------------------------------------
# Indexes & EXPLAIN QUERY PLAN — why the SAME query can be fast or slow
# ---------------------------------------------------------------------------
def demo_indexes():
    print("\n--- Indexes & EXPLAIN QUERY PLAN ---")

    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER)")
    conn.executemany(
        "INSERT INTO books (title, author_id) VALUES (?, ?)",
        [(f"Book {i}", i % 50) for i in range(5000)],
        # New words in this line:
        #   .executemany(sql, list_of_param_tuples)  -> runs the SAME
        #        parameterized statement once per tuple in the list — much
        #        faster than calling .execute() 5000 times in a loop, because
        #        the SQL only has to be parsed/planned ONCE
    )
    conn.commit()

    plan_before = conn.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM books WHERE author_id = 7"
    ).fetchall()
    # New words in this line:
    #   EXPLAIN QUERY PLAN  -> a SQL prefix (SQLite-specific spelling; other
    #        databases use EXPLAIN or EXPLAIN ANALYZE) that doesn't actually
    #        RUN the query — it returns a description of HOW the database
    #        intends to execute it, e.g. "scan every row" vs. "use an index"
    print("plan WITHOUT an index:", plan_before)
    # A "SCAN books" plan means: check author_id against all 5000 rows, one
    # by one, to find matches — O(n) no matter how big the table gets.

    conn.execute("CREATE INDEX idx_books_author_id ON books(author_id)")
    # New words in this line:
    #   CREATE INDEX name ON table(column)  -> builds a separate, sorted
    #        lookup structure for that column (conceptually similar to the
    #        binary search tree in 03_data_structures_algorithms.py) — a
    #        one-time cost to build and maintain, in exchange for much faster
    #        lookups on that column afterward

    plan_after = conn.execute(
        "EXPLAIN QUERY PLAN SELECT * FROM books WHERE author_id = 7"
    ).fetchall()
    print("plan WITH an index:", plan_after)
    # Now the plan should mention "USING INDEX idx_books_author_id" — SQLite
    # jumps straight to matching rows instead of scanning all 5000.

    conn.close()
    # Real-world tradeoff: indexes speed up READS but slow down WRITES
    # (every INSERT/UPDATE now has to update the index too) and use extra
    # disk space — index the columns you actually filter/JOIN/ORDER BY on
    # often, not every column defensively.


# ---------------------------------------------------------------------------
# ORM (SQLAlchemy) vs raw driver calls
# ---------------------------------------------------------------------------
def demo_orm():
    print("\n--- ORM (SQLAlchemy) vs raw SQL ---")
    try:
        from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
        from sqlalchemy.orm import declarative_base, relationship, sessionmaker
    except ImportError:
        # New words in this block:
        #   try / except ImportError  -> the same try/except syntax you
        #        already know, applied to a specific built-in exception:
        #        Python raises ImportError when an `import` fails because
        #        the library isn't installed. Catching it here makes
        #        SQLAlchemy an OPTIONAL dependency instead of crashing the
        #        whole script if it's missing.
        print("SQLAlchemy not installed — pip install SQLAlchemy to run this part")
        return

    # New words below (all from the sqlalchemy library, not Python itself):
    #   declarative_base()         -> returns a base class; any class that
    #        inherits from it becomes mapped to a database table
    #   Column(Type, **options)     -> declares one table column and its type
    #   Integer, String             -> SQLAlchemy's column type objects
    #   primary_key=True            -> marks a column as the table's primary key
    #   ForeignKey("table.column")  -> declares this column as a reference to
    #        another table's column
    #   relationship(...)           -> declares a Python-level link between
    #        two mapped classes (so book.author works), separate from the
    #        raw foreign-key COLUMN itself
    Base = declarative_base()

    class Author(Base):
        __tablename__ = "authors"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        books = relationship("Book", back_populates="author")

    class Book(Base):
        __tablename__ = "books"
        id = Column(Integer, primary_key=True)
        title = Column(String)
        author_id = Column(Integer, ForeignKey("authors.id"))
        author = relationship("Author", back_populates="books")

    engine = create_engine("sqlite:///:memory:")
    # New words in this line:
    #   create_engine(url)  -> SQLAlchemy's connection-manager object; the
    #        URL describes which database driver and file/server to use
    Base.metadata.create_all(engine)
    # New words in this line:
    #   Base.metadata.create_all(engine)  -> actually creates the tables
    #        (CREATE TABLE statements) for every class that inherited from Base
    Session = sessionmaker(bind=engine)
    session = Session()
    # New words in this line:
    #   sessionmaker(bind=engine)  -> a factory that produces Session objects
    #        tied to this engine
    #   Session()                   -> a session is your "conversation" with
    #        the database — queries and changes go through it

    orwell = Author(name="Orwell")
    session.add(orwell)
    # New words in this line:
    #   session.add(obj)  -> stages a new object to be inserted (nothing
    #        touches the database yet — that happens on .commit())
    session.add(Book(title="1984", author=orwell))
    session.commit()
    # New words in this line:
    #   session.commit()  -> writes all staged changes to the database in
    #        one transaction

    # No SQL strings anywhere — the ORM generates the JOIN for you
    for book in session.query(Book).all():
        # New words in this line:
        #   session.query(Book).all()  -> fetches every Book row, returning
        #        actual Book OBJECTS (with .title, .author, etc.) instead of
        #        raw tuples like the sqlite3 API returned above
        print(f"{book.title} by {book.author.name}")

    # Tradeoff: ORMs are convenient but can hide expensive queries
    # (see the N+1 query problem in 10_performance_scalability.py)


# ---------------------------------------------------------------------------
# Migrations: versioned, repeatable schema changes instead of manual edits
# ---------------------------------------------------------------------------
MIGRATIONS = [
    ("001_create_books", "CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT)"),
    ("002_add_available_column", "ALTER TABLE books ADD COLUMN available INTEGER DEFAULT 1"),
]


def run_migrations(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            name TEXT PRIMARY KEY,
            applied_at TEXT
        )
    """)
    for name, sql in MIGRATIONS:
        cur.execute("SELECT 1 FROM schema_migrations WHERE name = ?", (name,))
        if cur.fetchone():
            continue
            # New words in this line:
            #   continue  -> immediately skips to the NEXT iteration of the
            #        loop, without running any code below it for this
            #        iteration — used here so an already-applied migration
            #        is simply skipped, making migrations SAFE to re-run
        cur.execute(sql)
        cur.execute(
            "INSERT INTO schema_migrations (name, applied_at) VALUES (?, ?)",
            (name, time.strftime("%Y-%m-%d %H:%M:%S")),
            # New words in this line:
            #   time.strftime(format)  -> turns the CURRENT time into a
            #        formatted string. %Y/%m/%d/%H/%M/%S are format codes for
            #        year/month/day/hour/minute/second. Different from
            #        time.perf_counter() (Section 1), which measures ELAPSED
            #        time, not a human-readable timestamp.
        )
        print(f"Applied migration: {name}")
    conn.commit()


def demo_migrations():
    print("\n--- Migrations ---")
    conn = sqlite3.connect(":memory:")
    run_migrations(conn)
    run_migrations(conn)   # second run: nothing new applied, proving idempotency
    conn.close()
    # In a real project: Alembic (for SQLAlchemy) or Flask-Migrate does this for you.
    # This hand-rolled version exists just to show the underlying idea.


# ---------------------------------------------------------------------------
# Connection pooling (concept note — sqlite3 doesn't need it, but Mongo/Postgres do)
# ---------------------------------------------------------------------------
def demo_connection_pooling_notes():
    print("\n--- Connection Pooling (concept) ---")
    print("""
Opening a new DB connection per request is expensive (TCP handshake, auth).
A connection pool keeps a set of open connections ready to reuse:

    - Flask-SQLAlchemy: pool_size / max_overflow settings on create_engine()
    - PyMongo: MongoClient() already pools connections internally — reuse
      ONE client for the whole app instead of creating a new MongoClient()
      per request (a common beginner mistake in Flask + Mongo apps).
""")


# ---------------------------------------------------------------------------
# Caching with TTL (avoid hitting the DB for data that rarely changes)
# ---------------------------------------------------------------------------
class TTLCache:
    def __init__(self, ttl_seconds: float):
        self.ttl = ttl_seconds
        self._store: dict[str, tuple[float, object]] = {}
        # New words in this line:
        #   tuple[float, object]  -> a generic type hint (same [..] style as
        #        dict[str, bool]) meaning "a tuple of exactly a float and an
        #        object" — `object` here means "could be any type," since
        #        the cache stores all kinds of values

    def get(self, key):
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        # New words in this line:
        #   (tuple unpacking, same idea as core_language_mastery.py's `a, b = b, a`)
        #   entry is a 2-item tuple (expires_at, value); this pulls both
        #   parts out in one line instead of entry[0] / entry[1]
        if time.time() > expires_at:
            del self._store[key]
            # New words in this line:
            #   del  -> a statement that removes a key from a dict (or an
            #        item from a list, or deletes a variable entirely) —
            #        used here to actually evict the expired entry
            return None
        return value

    def set(self, key, value):
        self._store[key] = (time.time() + self.ttl, value)


def demo_caching():
    print("\n--- Caching with TTL ---")

    cache = TTLCache(ttl_seconds=0.2)

    def get_leaderboard():
        # pretend this is an expensive DB aggregation
        print("  (hit the database)")
        return ["Alice", "Bob", "Carol"]

    def get_leaderboard_cached():
        cached = cache.get("leaderboard")
        if cached is not None:
            print("  (served from cache)")
            return cached
        result = get_leaderboard()
        cache.set("leaderboard", result)
        return result

    get_leaderboard_cached()   # hits the DB
    get_leaderboard_cached()   # served from cache
    time.sleep(0.25)
    get_leaderboard_cached()   # expired — hits the DB again
    # In real apps: Redis, or Flask-Caching, do this for you with more features.


if __name__ == "__main__":
    demo_normalization_and_joins()
    demo_indexes()
    demo_orm()
    demo_migrations()
    demo_connection_pooling_notes()
    demo_caching()
 