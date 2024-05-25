import decimal
import enum

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.types import datetime_tz, intpk


class LedgerAccount(Base):
    __tablename__ = "ledger_account"

    class AccountClass(enum.Enum):
        BALANCE_SHEET = 1
        INCOME_STATEMENT = 2

        def __str__(self) -> str:
            return {
                self.BALANCE_SHEET: "Balance Sheet",
                self.INCOME_STATEMENT: "Income Statement",
            }[self]

    class AccountType(enum.Enum):
        ASSET = 1
        LIABILITY = 2
        EQUITY = 3
        REVENUE = 4
        EXPENSE = 5

        def __str__(self) -> str:
            return {
                self.ASSET: "Asset",
                self.LIABILITY: "Liability",
                self.EQUITY: "Equity",
                self.REVENUE: "Revenue",
                self.EXPENSE: "Expense",
            }[self]

    class AccountBalanceType(enum.Enum):
        DEBIT_BALANCE = 1
        CREDIT_BALANCE = 2

        def __str__(self) -> str:
            return {
                self.DEBIT_BALANCE: "Debit Balance",
                self.CREDIT_BALANCE: "Credit Balance",
            }[self]

    # Columns
    account_id: Mapped[intpk]
    account_name: Mapped[str] = mapped_column(unique=True)
    account_label: Mapped[str]
    account_class: Mapped[AccountClass]
    account_type: Mapped[AccountType]

    # Relationships
    items: Mapped[list["LedgerEntryItem"]] = relationship(back_populates="account")

    @property
    def account_balance_type(self) -> AccountBalanceType:
        if self.account_type in [self.AccountType.ASSET, self.AccountType.EXPENSE]:
            return self.AccountBalanceType.DEBIT_BALANCE
        return self.AccountBalanceType.CREDIT_BALANCE

    @property
    def account_balance(self) -> decimal.Decimal:
        total_debit = sum(
            [
                item.amount
                for item in self.items
                if item.type == LedgerEntryItem.Type.DEBIT
            ],
            start=decimal.Decimal("0"),
        )
        total_credit = sum(
            [
                item.amount
                for item in self.items
                if item.type == LedgerEntryItem.Type.CREDIT
            ],
            start=decimal.Decimal("0"),
        )

        if self.account_balance_type == LedgerAccount.AccountBalanceType.DEBIT_BALANCE:
            return total_debit - total_credit
        return total_credit - total_debit


class LedgerEntry(Base):
    __tablename__ = "ledger_entry"

    # Columns
    id: Mapped[intpk]
    date: Mapped[datetime_tz]

    # Relationships
    items: Mapped[list["LedgerEntryItem"]] = relationship(back_populates="entry")


class LedgerEntryItem(Base):
    __tablename__ = "ledger_entry_item"
    __table_args__ = (
        ForeignKeyConstraint(["account_id"], [LedgerAccount.account_id]),
        ForeignKeyConstraint(["entry_id"], [LedgerEntry.id]),
    )

    class Type(enum.Enum):
        DEBIT = "D"
        CREDIT = "C"

    # Columns
    id: Mapped[intpk]
    date: Mapped[datetime_tz]
    account_id: Mapped[int]
    type: Mapped[Type]
    amount: Mapped[decimal.Decimal]
    entry_id: Mapped[int]

    # Relationshipts
    account: Mapped[LedgerAccount] = relationship(back_populates="items")
    entry: Mapped[LedgerEntry] = relationship(back_populates="items")

    @property
    def is_debit(self) -> bool:
        return self.type == self.Type.DEBIT

    @property
    def is_credit(self) -> bool:
        return self.type == self.Type.CREDIT
