"""
19_advanced_oop.py

The advanced tier of Python OOP — the concepts that sit past
02_oop_design_principles.py and 18_inheritance_deep_dive.py:
    - Descriptors — the actual machinery @property is built on
    - __slots__ — restricting instance attributes, and why
    - Operator overloading beyond __eq__: ordering, hashing, the iterator
      protocol, making instances callable
    - Metaclasses — type() as a class factory, and __init_subclass__ as the
      lighter modern alternative
    - ABC vs. Protocol, done right — nominal vs. structural typing, and why
      you normally do NOT inherit from a Protocol
    - Design pattern: Strategy — composition instead of multiple inheritance,
      rebuilding a broken multi-inheritance mess the right way

Assumes everything in core_language_mastery.py, 02_oop_design_principles.py,
and 18_inheritance_deep_dive.py (see GLOSSARY.md) — including @dataclass,
class-based context managers, ABC/@abstractmethod, Protocol, __eq__, and MRO.

Run: python 19_advanced_oop.py
"""

from abc import ABC, abstractmethod
from functools import total_ordering
from typing import Protocol


# ---------------------------------------------------------------------------
# 1. Descriptors — the machinery @property is built on
# ---------------------------------------------------------------------------
# @property is convenient but it's per-class: write a validated "positive
# number" property on 3 different classes and you copy-paste the same
# get/set logic 3 times. A descriptor is a REUSABLE object that owns that
# logic once, then attaches to any attribute on any class.
#
# The protocol: any class defining __get__ (and usually __set__) becomes a
# descriptor. When you access instance.attr, Python checks: is `attr` on the
# CLASS a descriptor? If so, it calls descriptor.__get__(instance, owner)
# instead of doing a plain dict lookup. This is literally how @property,
# methods, and @staticmethod/@classmethod all work under the hood.
class PositiveNumber:
    def __set_name__(self, owner, name):
        # New words in this line:
        #   __set_name__(self, owner, name)  -> Python calls this
        #        automatically at CLASS-DEFINITION time (not per-instance),
        #        telling the descriptor what attribute name it was assigned
        #        to. `owner` is the class it's being defined on, `name` is
        #        the attribute name as written in that class's body.
        self.private_name = "_" + name

    def __get__(self, instance, owner):
        # New words in this line:
        #   __get__(self, instance, owner)  -> runs whenever someone reads
        #        instance.attr. `instance` is the object being read from
        #        (None if accessed on the class itself), `owner` is the
        #        class. Returning getattr(instance, private_name) reads the
        #        REAL value we stashed under a private name.
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        # New words in this line:
        #   __set__(self, instance, value)  -> runs whenever someone writes
        #        instance.attr = value. This is where validation lives —
        #        ONE implementation, reused by every class that uses this
        #        descriptor.
        if value < 0:
            raise ValueError(f"must be >= 0, got {value}")
        setattr(instance, self.private_name, value)


class BankAccount:
    balance = PositiveNumber()   # descriptor instance, shared machinery

    def __init__(self, owner: str, balance: float):
        self.owner = owner
        self.balance = balance   # goes through PositiveNumber.__set__


class Inventory:
    quantity = PositiveNumber()   # SAME descriptor class, different attribute

    def __init__(self, sku: str, quantity: int):
        self.sku = sku
        self.quantity = quantity


def demo_descriptors():
    print("\n--- Descriptors: the machinery behind @property ---")
    acct = BankAccount("Itay", 100)
    print(acct.owner, acct.balance)

    inv = Inventory("SKU-1", 50)
    print(inv.sku, inv.quantity)
    # ONE PositiveNumber class enforces "no negatives" on two totally
    # unrelated classes' attributes. That reuse is the entire point —
    # @property alone would need this logic written twice.

    try:
        acct.balance = -5
    except ValueError as e:
        print("Expected error (descriptor validation):", e)


