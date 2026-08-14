"""
02_oop_design_principles.py

Section 2: Object-Oriented & Design Principles
    - Inheritance vs. composition
    - Abstract base classes / interfaces
    - Duck typing & typing.Protocol
    - SOLID principles
    - Design patterns: Factory, Singleton, Strategy, Observer, Repository, Adapter
    - @classmethod — alternate constructors
    - Mixins & multiple inheritance (MRO)
    - Dataclasses, @property
    - Idioms: naming conventions, `is` vs `==`, __init__'s return contract

Run: python 02_oop_design_principles.py
"""

from abc import ABC, abstractmethod
# New words in this line:
#   abc              -> standard library module: "Abstract Base Classes"
#   ABC               -> a base class you inherit from to make YOUR class
#                        abstract (can't be instantiated directly)
#   abstractmethod    -> a decorator marking one method as "subclasses MUST
#                        override this"
from dataclasses import dataclass, field
# New words in this line:
#   field  -> a function (different from the @dataclass decorator itself)
#             used to configure a single dataclass attribute in detail —
#             see its use further down in this file
from typing import Protocol
# New words in this line:
#   Protocol  -> a base class for defining a "structural" interface — see
#                the Duck Typing section below for how this differs from ABC


# ---------------------------------------------------------------------------
# Inheritance vs. Composition
# ---------------------------------------------------------------------------
# Inheritance: "IS-A" relationship. Use sparingly — deep hierarchies get rigid.
class Animal:
    def speak(self):
        raise NotImplementedError


class Dog(Animal):
    def speak(self):
        return "Woof"


# Composition: "HAS-A" relationship. Usually more flexible than inheritance,
# because you can swap the parts out at runtime.
class Engine:
    def start(self):
        return "Engine started"


class Car:
    def __init__(self):
        self.engine = Engine()   # Car HAS-A engine, not IS-A engine

    def start(self):
        return self.engine.start()


def demo_inheritance_vs_composition():
    print("\n--- Inheritance vs Composition ---")
    print(Dog().speak())
    print(Car().start())
    # Rule of thumb: "favor composition over inheritance" — swapping self.engine
    # for an ElectricEngine at runtime is easy; swapping a base class is not.


# ---------------------------------------------------------------------------
# Abstract Base Classes / Interfaces
# ---------------------------------------------------------------------------
class PaymentProcessor(ABC):
    # New words in this line:
    #   (ABC) as a base class  -> combined with @abstractmethod below, this
    #        defines an "interface": a class that CANNOT be instantiated
    #        directly, and forces every subclass to implement the marked
    #        method(s) or Python refuses to build an instance of THEM either
    """An interface: any subclass MUST implement process()."""

    @abstractmethod
    # New words in this line:
    #   @abstractmethod  -> marks the method directly below as one every
    #        concrete subclass is REQUIRED to override
    def process(self, amount: float) -> str:
        ...
        # New words in this line:
        #   ...  -> the Ellipsis object, used here purely as a placeholder
        #        function body meaning "no implementation — subclasses must
        #        provide one." Equivalent to writing `pass`, but
        #        conventionally used for abstract/stub method bodies.


class CreditCardProcessor(PaymentProcessor):
    def process(self, amount: float) -> str:
        return f"Charged ${amount:.2f} to credit card"


class PayPalProcessor(PaymentProcessor):
    def process(self, amount: float) -> str:
        return f"Charged ${amount:.2f} via PayPal"


def demo_abc():
    print("\n--- Abstract Base Classes ---")
    for processor in (CreditCardProcessor(), PayPalProcessor()):
        print(processor.process(19.99))

    try:
        PaymentProcessor()   # can't instantiate an abstract class
    except TypeError as e:
        # New words in this line:
        #   TypeError  -> a BUILT-IN exception class (you don't have to
        #        write your own, as in core_language_mastery.py's
        #        BookNotFoundError, to catch or raise a standard one).
        #        Python itself raises this specific one when you try to
        #        instantiate an abstract class.
        print("Expected error:", e)


