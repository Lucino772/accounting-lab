import decimal
from collections.abc import Iterable


class StatementEntry:
    def __init__(self, name: str, balance: decimal.Decimal | None = None) -> None:
        self.__name = name
        self.__balance = balance
        self.__entries: list["StatementEntry"] = []

    @property
    def name(self) -> str:
        return self.__name

    @property
    def entries(self) -> Iterable["StatementEntry"]:
        return self.__entries

    @property
    def balance(self) -> decimal.Decimal:
        if len(self.__entries) > 0:
            return sum(
                [entry.balance for entry in self.__entries],
                start=decimal.Decimal("0"),
            )

        if self.__balance is None:
            return decimal.Decimal("0")

        return self.__balance

    def add_entry(
        self, name: str, balance: decimal.Decimal | None = None
    ) -> "StatementEntry":
        entry = StatementEntry(name, balance)
        self.__entries.append(entry)
        return entry

    def update_balance(self, balance: decimal.Decimal):
        if self.__balance is None:
            self.__balance = balance
        else:
            self.__balance += balance
