"""
Классы предметной области, реализующие интерфейсы из interfaces.py.

Иерархия та же, что в ЛР-3:
  BankAccount → CreditAccount, DepositAccount

Все три класса реализуют сразу два интерфейса — Printable и Comparable.
То есть мы и красиво печатаемся через to_string, и нормально сортируемся
через compare_to. Множественная реализация — то, что и нужно по заданию.
"""

from interfaces import Printable, Comparable


# ---------- валидаторы (как в прошлых лабах) ----------

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


# ---------- иерархия классов ----------


class BankAccount(Printable, Comparable):
    """Базовый банковский счёт.

    Сразу два интерфейса — Printable и Comparable, потому что классу
    надо и красиво печататься, и сравниваться. В Python множественное
    наследование от нескольких ABC — это норма.
    """

    bank_name = "z-bank_ZOV_GOYDA"
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
    @property
    def balance(self): return self._balance
    @property
    def interest_rate(self): return self._interest_rate
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
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — проценты не начисляются")
        self._balance += self._balance * (self._interest_rate / 100.0)

    def deactivate(self): self._is_active = False
    def activate(self): self._is_active = True

    # ---------- реализация Printable ----------

    def to_string(self) -> str:
        """Красивый отчёт — вот контракт Printable.

        Сделали мини-табличку, чтоб глазами читалось.
        """
        status = "активен" if self._is_active else "заблокирован"
        return (
            f"┌─ {self.kind} ─\n"
            f"│ №{self._account_number}\n"
            f"│ {self._holder_name}\n"
            f"│ Баланс: {self._balance:.2f} руб.\n"
            f"│ Ставка: {self._interest_rate:.1f}%\n"
            f"│ Статус: {status}\n"
            f"└─ {self.bank_name}"
        )

    # ---------- реализация Comparable ----------

    def compare_to(self, other) -> int:
        """Сравниваемся по балансу. -1 / 0 / +1."""
        if not isinstance(other, BankAccount):
            raise TypeError("Сравнивать BankAccount можно только с BankAccount-ом")
        if self._balance < other._balance:
            return -1
        if self._balance > other._balance:
            return 1
        return 0

    # ---------- стандартные dunder-методы ----------

    def __str__(self):
        # сокращённый str — для быстрых принтов в коллекциях. Полный отчёт — to_string().
        status = "активен" if self._is_active else "заблокирован"
        return (
            f"[{self.kind}] №{self._account_number} | {self._holder_name} | "
            f"{self._balance:.2f} руб. | {status}"
        )

    def __repr__(self):
        return (f"{type(self).__name__}(account_number={self._account_number!r}, "
                f"holder_name={self._holder_name!r}, balance={self._balance!r})")

    def __eq__(self, other):
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self._account_number == other._account_number

    def __hash__(self):
        return hash(self._account_number)


class CreditAccount(BankAccount):
    """Кредитный счёт — наследник BankAccount, оба интерфейса достаются автоматом."""

    kind = "Кредитный"

    def __init__(self, account_number, holder_name,
                 balance=0.0, interest_rate=0.0,
                 credit_limit=0.0, debt=0.0):
        super().__init__(account_number, holder_name, balance, interest_rate)
        self._credit_limit = _validate_money(credit_limit, "Кредитный лимит")
        self._debt = _validate_money(debt, "Долг")
        if self._debt > self._credit_limit:
            raise ValueError("Долг не может превышать кредитный лимит")

    @property
    def credit_limit(self): return self._credit_limit
    @property
    def debt(self): return self._debt

    def withdraw(self, amount):
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — снятие недоступно")
        amount = _validate_money(amount, "Сумма снятия")
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        available = self._balance + (self._credit_limit - self._debt)
        if amount > available:
            raise ValueError("Недостаточно средств с учётом кредитного лимита")
        if amount <= self._balance:
            self._balance -= amount
        else:
            remainder = amount - self._balance
            self._balance = 0.0
            self._debt += remainder

    def apply_interest(self):
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован")
        self._balance += self._balance * (self._interest_rate / 100.0)
        self._debt += self._debt * (self._interest_rate / 100.0)

    def to_string(self) -> str:
        # super() даёт нам базовый вывод, а мы добавляем своё про кредит
        base = super().to_string()
        # раскрываем декоративный ┘ и вставляем строчку про долг
        lines = base.splitlines()
        lines.insert(-1, f"│ Долг: {self._debt:.2f} / {self._credit_limit:.2f}")
        return "\n".join(lines)


class DepositAccount(BankAccount):
    """Вклад — заблокирован до mature(), потом снимай как обычный счёт."""

    kind = "Депозитный"

    def __init__(self, account_number, holder_name,
                 balance=0.0, interest_rate=0.0,
                 term_months=12):
        super().__init__(account_number, holder_name, balance, interest_rate)
        if not isinstance(term_months, int) or term_months <= 0:
            raise ValueError("Срок вклада должен быть положительным целым числом")
        self._term_months = term_months
        self._is_matured = False

    @property
    def term_months(self): return self._term_months
    @property
    def is_matured(self): return self._is_matured

    def mature(self): self._is_matured = True

    def withdraw(self, amount):
        if not self._is_matured:
            raise RuntimeError("Вклад ещё не созрел — снятие запрещено")
        super().withdraw(amount)

    def to_string(self) -> str:
        base = super().to_string()
        lines = base.splitlines()
        suffix = "созрел" if self._is_matured else f"заморожен на {self._term_months} мес."
        lines.insert(-1, f"│ Вклад: {suffix}")
        return "\n".join(lines)
