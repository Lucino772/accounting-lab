from flask_htmx import HTMX
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

htmx = HTMX()
db = SQLAlchemy()
migrate = Migrate()