# ---------------------------------------------------------------------------
# Duck Typing & typing.Protocol — "structural" interfaces
# ---------------------------------------------------------------------------
# ABC above is Python's EXPLICIT way to define an interface: subclass it, or
# Python refuses to let you instantiate the subclass. Python also supports
# interfaces with no inheritance at all — "duck typing": if it walks like a
# duck and quacks like a duck, treat it as a duck. Any object with the right
# METHODS works, no matter what it inherits from.
class Honker(Protocol):
    def honk(self) -> str:
        ...


class Car2:
    """Never mentions Honker anywhere — no inheritance relationship at all."""
    def honk(self) -> str:
        return "Beep!"


class Clown:
    """Also never mentions Honker."""
    def honk(self) -> str:
        return "Squeeze-honk!"


def make_it_honk(thing: Honker) -> str:
    # New words in this line:
    #   thing: Honker  -> type hint saying "anything with a honk() method is
    #        acceptable here." A type checker (like mypy) accepts Car2 and
    #        Clown even though neither inherits from Honker. Python itself
    #        does NOT check this at all at runtime — it's purely a promise to
    #        tooling and human readers, unlike ABC's @abstractmethod, which
    #        Python enforces for real when you try to instantiate a subclass
    #        that skipped an abstract method.
    return thing.honk()


def demo_protocol():
    print("\n--- Duck Typing / Protocol ---")
    print(make_it_honk(Car2()))
    print(make_it_honk(Clown()))
    # Rule of thumb: reach for ABC when you want Python to actively ENFORCE
    # "you must implement this" at instantiation time. Reach for Protocol
    # when you just want to describe a shape of object for readability/type
    # checkers, without forcing unrelated classes into a shared inheritance
    # tree.


# ---------------------------------------------------------------------------
# SOLID Principles (one small example per letter)
# ---------------------------------------------------------------------------
# S — Single Responsibility: a class should have ONE reason to change.
class InvoicePrinter:
    """Only responsible for printing — not calculating totals, not saving to DB."""
    def print_invoice(self, invoice: dict):
        print(f"Invoice for {invoice['customer']}: ${invoice['total']}")


# O — Open/Closed: open for extension, closed for modification.
# (Adding a new Shape subclass doesn't require editing total_area)
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self) -> float:
        return self.side ** 2


def total_area(shapes: list[Shape]) -> float:
    # New words in this line:
    #   list[Shape]  -> a generic type hint (same style as core_language_mastery.py's
    #        dict[str, bool]) meaning "a list whose items are all Shape objects"
    return sum(s.area() for s in shapes)
    # New words in this line:
    #   sum(iterable)  -> built-in function: adds up every value produced by
    #        the generator expression `s.area() for s in shapes` — never
    #        needs editing when a new Shape subclass is added


# L — Liskov Substitution: subclasses must be usable wherever the base class is
# expected, without breaking behavior. (Circle/Square above both honor this —
# any Shape can be passed to total_area().)

# I — Interface Segregation: don't force a class to implement methods it
# doesn't need. Split fat interfaces into smaller, focused ones.
class Printable(ABC):
    @abstractmethod
    def print_out(self):
        ...


class Scannable(ABC):
    @abstractmethod
    def scan(self):
        ...


class SimplePrinter(Printable):
    """Doesn't need to implement scan() because Printable is small and focused."""
    def print_out(self):
        return "Printing..."


# D — Dependency Inversion: depend on abstractions, not concrete implementations.
class NotificationSender(ABC):
    @abstractmethod
    def send(self, message: str):
        ...


class EmailSender(NotificationSender):
    def send(self, message: str):
        return f"Emailing: {message}"


class OrderService:
    def __init__(self, sender: NotificationSender):   # depends on the ABSTRACTION
        self.sender = sender

    def place_order(self):
        return self.sender.send("Order placed!")


def demo_solid():
    print("\n--- SOLID ---")
    InvoicePrinter().print_invoice({"customer": "Alice", "total": 42})
    print("total_area:", total_area([Circle(2), Square(3)]))
    print(SimplePrinter().print_out())
    print(OrderService(EmailSender()).place_order())
    # Swap EmailSender() for SmsSender() with zero changes to OrderService — that's the payoff.


# ---------------------------------------------------------------------------
# Design Patterns
# ---------------------------------------------------------------------------

