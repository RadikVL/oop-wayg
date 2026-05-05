"""
Функции-стратегии для коллекции счетов.

Тут лежит всё, что мы передаём в коллекцию как функции-аргументы:

  - функции-ключи для сортировки (`by_balance`, `by_holder`, ...)
  - функции-фильтры (`is_active`, `is_credit`, ...)
  - фабрики функций (`make_richer_than(threshold)` — возвращают новую функцию)
  - стратегии-преобразователи (`to_summary`, `apply_discount(...)`)
  - callable-классы (DiscountStrategy) — то же самое, что функция,
    но с состоянием

Зачем такое разделение: коллекция (collection.py) ничего не знает про
конкретные правила. Хочешь отсортировать по балансу — кидаешь сюда
функцию by_balance. Хочешь по имени — by_holder. Поменялась логика —
поправили только тут, коллекция не дёрнулась.
"""

from model import BankAccount, CreditAccount, DepositAccount


# ============================================================
# Функции-ключи для сортировки (key=...)
# ============================================================

def by_balance(account):
    """Сортировка по балансу. Просто отдаём число — чтоб sort() было что сравнивать."""
    return account.balance


def by_holder(account):
    """Сортировка по ФИО владельца."""
    return account.holder_name


def by_rate(account):
    """Сортировка по процентной ставке."""
    return account.interest_rate


def by_kind_then_balance(account):
    """Сортировка по виду счёта, а внутри вида — по балансу.

    Возвращаем кортеж — Python сравнит сначала первый элемент,
    а если равны, то второй. Бесплатная многоуровневая сортировка.
    """
    return (account.kind, account.balance)


# ============================================================
# Функции-фильтры (предикаты — возвращают bool)
# ============================================================

def is_active(account):
    """Активный счёт."""
    return account.is_active


def is_blocked(account):
    """Заблокированный."""
    return not account.is_active


def is_credit(account):
    """Кредитный счёт (фильтр по типу через isinstance)."""
    return isinstance(account, CreditAccount)


def is_deposit(account):
    return isinstance(account, DepositAccount)


# ============================================================
# Фабрики функций — функции, которые возвращают функцию.
# Удобно когда фильтр зависит от параметра, а параметр хочется задать
# снаружи (например, порог суммы)
# ============================================================

def make_richer_than(threshold):
    """Сделать фильтр: «баланс больше threshold».

    Внутри живёт замыкание (closure) — внутренняя функция помнит
    threshold даже после того, как make_richer_than() вернулся. Магия.
    """
    def predicate(account):
        return account.balance > threshold
    return predicate


def make_holder_filter(name):
    """Фильтр по конкретному владельцу."""
    def predicate(account):
        return account.holder_name == name
    return predicate


def make_rate_in_range(min_rate, max_rate):
    """Фильтр: ставка в диапазоне [min_rate, max_rate]."""
    def predicate(account):
        return min_rate <= account.interest_rate <= max_rate
    return predicate


# ============================================================
# Стратегии-преобразователи (для map())
# ============================================================

def to_summary(account):
    """Превратить счёт в короткую строку — типа «Иванов: 1500.00 руб.»."""
    return f"{account.holder_name}: {account.balance:.2f} руб."


def to_balance(account):
    """Вытащить из счёта только баланс — для сводных подсчётов."""
    return account.balance


def to_holder(account):
    return account.holder_name


# ============================================================
# Callable-объекты (классы со __call__) — стратегии с состоянием
# ============================================================

class DiscountStrategy:
    """Стратегия скидки: уменьшает баланс на заданный процент.

    Зачем класс, а не функция: класс может хранить состояние (тут — процент),
    его можно настраивать в рантайме, у него может быть метод __repr__,
    его можно тыкать isinstance-ом. По вызову — ведёт себя как обычная
    функция благодаря __call__.

    Пример:
        cut = DiscountStrategy(0.1)   # минус 10%
        cut(account)                  # тыкнули — счёт похудел
    """

    def __init__(self, percent):
        if not (0 <= percent <= 1):
            raise ValueError("percent должен быть в диапазоне [0; 1]")
        self.percent = percent

    def __call__(self, account):
        # урезаем баланс. Не пользуемся deposit/withdraw — нам сейчас
        # надо именно вкорячить значение, минуя проверки на активность
        new_balance = account.balance * (1 - self.percent)
        account._balance = new_balance
        return account

    def __repr__(self):
        return f"DiscountStrategy(percent={self.percent})"


class InterestStrategy:
    """Альтернативная стратегия начисления процентов с возможным бонусом.

    Дёргается как функция — за счёт __call__.
    """

    def __init__(self, bonus_percent=0.0):
        self.bonus_percent = bonus_percent

    def __call__(self, account):
        rate = account.interest_rate + self.bonus_percent
        account._balance += account.balance * (rate / 100.0)
        return account