# ---------------------------------------------------------------------------
# 2. __slots__ — restricting instance attributes
# ---------------------------------------------------------------------------
# By default every instance gets a __dict__ — a real dict holding its
# attributes, created fresh per object. __slots__ tells Python "this class
# only ever has these attributes," which:
#   (a) removes the per-instance __dict__, saving real memory when you have
#       many instances (a common senior-level perf lever)
#   (b) makes typos loud: instance.attr = x for an attr not in __slots__
#       raises AttributeError immediately, instead of silently creating a
#       new attribute nobody meant to add
class PointDict:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


class PointSlots:
    __slots__ = ("x", "y")
    # New words in this line:
    #   __slots__ = (...)  -> a class-level tuple of the ONLY attribute
    #        names instances of this class are allowed to have. No __dict__
    #        is created per instance at all.

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y


def demo_slots():
    print("\n--- __slots__ ---")
    pd = PointDict(1, 2)
    pd.z = 99   # allowed — PointDict has a normal __dict__
    print("PointDict allows pd.z =", pd.z)

    ps = PointSlots(1, 2)
    try:
        ps.z = 99   # not in __slots__
    except AttributeError as e:
        print("Expected error (__slots__ blocks new attributes):", e)
    # Note: PositiveNumber above still works fine WITH __slots__ — descriptors
    # live on the CLASS, not the instance, so they don't need a per-instance
    # __dict__ at all. This is not a coincidence: __slots__ itself is
    # implemented using descriptors.


# ---------------------------------------------------------------------------
# 3. Operator overloading beyond __eq__, and the iterator protocol
# ---------------------------------------------------------------------------
@total_ordering
class Money:
    # New words in this line:
    #   @total_ordering  -> given __eq__ and ONE of __lt__/__le__/__gt__/
    #        __ge__, this decorator fills in the rest for you. Write the
    #        comparison logic once instead of all 4 methods by hand.
    def __init__(self, cents: int):
        self.cents = cents

    def __eq__(self, other) -> bool:
        return self.cents == other.cents

    def __lt__(self, other) -> bool:
        return self.cents < other.cents

    def __hash__(self) -> int:
        # New words in this line:
        #   defining __eq__ without __hash__ makes instances UNHASHABLE —
        #        Python sets __hash__ to None automatically whenever a class
        #        defines __eq__ but not __hash__, because two "equal"
        #        objects with different hashes would break dicts/sets. If
        #        equal objects should be interchangeable as dict keys, hash
        #        them the same way you compare them.
        return hash(self.cents)

    def __repr__(self) -> str:
        return f"${self.cents / 100:.2f}"


class Countdown:
    """A hand-rolled iterator, showing the protocol property()/for loops rely on."""
    def __init__(self, start: int):
        self.current = start

    def __iter__(self):
        # New words in this line:
        #   __iter__(self)  -> called once when `for x in obj:` begins.
        #        Must return an object with __next__ — here that's `self`.
        return self

    def __next__(self):
        # New words in this line:
        #   __next__(self)  -> called once per loop iteration. Must raise
        #        StopIteration to signal "no more items" — that's what
        #        actually ends a for loop under the hood.
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


class Multiplier:
    """Making an instance callable, like a function."""
    def __init__(self, factor: float):
        self.factor = factor

    def __call__(self, value: float) -> float:
        # New words in this line:
        #   __call__(self, ...)  -> defining this lets you write
        #        instance(args) directly, as if the instance WERE a
        #        function. Used heavily for stateful callables (e.g. a
        #        configured validator, decorators-as-classes).
        return value * self.factor


def demo_operator_overloading():
    print("\n--- Operator overloading & iterator protocol ---")
    prices = [Money(500), Money(150), Money(999)]
    print("sorted:", sorted(prices))          # __lt__ (+ total_ordering) at work
    print("500 == 500:", Money(500) == Money(500))
    print("500 <= 999:", Money(500) <= Money(999))   # filled in by total_ordering
    print({Money(500): "five dollars"})       # requires __hash__

    print("Countdown from 3:", list(Countdown(3)))   # uses __iter__/__next__

    double = Multiplier(2)
    print("double(21) =", double(21))          # uses __call__


