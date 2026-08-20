from flask import Flask, render_template
from jinja2 import TemplateSyntaxError , TemplateNotFound
from domain.logs_setup import log
from domain.menu import main

app = Flask(__name__)


@app.route("/menu")
def menu():
    try:
        reponse = render_template("index.html" , menu = main)
        log.info("😋returned the menu of the cafe to the user")
        return reponse
    except TemplateNotFound:
        log.exception("❌ template not found-check you're folder name")
    except TemplateSyntaxError:
        log.exception("❌failed to syntax with the termplate: check index.html file")

@app.route("/order")
def order():
    try:
        response = render_template("index.html" , )

if __name__ == "__main__":
    app.run()