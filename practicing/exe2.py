# Exercise: Python Descriptors (v2) — build it yourself
#
# Goal: build a working descriptor from scratch with NO safety net. Think
# through each method's contract before writing it. Reference object.__set_name__
# if you need to recall how base types route attribute access.

# ======================================================================
# PART 1 — Infrastructure you will use (do not modify)
# ======================================================================

# This is the base type of everything. Instances can hold arbitrary
# attributes, and attribute access follows the data-model rules:
#   - __set_name__ is called once, with (owner_class, attribute_name),
#     when the descriptor is bound to the class, AFTER the class body runs.
#   - __set__(self, instance, value) is called on MORE specific assignment
#     than __get__ (i.e. setting beats reading).
#   - __get__(self, instance, owner) is called on LESS specific reads.
#
# RULE OF THUMB for a classic data descriptor:
#   Store the value under a private name, validate in __set__, fetch in __get__.


# ======================================================================
# PART 2 — Your task
# ======================================================================
#
# Write a descriptor class called 'Color' that enforces this contract:
#=
#   1. __set_name__:  capture the public attribute name.
#   2. __set__:       the value MUST be one of {"red", "green", "blue"}.
#                     Otherwise raise ValueError.
#   3. __get__:       return the stored value. If access is on the CLASS
#                     (instance is None), return the descriptor itself.
#
# Stores the real value under a private attribute (leading underscore)
# so that reading 'shape' does not loop back into __get__ forever.
#
# Then build a 'Shape' class that uses 'Color' for a 'shade' attribute and
# wraps it in a plain constructor so instances are created like:
#       s = Shape("hex", "red")
#
# Hint: __get__ must NOT call getattr recursively — think about WHERE you
# store the value (instance.__dict__ under a mangled/private name).

# --- (write your code below this line) ---


# ======================================================================
# PART 3 — Test (do not modify)
# ======================================================================

class 


if __name__ == "__main__":
    s = Shape("hexagon", "red")
    print("shade is red:", s.shade)

    s.shade = "blue"
    print("shade is blue:", s.shade)

    try:
        s.shade = "magenta"
    except ValueError as e:
        print("rejected bad color:", e)

    # Class-level access should return the descriptor itself
    print("class access returns descriptor:", type(Shape.shade).__name__)