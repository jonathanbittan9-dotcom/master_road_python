from abc import ABC, abstractmethod
from flask import Flask , render_template
from config import app_config
from logs_setup import log
from typing import Protocol
from dataclasses import dataclass
from jinja2 import TemplateNotFound , TemplateSyntaxError
app = Flask(__name__)

format=("[%(levelname)s] %(message)s")


######################### domain layer #########################




class paymentmastercard():
        def __init__(self, amount: float) ->  float:
            self.amount = amount
        def __repr__(self) -> str:
            return f"payment: {self.amount} dollars charged..."

class Messages_Interface(Protocol):
     def send(self, messages_count) -> str:
          ...

class Whatsapp(Messages_Interface):
     def send(self, messages_count) -> str:
        message = f"whatsapp: {messages_count}"
        return message
class Discord(Messages_Interface):
     def send(self, messages_count) -> str:
        message = f"discord: {messages_count}"
        return message

class Messages_Center:
            def __init__ (self, channels: list[Messages_Interface]) -> None:
                  self.channels = channels
            def notfiy_all(self, message: str) -> list[str]:
                 return [channel.send(message) for channel in self.channels]

class animal():
    def __init__(self, name: str):
          self.name = name
          self.isalive = True
    def move(self) -> str:
        return f"{self.name} is now moving"
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


@dataclass
class Laundry:
    shirts: int
    pants: int

    def summary(self) -> str:
        try:
            reponse = f"{self.shirts} shirts , {self.pants} pants"
            log.info("returned hte amount of luandry👕👖")
            return reponse
        except ValueError:
             log.exception("repsonse is not an int❌")


     
amount_charged = paymentmastercard(80)
messages_popping_whatsapp = Whatsapp().send("You got 25 messages from whatsapp")
messages_popping_discord = Discord().send("You got 36 messages from discord")
d = dog("lasca", "husky")
f = fish("nemo", "clownfish")
laundry_do = Laundry(5 , 7)


############################# web layer #########################################

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



@app.route("/messages")
def messages_return():
    
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





@app.route("/animals")
def animals_view() -> str:
    try:
        respsone =  render_template("practice.html",  dog=d.move()  , fish = f.swim())
        log.info("returned the data of the animals😺")
        return respsone
    except TypeError:
         log.exception("TypeError‼️")
         return render_template("errorpage.html")
    except TemplateSyntaxError:
        log.exception( "Failed to syntax with the tempalte❌")
        return render_template("error.html")
    
    

@app.route("/chores")
def chores():
    try:
        response = render_template("practice.html" , laundry=laundry_do)
        log.info("returned the chores data👊")
        return response
    except TypeError:
        log.exception("TypeError , laundry_do is isn't defendied one of the fucntions of list_handeling❌")
        return render_template("errorpage.html")

         
if __name__ == "__main__":
    log.info("the system ran ✔️")
    app.run(debug=True)



# git add .
# git commit -m "message"
# git push