# ---------------------------------------------------------------------------
# 4. Metaclasses — type() as a class factory
# ---------------------------------------------------------------------------
# You already know type(obj) returns obj's class. type() has a second job:
# type(name, bases, namespace) BUILDS a class, live, at runtime. `class Foo:`
# is syntax sugar that ends up calling exactly this.
def demo_type_as_factory():
    print("\n--- type() as a class factory ---")

    def greet(self):
        return f"hi, I'm {self.name}"

    Greeter = type(
        "Greeter",                       # class name
        (object,),                       # base classes (tuple)
        {"greet": greet, "name": "Bot"},  # namespace: methods + class attrs
    )
    # New words in this line:
    #   type(name, bases, namespace)  -> the 3-argument form of type()
    #        constructs a brand-new class object, equivalent to writing
    #        `class Greeter(object): name = "Bot"; greet = greet`. Rarely
    #        used directly, but this IS what the `class` statement compiles
    #        down to — a metaclass is anything that customizes this step.
    g = Greeter()
    print(g.greet())


# A metaclass is a class whose INSTANCES are themselves classes — the
# default metaclass for everything is `type` itself. Writing a custom one
# lets you hook into class CREATION, not just instance creation.
class EnforceDocstring(type):
    def __new__(mcs, name, bases, namespace):
        # New words in this line:
        #   class EnforceDocstring(type)  -> subclassing `type` makes this
        #        a metaclass. Its __new__ runs once, when a class USING it
        #        is being DEFINED (not when that class is instantiated).
        #        `mcs` (metaclass) plays the role `cls` plays for normal
        #        classes.
        for attr_name, value in namespace.items():
            if callable(value) and not attr_name.startswith("_") and not value.__doc__:
                raise TypeError(f"{name}.{attr_name} is missing a docstring")
        return super().__new__(mcs, name, bases, namespace)


class WellDocumented(metaclass=EnforceDocstring):
    def process(self):
        """Processes something."""
        return "ok"


def demo_custom_metaclass():
    print("\n--- Custom metaclass ---")
    print(WellDocumented().process())

    try:
        class Undocumented(metaclass=EnforceDocstring):
            def process(self):   # no docstring — caught at CLASS-DEFINITION time
                return "oops"
    except TypeError as e:
        print("Expected error (metaclass caught it before instantiation):", e)


# Most "I need to hook into subclass creation" needs are better served by
# __init_subclass__ — a plain classmethod-like hook, no metaclass required.
class Plugin:
    registry: list = []

    def __init_subclass__(cls, **kwargs):
        # New words in this line:
        #   __init_subclass__(cls, **kwargs)  -> called automatically
        #        whenever a SUBCLASS of Plugin is defined, no metaclass
        #        needed. This is the lightweight 95%-of-cases alternative —
        #        reach for a real metaclass only when even this isn't
        #        enough (e.g. changing how the class itself behaves, not
        #        just reacting to its creation).
        super().__init_subclass__(**kwargs)
        Plugin.registry.append(cls)


class CsvPlugin(Plugin):
    pass


class JsonPlugin(Plugin):
    pass


def demo_init_subclass():
    print("\n--- __init_subclass__ (the lighter alternative) ---")
    print("Auto-registered plugins:", [c.__name__ for c in Plugin.registry])


# ---------------------------------------------------------------------------
# 5. ABC vs. Protocol, done right
# ---------------------------------------------------------------------------
# ABC = NOMINAL typing: a class only counts as "a Shape" if it explicitly
#       writes `class Circle(Shape):`. The relationship is declared.
# Protocol = STRUCTURAL typing: a class counts as "a Sender" just by HAVING
#       a matching send() method — no inheritance, no declaration at all.
#       This is Python's version of "if it walks like a duck..."
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...


class Sender(Protocol):
    def send(self, message: str) -> str:
        ...


