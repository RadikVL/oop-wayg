"""
Базовый класс BankAccount — точно такой же, как в ЛР-1/ЛР-2.

Скопировали сюда, чтоб ЛР-3 запускалась автономно. От него мы дальше
наследуем CreditAccount и DepositAccount (см. models.py).
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
            raise ValueError("Имя владельца может содержать только буквы, пробелы и дефисы")
    return value.title()


def _validate_money(value, what):
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

    # человекочитаемое название "вида" счёта — потомки переопределят.
    # сделано через атрибут класса, чтоб __str__ работал полиморфно
    # без if-elif-чёрт-знает-чего
    kind = "Базовый счёт"

    def __init__(self, account_number, holder_name,
                 balance=0.0, interest_rate=0.0):
        self._account_number = _validate_account_number(account_number)
        self._holder_name = _validate_holder_name(holder_name)
        self._balance = _validate_money(balance, "Баланс")
        self._interest_rate = _validate_rate(interest_rate)
        self._is_active = True

    @property
    def account_number(self): return self._account_number

    @property
    def holder_name(self): return self._holder_name

    @holder_name.setter
    def holder_name(self, v): self._holder_name = _validate_holder_name(v)

    @property
    def balance(self): return self._balance

    @property
    def interest_rate(self): return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, v): self._interest_rate = _validate_rate(v)

    @property
    def is_active(self): return self._is_active

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
        """Начислить проценты. У потомков может быть своя логика — на то и polymorphism."""
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — проценты не начисляются")
        self._balance += self._balance * (self._interest_rate / 100.0)

    def deactivate(self): self._is_active = False
    def activate(self): self._is_active = True

    def __str__(self):
        status = "активен" if self._is_active else "заблокирован"
        # self.kind подхватится у потомков сам — на этом и держится полиморфный вывод
        return (
            f"[{self.kind}] №{self._account_number} | {self._holder_name} | "
            f"{self._balance:.2f} руб. | ставка {self._interest_rate:.1f}% | {status}"
        )

    def __repr__(self):
        return (
            f"{type(self).__name__}(account_number={self._account_number!r}, "
            f"holder_name={self._holder_name!r}, balance={self._balance!r}, "
            f"interest_rate={self._interest_rate!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self._account_number == other._account_number

    def __hash__(self):
        return hash(self._account_number)
