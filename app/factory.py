import jinja_partials
from flask import Flask, render_template

from app.extensions import htmx


def index():
    return render_template("index.html")


def create_app():
    app = Flask(__name__)
    jinja_partials.register_extensions(app)
    htmx.init_app(app)
    app.add_url_rule("/", view_func=index)
    return app
