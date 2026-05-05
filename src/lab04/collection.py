"""
AccountBook + интеграция с интерфейсами.

Главное отличие от ЛР-2:
  - можем фильтровать по интерфейсу (get_printable, get_comparable)
  - сортировка по compare_to (без ключа — потому что объекты сами знают,
    как себя сравнивать)
  - метод print_all() печатает всё через Printable.to_string()

Никаких if isinstance(x, CreditAccount) — работаем через контракты.
"""

from interfaces import Printable, Comparable
from models import BankAccount


class AccountBook:

    def __init__(self):
        self._items = []

    def add(self, account):
        if not isinstance(account, BankAccount):
            raise TypeError("Можно класть только BankAccount и его наследников")
        for a in self._items:
            if a.account_number == account.account_number:
                raise ValueError(f"Счёт №{account.account_number} уже есть")
        self._items.append(account)

    def remove(self, account):
        if account not in self._items:
            raise ValueError("Такого счёта в коллекции нет")
        self._items.remove(account)

    def get_all(self): return list(self._items)

    def __len__(self): return len(self._items)
    def __iter__(self): return iter(self._items)
    def __getitem__(self, i): return self._items[i]
    def __contains__(self, a): return a in self._items

    def __str__(self):
        if not self._items:
            return "AccountBook: пусто"
        return f"AccountBook ({len(self._items)} счёт(ов))"

    def __repr__(self): return f"AccountBook(items={self._items!r})"

    # ---------- работа через интерфейсы ----------

    def get_printable(self):
        """Все, кто умеет to_string() — то есть реализует Printable."""
        return [a for a in self._items if isinstance(a, Printable)]

    def get_comparable(self):
        """Все, кто умеет compare_to() — то есть реализует Comparable."""
        return [a for a in self._items if isinstance(a, Comparable)]

    def print_all(self):
        """Печатаем всё через единый интерфейс — никаких if по типу."""
        for item in self.get_printable():
            print(item.to_string())
            print()  # пустая строка между отчётами, чтоб глазам не больно

    def sort_via_comparable(self):
        """Отсортировать через compare_to (in-place).

        Реализовали через functools.cmp_to_key — берёт нашу compare_to
        и превращает её в key-функцию для sort. По сути обёртка.
        """
        from functools import cmp_to_key
        comparables = self.get_comparable()
        if len(comparables) != len(self._items):
            raise RuntimeError("В коллекции есть объекты без Comparable — сортировать нечего")
        self._items.sort(key=cmp_to_key(lambda a, b: a.compare_to(b)))


# ---------- универсальные функции, работающие через интерфейс ----------

def print_all(items):
    """Печатает любой список Printable-ов. Работает с чем угодно,
    лишь бы был метод to_string()."""
    for item in items:
        if not isinstance(item, Printable):
            raise TypeError(f"Объект {item!r} не реализует Printable")
        print(item.to_string())
        print()


def find_max(items):
    """Найти максимальный элемент через Comparable.compare_to().

    Тоже работает с чем угодно, что реализует Comparable. Универсальность —
    это и есть смысл интерфейсов.
    """
    if not items:
        return None
    best = items[0]
    for item in items[1:]:
        if not isinstance(item, Comparable):
            raise TypeError(f"Объект {item!r} не реализует Comparable")
        if item.compare_to(best) > 0:
            best = item
    return best