class Email:
    """Never mentions Sender anywhere. Still satisfies the protocol."""
    def send(self, message: str) -> str:
        return f"email: {message}"


def notify(sender: Sender, message: str) -> str:
    # New words in this line:
    #   typing a parameter as `Sender` (a Protocol) means "anything with a
    #        matching send() method is accepted" — type checkers (mypy)
    #        verify this structurally, and at runtime Python doesn't check
    #        it at all; duck typing just works because we only ever call
    #        .send() on it.
    return sender.send(message)


def demo_abc_vs_protocol():
    print("\n--- ABC (nominal) vs. Protocol (structural) ---")
    print(notify(Email(), "hello"))
    # Email never wrote `class Email(Sender):` — and it doesn't need to.
    # THIS is the entire point of Protocol: you get the type-safety benefit
    # without forcing every implementer to know your Protocol exists, which
    # matters most for classes you don't own (stdlib types, third-party
    # objects) that can never be retrofitted with an explicit base class.
    #
    # Compare to Shape (ABC) above: you CANNOT pass a random class with an
    # area() method to something expecting a Shape — it must explicitly
    # inherit `class Circle(Shape):`, or isinstance(x, Shape) is False and
    # Shape() itself can't even be instantiated unless area() is implemented.
    #
    # practice.py note: `class Whatsapp(messages):` (where `messages` is a
    # Protocol) explicitly inherits from a Protocol. That's legal Python,
    # but it defeats the reason to reach for Protocol in the first place —
    # if you're going to inherit anyway, an ABC says your intent more
    # clearly. Protocol earns its keep specifically when you DON'T want (or
    # can't force) inheritance.


# ---------------------------------------------------------------------------
# 6. Design pattern: Strategy — composition instead of multiple inheritance
# ---------------------------------------------------------------------------
# The Strategy pattern: instead of baking multiple behaviors into one class
# via multiple inheritance (fragile — see the diamond problem in
# 18_inheritance_deep_dive.py), you HOLD other objects that each implement
# one behavior, and delegate to them. HAS-A instead of IS-A.
class Channel(Protocol):
    def send(self, message: str) -> str:
        ...


class WhatsappChannel:
    def send(self, message: str) -> str:
        return f"whatsapp: {message}"


class DiscordChannel:
    def send(self, message: str) -> str:
        return f"discord: {message}"


class Notifier:
    """
    Rebuild of the broken ReturningMessages class from practice.py, using
    composition. The original tried to get "an object that can send through
    several channels" by INHERITING from Whatsapp AND discord AND messages
    at once — which produced a super().__init__() call sitting in the class
    body (runs at class-definition time, not instance-creation time, so it
    errors immediately) and two __repr__ definitions silently overwriting
    each other.
    """
    def __init__(self, channels: list[Channel]):
        # New words in this line:
        #   self.channels = channels  -> HOLDING a list of channel objects
        #        as an attribute, rather than inheriting from their classes.
        #        Each element just needs a .send() method — that's the
        #        Channel Protocol above, structurally satisfied, no
        #        inheritance chain to reason about.
        self.channels = channels

    def broadcast(self, message: str) -> list[str]:
        return [channel.send(message) for channel in self.channels]


def demo_strategy_pattern():
    print("\n--- Strategy pattern: composition instead of multiple inheritance ---")
    notifier = Notifier([WhatsappChannel(), DiscordChannel()])
    for result in notifier.broadcast("You have 5 new notifications"):
        print(result)
    # No super() called in a class body, no __repr__ clobbering itself, no
    # MRO to puzzle out — adding a 3rd channel later means writing ONE new
    # class with a send() method and appending it to the list. Nothing else
    # changes.


if __name__ == "__main__":
    demo_descriptors()
    demo_slots()
    demo_operator_overloading()
    demo_type_as_factory()
    demo_custom_metaclass()
    demo_init_subclass()
    demo_abc_vs_protocol()
    demo_strategy_pattern()
