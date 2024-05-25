import secrets

import jinja_partials
from flask import Flask

from app.controllers.accounts import blueprint as accounts_blueprint
from app.controllers.ledger import blueprint as ledger_blueprint
from app.controllers.statement import blueprint as statement_blueprint
from app.extensions import db, htmx, migrate


def create_app():
    app = Flask(__name__)
    jinja_partials.register_extensions(app)

    # Config
    app.secret_key = secrets.token_hex()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"

    # Init Extensions
    htmx.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    app.register_blueprint(ledger_blueprint, url_prefix="/ledger")
    app.register_blueprint(accounts_blueprint, url_prefix="/accounts")
    app.register_blueprint(statement_blueprint, url_prefix="/statement")

    return app
