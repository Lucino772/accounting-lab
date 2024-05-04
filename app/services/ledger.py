import datetime as dt
import decimal

from app.models.ledger import LedgerEntry, LedgerEntryItem


class LedgerEntryBuilder:
    def __init__(self, date: dt.datetime) -> None:
        self.__date = date
        self.__items: list[LedgerEntryItem] = []

    def add_debit(self, account: str, amount: decimal.Decimal) -> None:
        self.__items.append(
            LedgerEntryItem(
                date=self.__date,
                account=account,
                type=LedgerEntryItem.Type.DEBIT,
                amount=amount,
            )
        )

    def add_credit(self, account: str, amount: decimal.Decimal) -> None:
        self.__items.append(
            LedgerEntryItem(
                date=self.__date,
                account=account,
                type=LedgerEntryItem.Type.CREDIT,
                amount=amount,
            )
        )

    def build(self) -> LedgerEntry:
        # TODO: Ensure balance
        entry = LedgerEntry(date=self.__date)
        for item in self.__items:
            item.entry = entry
        entry.items = self.__items
        return entry