# --- Factory: centralizes object creation logic ---
class BookFactory:
    @staticmethod
    # New words in this line:
    #   @staticmethod  -> marks the method below as one that doesn't take
    #        `self` (or `cls`) — it doesn't need access to any particular
    #        instance, so it can be called as BookFactory.create(...) without
    #        ever creating a BookFactory() instance first
    def create(kind: str, title: str):
        if kind == "ebook":
            return {"type": "ebook", "title": title, "file_size": "10MB"}
        elif kind == "physical":
            # New words in this line:
            #   elif  -> "else if" — chains another condition after an `if`,
            #        checked only when the first `if` was False
            return {"type": "physical", "title": title, "shelf": "A1"}
        raise ValueError(f"Unknown book kind: {kind}")
        # New words in this line:
        #   ValueError  -> a built-in exception meaning "the type is right,
        #        but this particular value doesn't make sense here"


# --- Singleton: only one instance ever exists ---
class AppConfig:
    _instance = None
    # New words in this line:
    #   _instance (leading underscore)  -> a NAMING CONVENTION, not enforced
    #        by Python — signals "internal, don't touch this from outside
    #        the class"

    def __new__(cls):
        # New words in this line:
        #   __new__       -> a dunder method that runs BEFORE __init__ — it's
        #        actually responsible for CREATING the object in memory.
        #        __init__ only initializes an object that already exists.
        #        Overriding __new__ lets you return an EXISTING object
        #        instead of always creating a fresh one.
        #   cls           -> conventional parameter name meaning "the class
        #        itself" (AppConfig), the same role `self` plays for an
        #        instance
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # New words in this line:
            #   super().__new__(cls)  -> calls the PARENT class's __new__ to
            #        actually allocate the object in memory — same
            #        relationship as super().__init__() from
            #        core_language_mastery.py, but for the creation step
            #        instead of the initialization step
            cls._ins0tance.settings = {}
        return cls._instance


# --- Strategy: swap an algorithm at runtime ---
class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float:
        ...


class NoDiscount(DiscountStrategy):
    def apply(self, price):
        return price


class TenPercentOff(DiscountStrategy):
    def apply(self, price):
        return price * 0.9


class Checkout:
    def __init__(self, strategy: DiscountStrategy):
        self.strategy = strategy

    def total(self, price: float) -> float:
        return self.strategy.apply(price)


# --- Observer: notify subscribers when something happens ---
class EventPublisher:
    def __init__(self):
        self._subscribers = []

    def subscribe(self, callback):
        self._subscribers.append(callback)

    def publish(self, event: str):
        for callback in self._subscribers:
            callback(event)


# --- Repository: hides data-access details behind a simple interface ---
class BookRepository:
    """In real code this would talk to MongoDB/SQL. Callers don't need to know that."""
    def __init__(self):
        self._books = {}

    def add(self, book_id: str, book: dict):
        self._books[book_id] = book

    def get(self, book_id: str) -> dict | None:
        # New words in this line:
        #   dict | None  -> a union type hint meaning "returns a dict, or
        #        None." `|` between two types means "either type is
        #        acceptable" — the modern (Python 3.10+) alternative
        #        spelling of core_language_mastery.py's Optional[dict]
        return self._books.get(book_id)


# --- Adapter: makes an incompatible interface fit what your code expects ---
class OldLogger:
    def write_log(self, msg):   # legacy method name
        print(f"[old logger] {msg}")


class LoggerAdapter:
    """Adapts OldLogger's write_log() to the .log() interface the rest of the app expects."""
    def __init__(self, old_logger: OldLogger):
        self._old_logger = old_logger

    def log(self, msg):
        self._old_logger.write_log(msg)


