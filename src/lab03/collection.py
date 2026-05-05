"""
AccountBook — та же тетрадка из ЛР-2, но с парой методов под полиморфизм:
get_only_credit() и get_only_deposit().

Главная мысль: тип хранимого объекта — BankAccount, и любые наследники
сюда же укладываются (isinstance() их пропустит). Никаких изменений
в add() не нужно.
"""

from base import BankAccount
from models import CreditAccount, DepositAccount


class AccountBook:

    def __init__(self):
        self._items = []

    def add(self, account):
        if not isinstance(account, BankAccount):
            raise TypeError("В AccountBook можно класть только BankAccount и его наследников")
        # дубликат — по номеру счёта (как и в ЛР-2)
        for a in self._items:
            if a.account_number == account.account_number:
                raise ValueError(f"Счёт с номером {account.account_number} уже есть")
        self._items.append(account)

    def remove(self, account):
        if account not in self._items:
            raise ValueError("Такого счёта в коллекции нет")
        self._items.remove(account)

    def remove_at(self, index):
        del self._items[index]

    def get_all(self):
        return list(self._items)

    def find_by_number(self, account_number):
        for acc in self._items:
            if acc.account_number == account_number:
                return acc
        return None

    def find_by_holder(self, holder_name):
        return [a for a in self._items if a.holder_name == holder_name]

    def __len__(self): return len(self._items)
    def __iter__(self): return iter(self._items)
    def __getitem__(self, i): return self._items[i]
    def __contains__(self, a): return a in self._items

    def __str__(self):
        if not self._items:
            return "AccountBook: пусто"
        lines = [f"AccountBook ({len(self._items)} счёт(ов)):"]
        for i, a in enumerate(self._items):
            lines.append(f"  [{i}] {a}")
        return "\n".join(lines)

    def __repr__(self): return f"AccountBook(items={self._items!r})"

    # сортировки
    def sort_by_balance(self, reverse=False):
        self._items.sort(key=lambda a: a.balance, reverse=reverse)

    def sort_by_holder(self):
        self._items.sort(key=lambda a: a.holder_name)

    # фильтры
    def get_active(self):
        return self._build_subset(lambda a: a.is_active)

    def get_richer_than(self, threshold):
        return self._build_subset(lambda a: a.balance > threshold)

    def get_only_credit(self):
        """Только кредитные счета — фильтрация по типу через isinstance."""
        return self._build_subset(lambda a: isinstance(a, CreditAccount))

    def get_only_deposit(self):
        """Только депозитные."""
        return self._build_subset(lambda a: isinstance(a, DepositAccount))

    def _build_subset(self, predicate):
        new_book = AccountBook()
        new_book._items = [a for a in self._items if predicate(a)]
        return new_book
