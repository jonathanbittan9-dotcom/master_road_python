from abc import ABC

class messages(ABC):
    def notifications():
        ...
    
    def reports():
        ...

class slack(messages):
    def __init__(self, quota: int = 100) -> None:
        self.quota = quota
    def notifications():
        return  