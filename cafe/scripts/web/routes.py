from flask import Flask, render_template
from jinja2 import TemplateSyntaxError , TemplateNotFound
from scripts.domain. logs_setup import log


app = Flask(__name__)


@app.route("/menu")
def menu():
    from domain.menu import main

    try:
        reponse = render_template("index.html" , menu = main)
        log.info("😋returned the menu of the cafe to the user")
        return reponse
    except TemplateNotFound:
        log.exception("❌ template not found-check you're folder name")
    except TemplateSyntaxError:
        log.exception("❌failed to syntax with the termplate: check index.html file")

@app.route("/order/size")
def order():
    from domain.order import main
    return render_template("index.html" , order = main)
        

if __name__ == "__main__":
    app.run()