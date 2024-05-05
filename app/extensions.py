from flask_htmx import HTMX
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

htmx = HTMX()
db = SQLAlchemy(
    metadata=MetaData(
        naming_convention={
            "pk": "pk__%(table_name)s",
            "fk": "fk__%(table_name)s__%(column_0_name)s__%(referred_table_name)s",
            "ix": "ix__%(table_name)s__%(column_0_name)s",
            "uq": "uq__%(table_name)s__%(column_0_name)s",
            "ck": "ck__%(table_name)s__%(constraint_name)s",
        }
    )
)
migrate = Migrate()
