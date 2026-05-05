"""
BankAccount — взяли из ЛР-1, тут он живёт почти один-в-один.

Чтоб ЛР-2 запускалась сама по себе, без хитрого импорта из соседней папки,
просто забрали класс сюда. Всю валидацию для краткости тоже вкорячили
прямо в этот файл (в ЛР-1 она лежит отдельно, как и положено на 5).
"""


def _validate_account_number(value):
    if not isinstance(value, str):
        raise ValueError("Номер счёта должен быть строкой")
    value = value.strip()
    if value == "":
        raise ValueError("Номер счёта не может быть пустым")
    if not value.isdigit():
        raise ValueError("Номер счёта должен состоять только из цифр")
    if len(value) != 20:
        raise ValueError("Номер счёта должен содержать ровно 20 цифр")
    return value


def _validate_holder_name(value):
    if not isinstance(value, str):
        raise ValueError("Имя владельца должно быть строкой")
    value = value.strip()
    if value == "":
        raise ValueError("Имя владельца не может быть пустым")
    for ch in value:
        if not (ch.isalpha() or ch in (" ", "-")):
            raise ValueError(
                "Имя владельца может содержать только буквы, пробелы и дефисы"
            )
    return value.title()


def _validate_money(value, what):
    # bool отдельно, ибо True/False — это формально int, и без этой
    # проверки можно было бы влепить True рублей. Нахер такое
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{what} должен быть числом")
    if value < 0:
        raise ValueError(f"{what} не может быть отрицательным")
    return float(value)


def _validate_rate(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Процентная ставка должна быть числом")
    if value < 0 or value > 100:
        raise ValueError("Процентная ставка должна быть в диапазоне [0; 100]")
    return float(value)


class BankAccount:
    bank_name = "z-bank_ZOV_GOYDA"

    def __init__(self, account_number, holder_name,
                 balance=0.0, interest_rate=0.0):
        self._account_number = _validate_account_number(account_number)
        self._holder_name = _validate_holder_name(holder_name)
        self._balance = _validate_money(balance, "Баланс")
        self._interest_rate = _validate_rate(interest_rate)
        self._is_active = True

    @property
    def account_number(self):
        return self._account_number

    @property
    def holder_name(self):
        return self._holder_name

    @holder_name.setter
    def holder_name(self, new_name):
        self._holder_name = _validate_holder_name(new_name)

    @property
    def balance(self):
        return self._balance

    @property
    def interest_rate(self):
        return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, new_rate):
        self._interest_rate = _validate_rate(new_rate)

    @property
    def is_active(self):
        return self._is_active

    def deposit(self, amount):
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — пополнение недоступно")
        amount = _validate_money(amount, "Сумма пополнения")
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount

    def withdraw(self, amount):
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — снятие недоступно")
        amount = _validate_money(amount, "Сумма снятия")
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self._balance:
            raise ValueError("Недостаточно средств на счёте")
        self._balance -= amount

    def apply_interest(self):
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — проценты не начисляются")
        self._balance += self._balance * (self._interest_rate / 100.0)

    def deactivate(self):
        self._is_active = False

    def activate(self):
        self._is_active = True

    def __str__(self):
        status = "активен" if self._is_active else "заблокирован"
        return (
            f"Счёт №{self._account_number} | {self._holder_name} | "
            f"{self._balance:.2f} руб. | ставка {self._interest_rate:.1f}% | "
            f"{status}"
        )

    def __repr__(self):
        return (
            f"BankAccount(account_number={self._account_number!r}, "
            f"holder_name={self._holder_name!r}, "
            f"balance={self._balance!r}, "
            f"interest_rate={self._interest_rate!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self._account_number == other._account_number

    def __hash__(self):
        # хеш по номеру счёта — чтоб BankAccount можно было пихать в set/dict.
        # без этого Python ругается, потому что мы переопределили __eq__
        return hash(self._account_number)
