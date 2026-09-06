# Exercise: __slots__ (v3) — build it yourself
#
# Goal: use __slots__ to understand what it buys you and what it costs.
# Do NOT copy from 19_advanced_oop.py. Build cold, then compare.

# ======================================================================
# PART 1 — The concept (read, don't skip)
# ======================================================================
# Every normal instance gets its own __dict__ — the dict where attribute
# values live. That's ~64+ bytes per instance even when empty.
#
# __slots__ = (name, ...) declares: "instances of THIS class may only ever
# have these attributes." Consequences:
#   (a) no per-instance __dict__  -> less memory per instance
#   (b) typo'd attribute assignment raises AttributeError immediately,
#       instead of silently creating a brand-new attribute
#   (c) the class still works with descriptors, because descriptors live
#       on the CLASS, not the instance
#
# "May only ever have these attributes" — read that twice. Assignment to
# anything NOT in __slots__ is an error, not a silent creation.

# ======================================================================
# PART 2 — Your task
# ======================================================================
#
# 1. Write a class 'PlayerSlots' with:
#       __slots__ = ("name", "level")
#       __init__(self, name, level)  setting both
#
# 2. Write a class 'PlayerDict' that does the SAME but WITHOUT __slots__
#      (plain __dict__ behavior).
#
# 3. Below the test, answer (as comments) which of these "typo traps"
#    each class allows:
#       p = ...
#       p.nmae = "oops"     # misspelled
#       p.xp = 100          # not declared
#
# 4. (stretch, try before reading the hint) — make __slots__ visible:
#      compare PlayerSlots.__slots__ vs PlayerDict.__dict__ presence
#      difference on instances: print these two expressions and note
#      what's different:
#        hasattr(p_dict_instance, "__dict__")
#        hasattr(p_slots_instance, "__dict__")

# --- (write your code below this line) ---


# ======================================================================
# PART 3 — Test (do not modify)
# ======================================================================
if __name__ == "__main__":
    s = PlayerSlots("Ari", 5)
    d = PlayerDict("Ari", 5)
    print("slots level:", s.level)
    print("dict  level:", d.level)

    # same class, same attributes — but different memory behavior:
    print("slots has __dict__:", hasattr(s, "__dict__"))
    print("dict  has __dict__:", hasattr(d, "__dict__"))

    # the whole point: typos should NOT silently create attributes
    try:
        s.nmae = "oops"
        print("slots typo silently allowed (BAD)")
    except AttributeError:
        print("slots typo raised (GOOD)")

    d.nmae = "oops"   # this one is allowed — why that's dangerous:
    print("dict typo created a ghost attribute (BAD):", d.nmae)