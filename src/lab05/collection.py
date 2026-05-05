"""
AccountBook — коллекция, расширенная функциями-стратегиями.

Главные новички:
  - sort_by(key_func)    — сортирует через переданную функцию-ключ
  - filter_by(predicate) — возвращает НОВЫЙ AccountBook, прошедший фильтр
  - apply(func)          — применяет функцию ко всем элементам

Все три метода возвращают `self` (или новую коллекцию для filter_by) —
это даёт цепочки:

    book.filter_by(is_active).sort_by(by_balance).apply(some_func)

Без всяких if-ов, только функции и объекты.
"""

from model import BankAccount


class AccountBook:

    def __init__(self):
        self._items = []

    # ---------- базовая часть (как в прошлых лабах) ----------

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
        if not self._items: return "AccountBook: пусто"
        lines = [f"AccountBook ({len(self._items)} счёт(ов)):"]
        for i, a in enumerate(self._items):
            lines.append(f"  [{i}] {a}")
        return "\n".join(lines)

    def __repr__(self): return f"AccountBook(items={self._items!r})"

    # ---------- стратегические методы ----------

    def sort_by(self, key_func, reverse=False):
        """Отсортировать через переданную функцию-ключ. In-place, возвращает self.

        Возвращаем self, чтоб можно было собирать цепочки методов.
        """
        self._items.sort(key=key_func, reverse=reverse)
        return self

    def filter_by(self, predicate):
        """Отфильтровать через предикат. Возвращает НОВУЮ коллекцию.

        Не in-place — не хотим терять данные. Если фильтрация испортила
        бы исходник, цепочки операций превратились бы в ад.
        """
        new_book = AccountBook()
        new_book._items = [a for a in self._items if predicate(a)]
        return new_book

    def apply(self, func):
        """Применить функцию к каждому элементу. In-place, возвращает self.

        Если функция возвращает новый объект — кладём его на место старого.
        Если возвращает None или сам аргумент — оставляем как есть.
        """
        new_items = []
        for item in self._items:
            result = func(item)
            new_items.append(result if result is not None else item)
        self._items = new_items
        return self

    def map(self, transform):
        """Превратить коллекцию в список результатов transform(item).

        Заметь — возвращаем list, а не AccountBook: тип элементов
        после преобразования может быть любым (строка, число, словарь),
        а в AccountBook кладутся только BankAccount-ы.
        """
        return [transform(item) for item in self._items]
