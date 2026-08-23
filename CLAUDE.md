# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal, self-directed Python curriculum ("senior path") plus small scratch
Flask projects used to apply what's being learned. There is no README, no
CI, no linter/formatter config, and no `requirements.txt` — dependencies are
installed ad hoc into `venv/`. Treat this as a learning sandbox, not a
production codebase: code here is often intentionally exploratory,
in-progress, or left with rough edges while a concept is being practiced.

## Environment / commands

The venv is POSIX-layout (`venv/bin/...`), built with Python 3.14 — run
Python commands from a bash/WSL shell.

```bash
source venv/bin/activate
```

Installed so far (no lockfile — check `venv/lib/python3.14/site-packages`
before assuming a package is available): `flask`, `jinja2`, `werkzeug`,
`colorlog`, `pytest`. `05_databases.py` uses SQLAlchemy behind an
optional-import guard (`try: import ... except ImportError:`) since it
isn't installed.

**Run a teaching file** (each is standalone and runnable on its own to
demonstrate that lesson's concepts):
```bash
python teaching/19_advanced_oop.py
```

**Run the root scratch Flask app** (`practice.py`, port 5000):
```bash
python practice.py
```
Routes: `/pay`, `/messages`, `/animals`, `/chores`.

**Run the `cafe` mini-project** — must be launched with cwd set to the
`cafe/` directory (its `__main__.py` inserts that directory onto
`sys.path` so the sibling `scripts/` package resolves):
```bash
cd cafe
python -m cafe
```
Runs on port 3000. Routes: `/menu`, `/order/<size>`.

**Tests**: `pytest` is installed and `teaching/06_test_testing_demo.py` /
`06_testing_demo.py` demonstrate fixtures, `parametrize`, `monkeypatch`,
etc., but there are no `test_*.py` files or `conftest.py` anywhere yet. Once
tests exist, the standard invocations apply: `pytest` for the whole suite,
`pytest path/to/test_file.py::test_name` for a single test.

## Architecture

The repo has two parallel tracks that don't import from each other:

### 1. `teaching/` — the syllabus

Numbered files (`core_language_mastery.py`, `02_oop_design_principles.py`
… `19_advanced_oop.py`) form a strict learning sequence. Each file:
- Opens with a docstring naming what it covers and which earlier files
  (concepts) it assumes are already known.
- Marks brand-new syntax/concepts inline with a `# NEW:` comment at first
  use.
- Is meant to be run directly to see its concepts demonstrated/printed.

`teaching/GLOSSARY.MD` is the authoritative, ordered index of every
concept/syntax introduced across these files — it's how a file's "assumes
X is already known" claims get resolved. **When adding or editing a
teaching file, update `GLOSSARY.MD` to match** (new concepts appended in
the section for that file, in first-appearance order).

### 2. Scratch projects — applying the syllabus

- **Root app** (`practice.py`, `config.py`, `logs_setup.py`,
  `challenges.py`, `templates/`): one un-modularized Flask app used to
  bolt on new concepts as they're learned — a Singleton (`app_config` in
  `config.py`), a `Protocol`-based `Messages_Interface`, a diamond MRO demo
  (`A/B/C/D`), a `@dataclass` (`Laundry`), etc., alongside Flask routes
  that render `templates/practice.html` / `templates/errorpage.html`. This
  file is expected to accumulate unrelated experiments rather than stay
  cohesive.
- **`cafe/`** is the "graduated" version — the same kind of practice, but
  pulled into a layered package once a concept is ready to be structured
  properly:
  - `cafe/cafe/__main__.py` is the entrypoint (`python -m cafe`). It does a
    `sys.path` insert of the outer `cafe/` directory so that `scripts/`
    (a sibling of `cafe/cafe/`, not nested inside it) can be imported as a
    top-level package.
  - `cafe/scripts/domain/` is the domain layer. Note the naming is
    swapped from what the filenames suggest: `menu.py` defines the
    `Order` class, while `order.py` defines the `service` ABC and its
    `small`/`medium`/`large` subclasses plus the `SIZES` registry used to
    look up a size class by name.
  - `cafe/scripts/web/routes.py` is the Flask layer (`/menu`,
    `/order/<size>`), rendering templates from
    `cafe/scripts/web/templates/`.
  - The colorlog setup in `cafe/scripts/domain/logs_setup.py` is a
    separate copy of the same setup in the root `logs_setup.py`, not a
    shared import.
- **`practice/advanced_oop.py`** is a newer, currently near-empty scratch
  file — treat it as the staging area for the next round of practice
  rather than a finished module.
