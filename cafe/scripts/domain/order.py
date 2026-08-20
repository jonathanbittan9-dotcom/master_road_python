from abc import ABC , abstractmethod 
from domain.menu import Order
from domain.logs_setup import log
class service(ABC):
    def __init__(self, size: str , money: int) -> None:
        self.size = size
        self.money = money
    def __str__(self) -> int:
        class_name = type(self).__name__
        if class_name == "small":
            self.money = 6
        elif class_name == "medium":
            self.money = 9
        elif class_name == "large":
            self.money = 13
        else:
            log.exception("❌TypeError: one or more of the classes name is incorrect")
            self.money = None
    def sizeof(self):
        self.size = type(self).__name__
    @abstractmethod
    def text(self) -> str:
        return f"you paied {self.money} for {self.size} size"


class small(service):
    def __init__(self, size: str , money: int) -> None:
        self.size = size
        self.money = money
    def text(self) -> str:
        return f"you paied {self.money} for {self.size} size"

class medium(service):
    def __init__(self, size: str , money: int) -> None:
        self.size = size
        self.money = money
    def text(self) -> str:
        return f"you paied {self.money} for {self.size} size"

class small(service):
    def __init__(self, size: str , money: int) -> None:
        self.size = size
        self.money = money
    def text(self) -> str:
        return f"you paied {self.money} for {self.size} size"

    