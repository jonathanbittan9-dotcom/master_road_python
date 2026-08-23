from abc import ABC
from typing import Protocol
import functools
from dataclasses import dataclass


class user():
    def __get_name__(self, name , instance):
        self.private_name = "_" + name


class user_setup():
    Email = user()
    discord = user()


print(user_setup)