from flask import Flask, render_template
from jinja2 import TemplateSyntaxError , TemplateNotFound
from scripts.domain. logs_setup import log
from scripts.domain.order import small , medium , large , SIZES
app = Flask(__name__)


@app.route("/menu")
def menu():
    from scripts.domain.menu import main

    try:
        reponse = render_template("index.html" , menu = main)
        log.info("😋returned the menu of the cafe to the user")
        return reponse
    except TemplateNotFound:
        log.exception("❌ template not found-check you're folder name")
    except TemplateSyntaxError:
        log.exception("❌failed to syntax with the termplate: check index.html file")


@app.route("/order/<size>")
def order_progress(size):
    service_class = SIZES.get(size)
    if service_class is None:
        log.exception(f"❌Unknown order size requested: {size}")
        return render_template("ErrorPage.html"), 404

    item = service_class(size=size, money=0)
    try:
        response = render_template("index.html", order=item.text())
        log.info(f"user ordered successfully the size {size} ")
        return response
    except TemplateSyntaxError:
        log.exception("❌TemplateSyntaxError: failed to return the order summary")
        return render_template("ErrorPage.html")
    except TypeError:
        log.exception("❌TypeError: failed to return the order summary")
        return render_template("ErrorPage.html")
if __name__ == "__main__":
    app.run()