"""
18_inheritance_deep_dive.py

A focused deep dive on ONE topic from Section 2 (02_oop_design_principles.py):
inheritance itself. That file covers inheritance vs. composition, ABCs, and
mixins alongside a dozen other design topics — this file slows down and goes
much further on inheritance specifically:
    - Single inheritance & why it exists (recap)
    - super().__init__() — what it actually is, and the explicit alternative
    - Method overriding — replacing vs. extending a parent's behavior
    - Multiple inheritance, the diamond problem, and MRO in depth
    - Cooperative multi-inheritance with super() chains
    - isinstance() vs issubclass() vs type()
    - Abstract classes as enforced contracts (recap + abstract properties)
    - Common pitfalls
    - A worked example: a small polymorphic payroll system

Run: python 18_inheritance_deep_dive.py
"""

from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# 1. Single inheritance — recap
# ---------------------------------------------------------------------------
# Rule of thumb: put what's SHARED in the parent, put what's DIFFERENT in
# each subclass.
class Animal:
    def __init__(self, name: str):
        self.name = name
        self.is_alive = True

    def eat(self) -> str:
        return f"{self.name} is eating"


class Dog(Animal):
    # Dog defines NOTHING new here — it inherits __init__ and eat() as-is,
    # and only adds a method Animal never had.
    def speak(self) -> str:
        return "Woof"


class Cat(Animal):
    def speak(self) -> str:
        return "Meow"


def demo_single_inheritance():
    print("\n--- Single inheritance ---")
    d = Dog("Rex")
    print(d.eat())     # inherited from Animal, unchanged
    print(d.speak())   # Dog's own method, Animal never had this


# ---------------------------------------------------------------------------
# 2. Method overriding — replacing a parent's method
# ---------------------------------------------------------------------------
# Overriding means the SUBCLASS defines a method with the same name as one
# the parent already has. When you call it on a subclass instance, Python
# finds the subclass's version first and never looks further up.
class Fish(Animal):
    def move(self) -> str:
        return f"{self.name} swims"


class Animal2(Animal):
    """Same as Animal, but adds move() so Fish has something to override."""
    def move(self) -> str:
        return f"{self.name} moves"


def demo_overriding():
    print("\n--- Method overriding ---")

    class Fish2(Animal2):
        def move(self) -> str:
            return f"{self.name} swims"

    f = Fish2("Nemo")
    print(f.move())   # Fish2's own version wins
    print(f.eat())     # still inherited unchanged from Animal (via Animal2)


# ---------------------------------------------------------------------------
# 3. super().__init__() — what it really is, and the explicit alternative
# ---------------------------------------------------------------------------
# Overriding __init__ REPLACES the parent's __init__ entirely, unless you
# explicitly call it too. super() is how you do that.
class AnimalV2:
    def __init__(self, name: str):
        self.name = name
        self.is_alive = True


class DogV2(AnimalV2):
    def __init__(self, name: str, breed: str):
        super().__init__(name)
        # New words in this line:
        #   super().__init__(name)  -> super() returns a proxy object bound
        #        to THIS instance, representing "the next class in the MRO
        #        after DogV2." Calling .__init__(name) on it runs
        #        AnimalV2's __init__ with self already supplied — you only
        #        pass the REMAINING arguments (name), never self.
        self.breed = breed


class DogBroken(AnimalV2):
    """Forgets to call super().__init__() — a common bug."""
    def __init__(self, name: str, breed: str):
        self.breed = breed
        # self.name and self.is_alive are NEVER set here.


def demo_super_vs_explicit():
    print("\n--- super().__init__() ---")
    d = DogV2("Rex", "Labrador")
    print(d.name, d.is_alive, d.breed)

    # super() is equivalent (in single inheritance) to calling the parent
    # class directly and passing self explicitly:
    class DogExplicit(AnimalV2):
        def __init__(self, name: str, breed: str):
            AnimalV2.__init__(self, name)
            # New words in this line:
            #   AnimalV2.__init__(self, name)  -> calling a method directly
            #        on the CLASS (not an instance) requires passing `self`
            #        yourself, since there's no instance to bind it to yet.
            #        This does the same job as super().__init__(name) here,
            #        but super() is preferred in real code because it
            #        automatically follows the MRO — this hardcodes
            #        "AnimalV2" by name, which breaks the cooperative chain
            #        you'll see in multiple inheritance below.
            self.breed = breed

    print(DogExplicit("Fido", "Poodle").name)

    try:
        broken = DogBroken("Ghost", "Unknown")
        print(broken.name)   # never set — this line raises
    except AttributeError as e:
        print("Expected error (forgot super().__init__()):", e)


# ---------------------------------------------------------------------------
# 4. Multiple inheritance, the diamond problem, and MRO
# ---------------------------------------------------------------------------
#         A
#        / \
#       B   C
#        \ /
#         D
# D inherits from both B and C, which both inherit from A. If B and C both
# override the same method, which one does D get? Python answers this with
# the MRO (Method Resolution Order): a single, deterministic search order
# computed by the C3 linearization algorithm. In practice, for a simple case
# like this, the rule is "depth-first, left-to-right, but never put a class
# before one of its own children" — you can always just READ it off
# ClassName.__mro__ instead of computing it by hand.
class A:
    def who(self) -> str:
        return "A"


class B(A):
    def who(self) -> str:
        return "B -> " + super().who()
        # New words in this line:
        #   super().who() here does NOT necessarily mean "call A.who()".
        #   It means "call whichever class comes next after B in the MRO
        #   of the ACTUAL instance this runs on" — see demo below, where
        #   that's C, not A.


class C(A):
    def who(self) -> str:
        return "C -> " + super().who()


class D(B, C):
    def who(self) -> str:
        return "D -> " + super().who()


