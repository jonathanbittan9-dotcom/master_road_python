"""
06_testing_demo.py

Section 6: Testing (part 1 — the code being tested)

This is the "application code": a tiny book-lending service. The actual
testing techniques (fixtures, parametrize, mocking) live in the companion
file 06_test_testing_demo.py, which tests THIS file.

This split — app code in one file, tests in another — is itself a habit
worth learning: tests don't live mixed into main.py, they live in their
own file/directory (conventionally a tests/ folder, prefixed test_*.py
so pytest auto-discovers them).
"""

from dataclasses import dataclass


class BookNotFoundError(Exception):
    pass


class BookUnavailableError(Exception):
    pass


@dataclass
class Book:
    id: str
    title: str
    available: bool = True


class Library:
    """The class under test."""

    def __init__(self, notifier=None):
        self._books: dict[str, Book] = {}
        # `notifier` is injected so tests can swap in a fake one instead of
        # sending a real email/Discord message during a test run.
        self._notifier = notifier

    def add_book(self, book: Book):
        self._books[book.id] = book

    def borrow(self, book_id: str) -> str:
        book = self._books.get(book_id)
        if book is None:
            raise BookNotFoundError(f"No book with id {book_id}")
        if not book.available:
            raise BookUnavailableError(f"'{book.title}' is already borrowed")
        book.available = False
        if self._notifier:
            self._notifier.send(f"'{book.title}' was borrowed")
        return f"You borrowed '{book.title}'"

    def is_prime_id(self, n: int) -> bool:
        """Small pure function — good candidate for parametrized tests."""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            # New words in this line:
            #   range(start, stop)  -> range() used with TWO arguments —
            #        counts from `start` up to (not including) `stop`,
            #        instead of the one-argument form seen earlier
            #        (range(n), which always starts at 0)
            #   int(x)               -> built-in function: converts x to an
            #        integer, truncating any decimal part (n ** 0.5 is a
            #        float, since it's a square root)
            if n % i == 0:
                return False
        return True


if __name__ == "__main__":
    # Quick manual smoke-test (NOT a substitute for real tests — see
    # 06_test_testing_demo.py and run it with: pip install pytest && pytest
    library = Library()
    library.add_book(Book(id="1", title="1984"))
    print(library.borrow("1"))
    try:
        library.borrow("1")
    except BookUnavailableError as e:
        print("Expected error:", e)
