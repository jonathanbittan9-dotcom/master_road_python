# ReadOnly descriptor — demo of "fail loud instead of fail silent".
# Run: python practicing/readonly_demo.py

# ======================================================================
# PART A — WITHOUT the descriptor: the bug is silent
# ======================================================================
class User:
    def __init__(self, name, created_at):
        self.name = name
        self.created_at = created_at

u = User("Ari", 12345)
u.created_at = 999      # a bug: some code clobbered it
print("silent version  ->", u.created_at, "  <- wrong, but nobody knows")

# ======================================================================
# PART B — WITH the descriptor: same bug now crashes loudly
# ======================================================================
class ReadOnly:
    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value):
        if self.private_name in instance.__dict__:
            raise AttributeError(
                f"{self.private_name[1:]} is frozen (set once at creation)"
            )
        setattr(instance, self.private_name, value)

class User:
    created_at = ReadOnly()
=
    def __init__(self, name, created_at):
        self.name = name
        self.created_at = created_at

u = User("Ari", 12345)
print("frozen version  ->", u.created_at)
try:
    u.created_at = 999      # the exact same bug
except AttributeError as e:
    print("frozen version  -> AttributeError:", e, " <- crash here, fix it today")