def demo_diamond_and_mro():
    print("\n--- Diamond problem & MRO ---")
    print("MRO:", [cls.__name__ for cls in D.__mro__])
    print(D().who())
    # Expected: D -> B -> C -> A
    # Every class's super() call is "cooperative": it doesn't jump straight
    # to ITS OWN parent, it jumps to the NEXT class in the MRO of the actual
    # object. Since D's MRO is [D, B, C, A, object], B's super() lands on C
    # (not A) — that's what makes the diamond resolve without calling A
    # twice.


# ---------------------------------------------------------------------------
# 5. isinstance() vs issubclass() vs type()
# ---------------------------------------------------------------------------
def demo_isinstance_vs_issubclass():
    print("\n--- isinstance vs issubclass vs type ---")
    d = Dog("Rex")

    print("isinstance(d, Dog):", isinstance(d, Dog))       # True — exact class
    print("isinstance(d, Animal):", isinstance(d, Animal))  # True — Dog IS-A Animal too
    print("type(d) == Animal:", type(d) == Animal)          # False — type() is EXACT, no subclass credit
    print("issubclass(Dog, Animal):", issubclass(Dog, Animal))
    # New words in this line:
    #   issubclass(ClassA, ClassB)  -> like isinstance(), but compares two
    #        CLASSES to each other instead of an instance to a class. Answers
    #        "is ClassA a subclass of (or the same as) ClassB?" Every class
    #        is considered a subclass of itself, so issubclass(Dog, Dog) is
    #        also True.
    print("issubclass(Dog, Dog):", issubclass(Dog, Dog))
    print("issubclass(Animal, Dog):", issubclass(Animal, Dog))  # False — wrong direction


# ---------------------------------------------------------------------------
# 6. Abstract classes as enforced contracts
# ---------------------------------------------------------------------------
# Recap from 02_oop_design_principles.py, extended with an abstract PROPERTY.
class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        # New words in this line:
        #   stacking @property under @abstractmethod  -> requires every
        #        concrete subclass to provide a `name` PROPERTY (accessed
        #        like an attribute, `shape.name`, no parentheses) — not just
        #        any method. Order matters: @property goes on top (applied
        #        last).
        ...


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius ** 2

    @property
    def name(self) -> str:
        return "circle"


def demo_abstract_contract():
    print("\n--- Abstract classes as contracts ---")
    c = Circle(3)
    print(c.name, "area:", round(c.area(), 2))

    try:
        Shape()   # can't instantiate — area() and name are unimplemented
    except TypeError as e:
        print("Expected error:", e)

    class BrokenSquare(Shape):
        def __init__(self, side):
            self.side = side
        # forgot to implement area() and name

    try:
        BrokenSquare(4)
    except TypeError as e:
        print("Expected error (missing abstract members):", e)


# ---------------------------------------------------------------------------
# 7. Common pitfalls
# ---------------------------------------------------------------------------
def demo_pitfalls():
    print("\n--- Common pitfalls ---")

    # Pitfall 1: forgetting super().__init__() — already shown above, but
    # it's the single most common inheritance bug in real code.

    # Pitfall 2: overriding a method with an incompatible signature, which
    # silently breaks polymorphism for any caller expecting the base
    # signature (Liskov Substitution violation from 02_oop_design_principles.py).
    class Base:
        def resize(self, factor: float):
            return f"resized by {factor}"

    class Bad(Base):
        def resize(self, factor: float, unit: str):  # now REQUIRES a 2nd arg
            return f"resized by {factor} {unit}"

    def resize_all(items, factor):
        return [item.resize(factor) for item in items]

    try:
        resize_all([Base(), Bad()], 2.0)
    except TypeError as e:
        print("Expected error (Bad.resize needs an extra argument):", e)

    # Pitfall 3: deep, rigid hierarchies. If you find yourself overriding
    # the same method 4 levels down to "undo" behavior from 2 levels up,
    # that's usually a sign composition (HAS-A) would have been the better
    # fit than inheritance (IS-A) — see demo_inheritance_vs_composition() in
    # 02_oop_design_principles.py.


# ---------------------------------------------------------------------------
# 8. Worked example: a small polymorphic payroll system
# ---------------------------------------------------------------------------
class Employee:
    def __init__(self, name: str, base_salary: float):
        self.name = name
        self.base_salary = base_salary

    def pay(self) -> float:
        return self.base_salary


class Manager(Employee):
    def __init__(self, name: str, base_salary: float, bonus: float):
        super().__init__(name, base_salary)
        self.bonus = bonus

    def pay(self) -> float:
        return self.base_salary + self.bonus


class SalesRep(Employee):
    def __init__(self, name: str, base_salary: float, commission: float, sales: float):
        super().__init__(name, base_salary)
        self.commission = commission
        self.sales = sales

    def pay(self) -> float:
        return self.base_salary + self.commission * self.sales


def demo_payroll_polymorphism():
    print("\n--- Polymorphism in practice ---")
    employees = [
        Employee("Alex", 3000),
        Manager("Sam", 4000, 500),
        SalesRep("Jo", 2000, 0.1, 5000),
    ]
    for e in employees:
        # The loop never checks `type(e)` — it just calls .pay() and trusts
        # each class's own override to do the right thing. THIS is the
        # actual payoff of overriding: callers stay simple, and each class
        # is responsible for its own behavior.
        print(f"{e.name}: {e.pay()}")


if __name__ == "__main__":
    demo_single_inheritance()
    demo_overriding()
    demo_super_vs_explicit()
    demo_diamond_and_mro()
    demo_isinstance_vs_issubclass()
    demo_abstract_contract()
    demo_pitfalls()
    demo_payroll_polymorphism()
