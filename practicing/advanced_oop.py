from abc import ABC
from typing import Protocol
import functools
from dataclasses import dataclass

class user():
    def __get_name__(self, name , instance) -> None:
        self.private_name = "_" + name

    def __get__(self , instance , name) -> str:
        if instance is None:
            return getattr()

    def __set__()
class user_setup():
    Email = user()
    discord = user()


print(user_setup)