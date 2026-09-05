from abc import ABC
from typing import Protocol
import functools
from dataclasses import dataclass

class user():
    def __set_name__(self, owner, name) -> None:
        # Called once per descriptor when it's defined in user_setup.
        # (owner=user_setup, name="Email" or "discord")
        # Stores the private key we'll use to stash data on instances.
        self.private_name = "_" + name

    def __set__(self, instance, value) -> None:
        if not isinstance(value , str):
            raise ValueError(f"value is not a str.❌")
        setattr(instance, self.private_name, value)
    

    def __get__(self, instance, owner) -> str:
        # Called when you READ the attribute.
        #   instance = the object you accessed it on (e.g. u)
        #   owner    = the class it's defined on (e.g. user_setup)
        # If instance is None it means you accessed it on the CLASS
        # (user_setup.Email, not u.Email) — there's no object to read
        # data from, so by convention we return self, the descriptor
        # object sitting in the class's __dict__:
        #   user_setup.Email is user_setup.__dict__["Email"]  # True
        if instance is None:
            return self
        # Otherwise read the stored value off the instance under the
        # private name, e.g. getattr(u, "_Email") -> "a@b.com"
        #
        # getattr(instance, private_name) "GETS" a value FROM the
        # instance by looking up the attribute name:
        #   getattr(u, "_Email")
        #   |      |     |
        #   |      |     └──── the attribute name to look up
        #   |      └────────── the instance to get it FROM
        #   └───────────────── "get"
        # And `return` hands that value back out, so `u.Email`
        # evaluates to whatever was gotten, e.g. "a@b.com".
        return getattr(instance, self.private_name)

    

class user_setup():
    Email = user()
    discord = user()

print(user_setup)

u = user_setup()
u.Email = "a@b.com"
print(u.Email)

# u.discord = 5   # should raise ValueError: value is not a str.❌