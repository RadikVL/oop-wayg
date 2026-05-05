"""
AccountBook — наша "тетрадка" со счетами, контейнер для BankAccount.

Что умеет:
  - добавлять/удалять счета (с проверкой типа и без дубликатов по номеру)
  - искать по номеру или по владельцу
  - её можно мерять через len(), бегать for'ом, обращаться по индексу
  - сортировать и фильтровать (фильтр возвращает новый AccountBook)

Тип проверяем строго: всё, что не BankAccount — на хер из коллекции.
"""

from model import BankAccount


class AccountBook:

    def __init__(self):
        # внутри — обычный список. Не плодим никаких супер-структур,
        # для учебной задачи и так норм
        self._items = []

    # ---------- добавление / удаление ----------

    def add(self, account):
        """Добавить счёт. Проверяем тип и дубликат по номеру."""
        if not isinstance(account, BankAccount):
            raise TypeError("В AccountBook можно класть только BankAccount")
        # дубликаты по номеру счёта не пускаем — иначе и __eq__ потеряет смысл,
        # и в реале два счёта с одним номером это нонсенс
        if self.find_by_number(account.account_number) is not None:
            raise ValueError(
                f"Счёт с номером {account.account_number} уже есть в коллекции"
            )
        self._items.append(account)

    def remove(self, account):
        """Удалить счёт. Если его нет — кидаем ValueError, не молчим."""
        if account not in self._items:
            raise ValueError("Такого счёта в коллекции нет")
        self._items.remove(account)

    def remove_at(self, index):
        """Удалить счёт по индексу — отдельный метод, чтоб не путать с remove()."""
        # пусть Python сам кинет IndexError, если индекс кривой —
        # его сообщение не хуже нашего
        del self._items[index]

    # ---------- доступ ----------

    def get_all(self):
        """Вернуть копию списка — чтоб снаружи никто наш _items не покорёжил."""
        return list(self._items)

    def find_by_number(self, account_number):
        """Найти счёт по номеру. Нет такого — None."""
        for acc in self._items:
            if acc.account_number == account_number:
                return acc
        return None

    def find_by_holder(self, holder_name):
        """Найти все счета конкретного владельца (по точному совпадению ФИО)."""
        # тут возвращаем список, а не один счёт — у одного человека
        # вполне может быть несколько счетов
        return [acc for acc in self._items if acc.holder_name == holder_name]

    # ---------- магические методы ----------

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        # отдаём итератор списка — Python сам нам всё сделает
        return iter(self._items)

    def __getitem__(self, index):
        # благодаря этому работает и accounts[0], и accounts[1:3] (срезы)
        return self._items[index]

    def __contains__(self, account):
        # тоже бесплатно: 'account in book' будет дёргать __eq__
        return account in self._items

    def __str__(self):
        if not self._items:
            return "AccountBook: пусто"
        lines = [f"AccountBook ({len(self._items)} счёт(ов)):"]
        for i, acc in enumerate(self._items):
            lines.append(f"  [{i}] {acc}")
        return "\n".join(lines)

    def __repr__(self):
        return f"AccountBook(items={self._items!r})"

    # ---------- сортировка ----------

    def sort_by_balance(self, reverse=False):
        """Отсортировать счета по балансу (in-place). reverse=True — по убыванию."""
        self._items.sort(key=lambda a: a.balance, reverse=reverse)

    def sort_by_holder(self):
        """По алфавиту владельцев."""
        self._items.sort(key=lambda a: a.holder_name)

    def sort_by_rate(self, reverse=False):
        """По ставке."""
        self._items.sort(key=lambda a: a.interest_rate, reverse=reverse)

    # ---------- фильтры (возвращают новую AccountBook) ----------

    def get_active(self):
        """Только активные счета."""
        return self._build_subset(lambda a: a.is_active)

    def get_blocked(self):
        """Только заблокированные."""
        return self._build_subset(lambda a: not a.is_active)

    def get_richer_than(self, threshold):
        """Счета с балансом > threshold."""
        return self._build_subset(lambda a: a.balance > threshold)

    def _build_subset(self, predicate):
        # помощник: создаём новую коллекцию и кидаем туда то, что прошло фильтр.
        # add() не дёргаем — там проверка на дубликаты, а тут всё уже валидно
        new_book = AccountBook()
        new_book._items = [a for a in self._items if predicate(a)]
        return new_book
