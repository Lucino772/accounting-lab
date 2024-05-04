import decimal
import enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import datetime_tz, intpk


class LedgerEntry(Base):
    __tablename__ = "ledger_entry"

    id: Mapped[intpk]  # noqa: A003
    date: Mapped[datetime_tz]
    items: Mapped[list["LedgerEntryItem"]] = relationship(back_populates="entry")


class LedgerEntryItem(Base):
    __tablename__ = "ledger_entry_item"

    class Type(enum.Enum):
        DEBIT = "D"
        CREDIT = "C"

    id: Mapped[intpk]  # noqa: A003
    date: Mapped[datetime_tz]
    account: Mapped[str]
    type: Mapped[Type]  # noqa: A003
    amount: Mapped[decimal.Decimal]

    entry_id: Mapped[int] = mapped_column(ForeignKey(LedgerEntry.id))
    entry: Mapped[LedgerEntry] = relationship(back_populates="items")

    @property
    def is_debit(self) -> bool:
        return self.type == self.Type.DEBIT

    @property
    def is_credit(self) -> bool:
        return self.type == self.Type.CREDIT