def demo_patterns():
    print("\n--- Design Patterns ---")

    print("Factory:", BookFactory.create("ebook", "1984"))

    cfg1, cfg2 = AppConfig(), AppConfig()
    cfg1.settings["debug"] = True
    print("Singleton — same instance:", cfg1 is cfg2, cfg2.settings)

    print("Strategy (no discount):", Checkout(NoDiscount()).total(100))
    print("Strategy (10% off):", Checkout(TenPercentOff()).total(100))

    publisher = EventPublisher()
    publisher.subscribe(lambda e: print(f"Subscriber A got: {e}"))
    # New words in this line:
    #   lambda e: expr  -> a small ANONYMOUS function written inline: `e` is
    #        its parameter, and everything after the `:` is the single
    #        expression it evaluates and returns. Equivalent to writing:
    #            def handler(e):
    #                return print(...)
    #        and passing `handler` instead — a lambda can only ever contain
    #        one expression, no statements, no multiple lines.
    publisher.subscribe(lambda e: print(f"Subscriber B got: {e}"))
    publisher.publish("book_borrowed")

    repo = BookRepository()
    repo.add("b1", {"title": "1984"})
    print("Repository:", repo.get("b1"))

    LoggerAdapter(OldLogger()).log("Adapter pattern in action")


# ---------------------------------------------------------------------------
# @classmethod — alternate constructors
# ---------------------------------------------------------------------------
class Pizza:
    def __init__(self, toppings: list[str]):
        self.toppings = toppings

    @classmethod
    # New words in this line:
    #   @classmethod  -> like @staticmethod (see BookFactory above), doesn't
    #        take `self` — but DOES take `cls` as its first argument, the
    #        exact same `cls` you met in __new__. Lets a method build and
    #        return a new instance without the caller writing out __init__'s
    #        full argument list by hand.
    def margherita(cls):
        return cls(["mozzarella", "basil"])
        # New words in this line:
        #   cls([...])  -> calling `cls` like a function builds a new
        #        instance of whichever class this was called on — Pizza, or
        #        even a subclass of Pizza, whichever `cls` happens to be.
        #        This IS the point of @classmethod: a descriptively-named
        #        "alternate constructor," instead of one crowded __init__
        #        trying to handle every possible way to build a Pizza.

    @classmethod
    def pepperoni(cls):
        return cls(["mozzarella", "pepperoni"])


def demo_classmethod():
    print("\n--- @classmethod ---")
    print("Margherita:", Pizza.margherita().toppings)
    print("Pepperoni:", Pizza.pepperoni().toppings)
    # Compare to BookFactory.create() above: that @staticmethod has NO
    # automatic access to the class at all (no self, no cls) — it's really
    # just a regular function that happens to live inside the class for
    # organization. @classmethod differs by receiving `cls`, which is what
    # lets it turn around and build an instance of that class.


# ---------------------------------------------------------------------------
# Mixins & Multiple Inheritance
# ---------------------------------------------------------------------------
# A mixin is a small class that's never meant to stand on its own — it exists
# purely to be combined with another class via multiple inheritance, bolting
# on one focused capability.
class JSONMixin:
    """Reusable: any class that mixes this in gets to_json() for free."""
    def to_json(self) -> str:
        import json
        return json.dumps(self.__dict__)
        # New words in this line:
        #   self.__dict__  -> every instance's own attribute dict (same thing
        #        you'd see via raw.__dict__ on any freshly built object).
        #        json.dumps() turns it into a JSON string. This works for ANY
        #        class that mixes JSONMixin in, because it never hardcodes
        #        attribute names — it just reads whatever's already there.


class Employee(JSONMixin):
    # New words in this line:
    #   class Employee(JSONMixin)  -> single inheritance here, but the SAME
    #        syntax extends to multiple base classes: `class Foo(A, B, C)`
    #        combines all three at once. Employee "IS-A" nothing in
    #        particular — it just picks up JSONMixin's behavior as an add-on.
    def __init__(self, name: str, salary: float):
        self.name = name
        self.salary = salary


def demo_mixin():
    print("\n--- Mixins ---")
    print(Employee("Itay", 5000).to_json())
    # New words in this line:
    #   MRO (Method Resolution Order)  -> when a class inherits from more
    #        than one base and two bases define the same method name, Python
    #        needs a rule for which one wins. It checks the class itself
    #        first, then each base (and everything THAT base inherits from)
    #        left to right, in the order written in the class definition.
    #        You can see this order for any class via ClassName.__mro__.
    print("MRO:", [c.__name__ for c in Employee.__mro__])


