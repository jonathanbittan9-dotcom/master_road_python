# Glossary — what's been taught, in order

This tracks every concept/syntax introduced across the learning files, in
the order it first appears. Each code file's comments assume everything
listed ABOVE its own entry is already familiar, and mark anything new
with a `# NEW:` comment at its first use.

Use this as a lookup — if a comment says "already taught," find it here
to jump back to where.

## Baseline: `testlearn.py` (your own file, before this syllabus)
- `class`, `__init__`, `self`, instance attributes
- Inheritance + `super().__init__()`
- Class variables (shared across all instances, e.g. `Book.total_books`)
- `__repr__` (controls how an object prints)
- `random.randint(a, b)`
- `try` / `except` / `log.exception()` (logs the exception with a traceback)
- Flask basics: `Flask(__name__)`, `@app.route()`, `render_template()`, `url_for()`
- `logging` module basics: `basicConfig`, `StreamHandler`, custom formatters
- f-string-adjacent `%s`/`%d` lazy logging (`log.info("x=%s", x)`)

## `core_language_mastery.py` — Section 1: Core Language Mastery
- Mutability vs. immutability; `is` (identity) vs `==` (equality); `list.copy()`
- List/dict/set comprehensions; generator expressions `(x for x in ...)`
- `yield`, generator functions, lazy evaluation, `next()`
- f-strings (`f"{value}"`)
- Decorators — writing your own; `functools.wraps`
- Context managers — class-based (`__enter__`/`__exit__`) and `@contextlib.contextmanager`
- `*args`, `**kwargs` — both defining and unpacking (`func(*list)`, `func(**dict)`)
- Closures; `nonlocal`
- Custom exceptions (subclassing `Exception`), `finally`
- Type hints: `Optional[X]`, `Union[X, Y]`, generic built-ins like `dict[str, bool]`
- `@dataclass`
- `collections.Counter`, `collections.defaultdict`, `itertools.chain`
- `time.perf_counter()` (high-resolution timer)
- `enumerate(iterable)`, `zip(iter1, iter2, ...)`
- `any(iterable)`, `all(iterable)`
- Walrus operator `:=` — assign and test in one expression
- `functools.lru_cache(maxsize=...)` — automatic memoization, `.cache_info()`

