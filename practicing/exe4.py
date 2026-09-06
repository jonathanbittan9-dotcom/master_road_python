# Exercise: Descriptors (v4) — level up
#
# You did Color (validate + store). Now two harder patterns, build cold.

# ======================================================================
# PART 1 — Read-only descriptor
# ======================================================================
# Sometimes an attribute may be SET only during instantiation, then frozen.
# Classic approach: __get__ returns the stored value; __set__ raises
# AttributeError after the first write.
#
# TASK: write a descriptor 'ReadOnly' such that:
#       class User:
#           created_at = ReadOnly()
#           def __init__(self, name, created_at):
#               self.name = name
#               self.created_at = created_at   # 1st write allowed
#
#       u = User("Ari", 12345)
#       print(u.created_at)          # 12345
#       u.created_at = 999           # AttributeError — frozen
#
# HINT: __set_name__ stores which attribute to protect.
#       Track "already set" on the INSTANCE (not the descriptor!) —
#       otherwise two instances would share one flag. Where does per-instance
#       state live? (instance.__dict__ under a private name).

# --- (write ReadOnly below) ---


# ======================================================================
# PART 2 — Parameterized descriptor
# ======================================================================
# Color is hardcoded to 3 colors. A descriptor configured per-attachment
# is much more useful: `temperature = Range(-40, 50)`.
#
# TASK: write a descriptor 'Range' constructed as Range(low, high) that:
#       - validates value is a number inside [low, high]
#       - reuses the SAME class for different bounds on different attributes
#
#       class Thermostat:
#           temperature = Range(10, 30)
#           humidity    = Range(0, 100)
#
#       t = Thermostat(22, 45)       # ok both
#       t.temperature = 5            # ValueError
#       t.humidity = 120             # ValueError
#
#   THINK before coding: a descriptor instance is created ONCE per class
#   attribute, and __init__ runs at class-definition time. Where do you
#   store low/high? Where do you store the VALUE? These are different
#   levels: descriptor-level vs instance-level.

# --- (write Range below) ---


class range:
    def __set_name__(self , private_name):
        self.private_name = "_" + private_name
    def __set__(self , instance , value):
        if self.private_name in instance.__dict__:
            raise AttributeError(f"{self.private_name} FROZE -> ATTRIBUTE ERROR! , CANNOT CHANGE THE VALUE!")
    
        setattr(instance , self.private_name , value)
    def __get__(self , instance , owner):
        if instance is None:
            return self

if __name__ == "__main__" and False:  # toggle to False when ready
    pass

if __name__ == "__main__":
    # --- ReadOnly ---
    u = User("Ari", 12345)
    print("created_at is set:", u.created_at)
    try:
        u.created_at = 999
        print("frozen failed — write allowed (BAD)")
    except AttributeError:
        print("frozen correctly (GOOD)")

    u2 = User("Bo", 54321)
    print("second instance independent:", u2.created_at == 54321 and u.created_at == 12345)

    # --- Range ---
    t = Thermostat(22, 45)
    print("initial temp/humidity:", t.temperature, t.humidity)
    t.temperature = 28
    print("updated temp:", t.temperature)
    for bad in (5, 31, "warm", None):
        try:
            setattr(t, "temperature", bad)
            print(f"accepted {bad!r} (BAD)")
        except ValueError:
            print(f"rejected {bad!r} (GOOD)")