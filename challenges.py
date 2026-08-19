from abc import ABC

class messages(ABC):
    def notifications():
        ...
    
    def reports():
        ...

class slack(messages):
    def __init__(self, name , quota: int = 100) -> None:
        self.quota = quota
        self.name = name
    def notifications():
        return f""