## `02_oop_design_principles.py` — Section 2: OOP & Design
- `abc.ABC`, `@abstractmethod` — abstract base classes / interfaces
- `...` (Ellipsis) as a placeholder function body
- `elif`
- generic type hints on built-ins other than dict, e.g. `list[Shape]`
- `sum(iterable)`
- `@staticmethod`
- `__new__` (controls object *creation*, before `__init__` runs) — used for Singleton; `cls` parameter
- `X | None` — union type syntax (Python 3.10+), same meaning as `Optional[X]`
- `lambda` (anonymous inline functions)
- `dataclasses.field()` with `default=` / `repr=False`
- `@property` and the matching `@x.setter`
- `isinstance(value, Type)`
- `typing.Protocol` — duck typing / structural interfaces (vs. ABC's enforced ones)
- `@classmethod` — alternate constructors, receives `cls` (contrast with `@staticmethod`)
- Mixins & multiple inheritance, `ClassName.__mro__` (Method Resolution Order)
- `__eq__` override (identity `is` vs. value `==`, and why Singleton checks must use `is`)
- Naming conventions: `PascalCase` classes vs. `snake_case` everything else
- `__init__`'s always-`None` return contract (`-> None`, never a data type)

## `03_data_structures_algorithms.py` — Section 3: Data Structures & Algorithms
- Numeric literal underscores (`200_000` == `200000`)
- `set(iterable)`, and the `{x}` single-item set literal
- `len(x)`
- `heapq` module (`heappush`, `heappop`) — a min-heap / priority queue
- `collections.deque` (fast append/pop at BOTH ends, unlike `list`)
- Default parameter values (`def f(x, y=None)`)
- `list.pop()` (no args — removes/returns the last item) and `deque.popleft()`
- The mutable-default-argument gotcha, and the `=None` + `if x is None: x = ...` fix
- Tuple-swap idiom: `a, b = b, a`
- `//` floor division
- `sorted(iterable)`
- `sorted(iterable, key=lambda x: ..., reverse=True)`
- Two-pointer technique (opposite-end indices closing inward on a sorted sequence)
- `sys.getrecursionlimit()`, `RecursionError` — Python doesn't optimize deep recursion

## `04_software_architecture.py` — Section 4: Architecture
- `dict.values()`
- `LookupError` (built-in exception; `KeyError`/`IndexError` are subclasses of it)
- `dict.setdefault(key, default)`
- `os.environ.get("NAME")` for reading environment variables
- `RuntimeError` (built-in catch-all exception)
- `@dataclass(frozen=True)` — immutable value objects
- Forward-reference type hints (a class referring to its own type in quotes, e.g. `"Money"`)
- Feature flags — shipping disabled code paths, toggled by config not deploy

## `05_databases.py` — Section 5: Databases
- `sqlite3`: `connect()`, `cursor()`, `execute()`, `fetchone()`, `fetchall()`, `.lastrowid`, `commit()`, `close()`
- Parameterized queries (`?` placeholders) vs. unsafe string formatting
- `with connection:` on a DB connection — commits on success, rolls back on exception
- Optional-dependency pattern: `try: import x / except ImportError:`
- SQLAlchemy basics: `declarative_base()`, `Column`, `ForeignKey`, `relationship()`, `sessionmaker()`, `session.add/commit/query`
- `continue` (skip to next loop iteration)
- `time.strftime(format)` — formatted timestamps
- nested generic type hints, e.g. `tuple[float, object]`
- `del` statement (remove a dict key / list item / variable)
- `CREATE INDEX name ON table(column)`, `EXPLAIN QUERY PLAN` (SCAN vs. SEARCH USING INDEX)
- `.executemany(sql, list_of_param_tuples)` — bulk inserts in one call

## `06_testing_demo.py` / `06_test_testing_demo.py` — Section 6: Testing
- `range(start, stop)` — the two-argument form of `range`
- `int(x)` — built-in type conversion
- `pytest` fixtures (`@pytest.fixture`) — reusable setup, injected by parameter name
- `assert expr`
- `@pytest.mark.parametrize` — one test definition, many input/expected pairs
- `pytest.raises(ExceptionType)` — asserting that code raises an exception
- `unittest.mock.Mock()` and `.assert_called_once_with(...)` — a fake object that records how it was called
- `importlib.import_module("name")` — importing a module by string name
- `monkeypatch` fixture (built into pytest) — `.setenv(name, value)`, `.setattr(obj, "name", value)`, auto-restored after each test
- `@pytest.fixture(scope="module")` — reused across a whole file instead of per-test
- `@pytest.fixture(autouse=True)` — runs for every test without being requested by name
- `conftest.py` convention — fixtures shared across test files automatically

## `07_version_control_notes.py` — Section 7: Git (conceptual/reference)
- No new Python syntax — this file is a runnable cheat sheet of git commands
- `.gitignore` — patterns git should never track (generated files, secrets)
- Semantic versioning (`MAJOR.MINOR.PATCH`), `git tag -a vX.Y.Z`

## `08_devops/` — Section 8: DevOps
- Dockerfile directives: `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `EXPOSE`, `USER`, `CMD`
- YAML syntax (`docker-compose.yml`, `ci.yml`): key: value, lists with `-`, nesting by indentation
- GitHub Actions concepts: `jobs`, `runs-on`, `steps`, `uses`, `with`, `${{ }}` expressions
- Subclassing a stdlib class and overriding one of its methods (`logging.Formatter.format`)
- `logging.getLogger()`, `.setLevel()`, `logging.StreamHandler()`, `.setFormatter()`
- `json.dumps(dict)` — serialize a dict to a JSON string
- Conditional expression / ternary: `X if condition else Y`
- Passing a function as an argument to be called later (`db_ping_fn`)
- `except Exception` — catching (almost) any exception broadly
- The `(_ for _ in ()).throw(Exception(...))` idiom — raising an exception inside a `lambda`
- Deployment strategies: recreate, rolling, blue-green, canary

## `09_security.py` — Section 9: Security
- `re.compile(pattern)` / `pattern.match(string)` — regular expressions, raw strings `r"..."`
- `bool(x)` conversion
- `hashlib.sha256(...).hexdigest()`, `.encode()`
- String slicing `s[:20]` (read a substring) vs. list slice-ASSIGNMENT (write)
- `!=` (not-equal operator)
- `werkzeug.security.generate_password_hash` / `check_password_hash` (salted hashing)
- `html.escape(string)`
- `time.time()` (wall-clock time) vs. `time.perf_counter()` (elapsed time)
- List slice-assignment: `some_list[:] = [...]` (replaces contents in place)
- `secrets.token_hex(n)` — cryptographically random tokens (vs. `random` module's predictable randomness)
- CSRF token pattern — proving a request came from a page the server itself rendered

## `10_performance_scalability.py` — Section 10: Performance
- `sys.stdout.reconfigure(encoding=...)` — fixing console encoding issues
- `cProfile.Profile()` + `pstats.Stats(...)` — code profiling
- `io.StringIO()` — an in-memory text stream
- `_` as a "don't care" throwaway variable name in unpacking
- `async def`, `await`, `asyncio.run()`, `asyncio.gather()` — async/await concurrency
- `concurrent.futures.ThreadPoolExecutor` / `ProcessPoolExecutor` + `.map()`
- List repetition: `[n] * 4`
- `timeit.timeit(code_string, number=N)` — comparing two snippets head-to-head (vs. cProfile's whole-program view)
- `sys.getsizeof(obj)` — an object's actual memory footprint

## `11_system_design.py` — Section 11: System Design
- `min(a, b)`
- `collections.OrderedDict` + `.move_to_end()` + `.popitem(last=False)`
- bare `raise` (re-raises the exception currently being handled)
- `random.uniform(a, b)` (float in a range, vs. `randint`'s integers)
- `try` / `except` / `else` (the `else` clause runs only if no exception occurred)
- Idempotency keys — making retries of side-effecting actions (payments) safe
- Load balancing strategies: round robin, least connections, weighted, IP hash / consistent hashing

## `12_debugging_tooling.py` — Section 12: Debugging
- `traceback.format_exc()` — get a traceback as a string
- `breakpoint()` — the built-in interactive debugger entry point (Python 3.7+)
- Post-mortem debugging: `python -m pdb -c continue script.py`, `pdb.post_mortem()` / `pdb.pm()`, IPython's `%debug`
- `warnings.warn(msg, Category, stacklevel=...)`, `warnings.catch_warnings()`, `DeprecationWarning`

## `13_professional_soft_skills.md` — Section 13: Professional / Soft Skills
- Not code — templates and habits: PR descriptions, giving/receiving code
  review feedback, estimating work, blameless incident postmortems, mentoring

## `14_web_fundamentals.py` — Section 14: Web Fundamentals
- Flask `make_response()`, the `session` object, `request.cookies`
- `response.set_cookie(..., httponly=True, samesite="Lax")`
- `response.headers[...] = ...` (dict-style header assignment)
- `app.run(..., use_reloader=False)`

## `15_flask_architecture_and_requests.py` — Section 15: Flask Architecture & Requests
- `create_app()` — the application factory pattern (vs. a module-level `app = Flask(__name__)`)
- Config classes + `app.config.from_object(SomeClass)`
- `Blueprint(name, import_name, url_prefix=...)`, `app.register_blueprint(bp)`
- `methods=["GET", "POST"]` on a route, `request.method`
- `redirect()`, the Post/Redirect/Get pattern
- `flash(msg, category)` + Jinja's `get_flashed_messages(with_categories=true)`
- `render_template_string(...)` (template text as a Python string, not a file)
- `abort(status_code)`, `@app.errorhandler(404)`, returning `(body, status)` tuples
- `@app.before_request` / `@app.after_request`, `flask.g`
- `app.test_client()`, `client.get/post(...)`, `follow_redirects=True`
- `os.environ["NAME"]` (raises `KeyError` if missing) vs. `.get("NAME")`
- HTTP methods & idempotency: GET/PUT/DELETE (idempotent) vs. POST/PATCH (not, generally)
- CORS: same-origin policy, `Access-Control-Allow-Origin`, Flask-CORS
- `flask.current_app` — a proxy for whichever app is handling the current request
- Application context vs. request context (`current_app`/`g` vs. `request`/`session`)

## `16_flask_data_auth_apis.py` — Section 16: Data, Auth & APIs
- `flask_sqlalchemy.SQLAlchemy()` created app-less, then `db.init_app(app)`
- `db.Model`, `db.Column`, `db.ForeignKey`, `db.relationship(..., backref=..., lazy=True)`
- `SQLALCHEMY_ENGINE_OPTIONS` with `StaticPool` + `check_same_thread=False` (in-memory SQLite + threading gotcha)
- `app.app_context()` (activating an app outside of a real request, e.g. at startup)
- `db.session.add/commit`, `Model.query` (legacy style) vs. `db.session.get(Model, pk)` (SQLAlchemy 2.x style)
- Hand-rolled login: `session["username"]`, `generate_password_hash`/`check_password_hash` inside real routes
- A decorator-based `login_required` built with `functools.wraps` (applied to a real view)
- Optional-dependency notes for `flask_login` and `flask_wtf` (what each replaces, not installed here)
- `request.get_json(silent=True)`, `request.args.get(name, default, type=int)` (query-param pagination)
- `client.post(url, json={...})` in `app.test_client()` — sessions/cookies persist across calls on one client
- `db.session.rollback()` — undoing uncommitted changes after a failed `.commit()`
- `methods=["PUT"]` / `["DELETE"]` routes, `return "", 204` (No Content)

## `17_observability_and_monitoring.py` — Section 17: Observability & Monitoring
- The three pillars: logs, metrics, traces — what each answers that the others can't
- Counters, gauges, histograms; `p50`/`p99` percentiles vs. a plain average
- Distributed tracing: `trace_id` (shared across a whole request) vs. `span_id` (one hop), `uuid.uuid4()`
- SLI / SLO / SLA, and error budgets as a quantified "can we ship this risky change" gate
- Symptom-based vs. cause-based alerts; alert fatigue

## `18_inheritance_deep_dive.py` — Section 18: Inheritance Deep Dive
(A focused expansion of the inheritance corner of `02_oop_design_principles.py` — nothing here contradicts that file, it just goes slower and further on this one topic.)
- Calling a parent method directly, `ParentClass.method(self, ...)` — the explicit alternative to `super()`, and why `super()` is preferred (it follows the MRO; a hardcoded class name doesn't)
- Diamond inheritance (`D(B, C)` where both `B` and `C` inherit from `A`) and *cooperative* `super()` — each class's `super()` call goes to the next class in the actual instance's MRO, not necessarily to its own direct parent
- `issubclass(ClassA, ClassB)` — compares two classes to each other (vs. `isinstance`, which compares an instance to a class)
- Stacking `@property` under `@abstractmethod` — forces subclasses to implement an abstract *property*, not just a method
- Liskov Substitution violated in practice: an override with an incompatible signature (extra required argument) breaks callers written against the base class

## `19_advanced_oop.py` — Section 19: Advanced OOP
- Descriptors: `__get__`/`__set__`/`__set_name__` — the reusable machinery `@property` is built on
- `__slots__` — restricts instance attributes, drops the per-instance `__dict__`
- `functools.total_ordering` — derives the rest of `__lt__`/`__le__`/`__gt__`/`__ge__` from `__eq__` + one comparison
- Defining `__eq__` without `__hash__` makes instances unhashable (Python sets `__hash__ = None` automatically)
- The iterator protocol by hand: `__iter__` returning `self`, `__next__` raising `StopIteration`
- `__call__` — making an instance invocable like a function
- `type(name, bases, namespace)` — the 3-argument form of `type()`, dynamically constructing a class (what `class Foo:` compiles down to)
- Custom metaclasses: `class Meta(type):` overriding `__new__`, hooking into class *creation* itself
- `__init_subclass__` — the lightweight, no-metaclass hook for reacting to subclass creation
- ABC (nominal typing, explicit inheritance required) vs. `Protocol` (structural typing, matching methods are enough — no inheritance needed, and usually shouldn't be used)
- Strategy pattern: composition (`self.channels = [...]`) instead of multiple inheritance, to combine independent behaviors without an MRO to reason about
