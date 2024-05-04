from sqlalchemy.orm import DeclarativeBase

from app.extensions import db


class Base(DeclarativeBase):
    metadata = db.metadata
