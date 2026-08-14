from abc import ABC, abstractmethod
from flask import Flask , render_template
from config import app_config
from logs_setup import log
from typing import Protocol
from jinja2 import TemplateNotFound , TemplateSyntaxError
app = Flask(__name__)

format=("[%(levelname)s] %(message)s")


class paymentmastercard():
        def __init__(self, amount: float) ->  float:
            self.amount = amount
        def __repr__(self) -> str:
            return f"payment: {self.amount} dollars charged..."

amount_charged = paymentmastercard(80)
    # class paymentmastercardfail(paymentmastercard):
@app.route("/pay")
def payment_process():
    try:
        log.info("trying to return the payment of the user...")
        respone = render_template("practice.html" , amount=amount_charged)
        log.info("returned the the payment of the user🤑")
        return respone
    except Exception:
         log.exception("failed to return the payment of the user❌")
         return render_template("errorpage.html")
# class login_system:

class messages(Protocol):
     def send(self, message_kind):
          ...

class Whatsapp(messages):
     def send(self, message_kind):
          return f"whatsapp: {message_kind}"

class discord(messages):
     def send(self, message_kind):
          return f"discord: {message_kind}"

messages_popping_whatsapp = Whatsapp().send("You got 25 messages from whatsapp")
messages_popping_discord = discord().send("You got 36 messages from discord")

@app.route("/messages")
def messages_return():
    class ReturningMessages(Whatsapp , discord , messages):
            super().__init__(messages, Whatsapp, discord)
            def __init__ (self, messages_count) -> str:
                  self.messages_count = messages_count
            def __repr__(messages_count) -> str:
                  return f"{Whatsapp} has {messages_count} notifications"
            def __repr__(messages_count) -> str:
                 return f"{discord} has {messages_count} notifications "
    try:
        response = render_template("practice.html" , messages=ReturningMessages)
        log.info("returned the messages of whatsapp💬")
        return response
    except  TypeError:
        log.exception("TypeError‼️")
        return render_template("errorpage.html")
    except TemplateNotFound:
        log.exception("Tempalte errorpage.html cannot be found❌")
        return render_template("errorpage.html")


class animal:
    def __init__(self, name: str):
          self.name = name
          self.isalive = True
    def move(self) -> str:
        return f"{self.name} is now moving"
    def eat(self) -> str:
         return f"{self.name} is now eating"
    def swim(self) -> str:
         return f"{self.name} is now swimming"

class fish(animal):
    def __init__(self , name: str , breed: str):
            super().__init__(name)
            self.breed = breed
class dog(animal):
     def __init__(self , name: str , breed: str):
          super().__init__(name)
          self.breed = breed



@app.route("/animals")
def animals_view() -> str:
    try:
        d = dog("lasca", "husky")
        f = fish("nemo", "clownfish")
        respsone =  render_template("practice.html",  dog=d.move()  , fish = f.swim())
        log.info("returned the data of the animals😺")
        return respsone
    except TypeError:
         log.exception("TypeError‼️")
         return render_template("errorpage.html")
    except TemplateSyntaxError:
        log.exception( "Failed to syntax with the tempalte❌")
        return render_template("error.html")
    

class A:
    def who(self) -> str:
        return "A"


class B(A):
    def who(self) -> str:
        return "B -> " + super().who()


class C(A):
    def who(self) -> str:
        return "C -> " + super().who()


class D(B, C):
    def who(self) -> str:
        return "D -> " + super().who()

log.info( [cls.__name__ for cls in D.__mro__])

class list_handling(ABC):
    @abstractmethod
    def pants(self) -> str:
        ...

    def shirts(self) -> str:
        ...

class laundry(list_handling):
    def __init__(self, shirts_to_do: int , pants_to_do: int) -> int:
          self.shirts_to_do = shirts_to_do
          self.pants_to_do = pants_to_do
    def shirts(self) -> str:
        response = f"there are {self.shirts_to_do} shirts to get to luandry"
        log.info("returned the amount of shirts that need to get to the luandry👕")
        return response
    def pants(self) -> str:    
        reponse =  f"there are {self.pants_to_do} pants to get to luandry"
        log.info("returned the amount of pants that need to get to the luandry👖")
        return reponse
    

laundry_do = laundry(5 , 7)
    

@app.route("/chores")
def chores():
    try:
        response = render_template("practice.html" , laundry=laundry_do)
        log.info("returned the chores data👊")
        return response
    except TypeError:
        log.exception("TypeError , laundry_do is isn't defendied one of the fucntions of list_handeling❌")
        

         
if __name__ == "__main__":
    log.info("the system ran ✔️")
    app.run(debug=True)