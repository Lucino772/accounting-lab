from flask import Flask
import jinja_partials
from app.extensions import htmx


def create_app():
    app = Flask(__name__)
    jinja_partials.register_extensions(app)
    htmx.init_app(app)
    return app
