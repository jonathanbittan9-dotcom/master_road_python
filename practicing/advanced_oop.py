from abc import ABC
from typing import Protocol
import functools
from dataclasses import dataclass

class user():
    def __set_name__(self, owner, name) -> None:
        self.private_name = "_" + name

    def __get__(self, instance, owner) -> str:
        if instance is None:
            return self
        return getattr(instance, self.private_name)

    def __set__(self, instance, value) -> None:
        if not isinstance(value , str):
            raise ValueError(f"value is not a str.❌")
        setattr(instance, self.private_name, value)

class user_setup():
    Email = user()
    discord = user()


print(user_setup)

u = user_setup()
u.Email = "a@b.com"
print(u.Email)

# u.discord = 5   # should raise ValueError: value is not a str.❌