# ---------------------------------------------------------------------------
# Dataclasses & @property
# ---------------------------------------------------------------------------
@dataclass
class Book:
    title: str
    author: str
    _available: bool = field(default=True, repr=False)
    # New words in this line:
    #   field(...)      -> dataclasses' way to configure a field beyond a
    #        simple default value (finer control than just `= True`)
    #   default=True    -> sets the default value, same effect as `= True`
    #        would have on its own
    #   repr=False      -> hides this specific field from the
    #        auto-generated __repr__ (useful here since it's exposed below
    #        through a differently-named public property instead)

    @property
    # New words in this line:
    #   @property  -> lets you call `book.available` like a plain attribute
    #        (no parentheses), but it actually runs the method below every
    #        time it's accessed
    def available(self) -> bool:
        return self._available

    @available.setter
    # New words in this line:
    #   @available.setter  -> pairs with @property above; marks the method
    #        below as what runs whenever code does `book.available = X`,
    #        letting you validate/transform X instead of just overwriting
    #        the attribute directly
    def available(self, value: bool):
        if not isinstance(value, bool):
            # New words in this line:
            #   isinstance(value, Type)  -> built-in function: checks
            #        whether `value` is of that type (or a subclass of it)
            #        — more flexible than `type(value) == bool`, which would
            #        reject subclasses of bool
            raise TypeError("available must be a bool")
        self._available = value


def demo_dataclass_property():
    print("\n--- Dataclasses & @property ---")
    book = Book("1984", "Orwell")
    print(book, "available:", book.available)
    book.available = False
    print("after borrowing:", book.available)
    try:
        book.available = "nope"   # rejected by the setter's validation
    except TypeError as e:
        print("Expected error:", e)


# ---------------------------------------------------------------------------
# Idioms & Conventions — the unwritten rules, not new syntax
# ---------------------------------------------------------------------------
# Class names: PascalCase (AppConfig, PaymentProcessor) — never snake_case
# (app_config) or all-lowercase (paymentmastercard). Functions, methods, and
# variables stay snake_case (process_payment, total_books). Python doesn't
# enforce this — nothing crashes if you ignore it — but every other Python
# codebase you read or contribute to assumes it, so a name in the wrong case
# reads as a beginner mistake even when the code runs fine.

def demo_is_vs_equals():
    print("\n--- `is` vs `==` ---")

    class Coordinate:
        def __init__(self, x, y):
            self.x, self.y = x, y

        def __eq__(self, other):
            return self.x == other.x and self.y == other.y
            # New words in this line:
            #   __eq__  -> the dunder Python calls whenever you write
            #        `a == b` for two objects of this class. Overriding it
            #        lets you define what "equal" means for YOUR data (here:
            #        same x and y), instead of the default (same object in
            #        memory).

    p1, p2 = Coordinate(1, 2), Coordinate(1, 2)
    print("p1 is p2:", p1 is p2)   # False — two separate objects were built
    print("p1 == p2:", p1 == p2)   # True  — __eq__ says "same x/y, close enough"
    # This is exactly why a Singleton's __new__ check must use `is None`,
    # never `== None`: `is` compares raw identity and can never be fooled by
    # a class's own __eq__ override, because it doesn't call __eq__ at all.
    # `==` on the other hand does whatever __eq__ says — which, as just
    # shown, doesn't have to mean identity.


def demo_init_returns_none():
    print("\n--- __init__ always returns None ---")

    class Wallet:
        def __init__(self, amount: float) -> None:
            # New words in this line:
            #   -> None  -> the correct return type hint for __init__,
            #        always. __init__'s only job is to set attributes on
            #        `self` — it is never allowed to `return` a value
            #        (Python raises TypeError if you try `return something`
            #        inside __init__). Hinting it as `-> float` (an easy
            #        mistake when you're used to regular functions returning
            #        data) promises a float comes back, but nothing ever
            #        does.
            self.amount = amount

    w = Wallet(80)
    print("Wallet.__init__(w, 80) actually returned:", Wallet.__init__(w, 80))


if __name__ == "__main__":
    demo_inheritance_vs_composition()
    demo_abc()
    demo_protocol()
    demo_solid()
    demo_patterns()
    demo_classmethod()
    demo_mixin()
    demo_dataclass_property()
    demo_is_vs_equals()
    demo_init_returns_none()