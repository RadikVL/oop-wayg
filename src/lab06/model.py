"""
Иерархия счетов из ЛР-3, дополненная двумя методами:
  - display() — красивое строковое представление (под Protocol Displayable);
  - score()   — численная оценка "ценности" счёта (под Protocol Scorable).

Важно: классы НЕ наследуются от протоколов. Они просто имеют нужные
методы — этого достаточно, чтобы пройти структурную типизацию.
В этом и смысл Protocol: «не важно, кто ты по родословной, важно
что ты умеешь».
"""


def _validate_account_number(value):
    if not isinstance(value, str): raise ValueError("Номер счёта должен быть строкой")
    value = value.strip()
    if value == "": raise ValueError("Номер счёта не может быть пустым")
    if not value.isdigit(): raise ValueError("Номер счёта должен состоять только из цифр")
    if len(value) != 20: raise ValueError("Номер счёта должен содержать ровно 20 цифр")
    return value


def _validate_holder_name(value):
    if not isinstance(value, str): raise ValueError("Имя владельца должно быть строкой")
    value = value.strip()
    if value == "": raise ValueError("Имя владельца не может быть пустым")
    for ch in value:
        if not (ch.isalpha() or ch in (" ", "-")):
            raise ValueError("Имя владельца может содержать только буквы, пробелы и дефисы")
    return value.title()


def _validate_money(value: float, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{what} должен быть числом")
    if value < 0:
        raise ValueError(f"{what} не может быть отрицательным")
    return float(value)


def _validate_rate(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Процентная ставка должна быть числом")
    if value < 0 or value > 100:
        raise ValueError("Процентная ставка должна быть в диапазоне [0; 100]")
    return float(value)


class BankAccount:
    """Базовый банковский счёт.

    Атрибуты типизированы: видно, что хранится. Полная аннотация —
    для генериков и протоколов в lab06 это критично.
    """

    bank_name: str = "z-bank_ZOV_GOYDA"
    kind: str = "Базовый счёт"

    def __init__(self, account_number: str, holder_name: str,
                 balance: float = 0.0, interest_rate: float = 0.0) -> None:
        self._account_number: str = _validate_account_number(account_number)
        self._holder_name: str = _validate_holder_name(holder_name)
        self._balance: float = _validate_money(balance, "Баланс")
        self._interest_rate: float = _validate_rate(interest_rate)
        self._is_active: bool = True

    @property
    def account_number(self) -> str: return self._account_number
    @property
    def holder_name(self) -> str: return self._holder_name
    @property
    def balance(self) -> float: return self._balance
    @property
    def interest_rate(self) -> float: return self._interest_rate
    @property
    def is_active(self) -> bool: return self._is_active

    def deposit(self, amount: float) -> None:
        if not self._is_active: raise RuntimeError("Заблокирован")
        amount = _validate_money(amount, "Сумма пополнения")
        if amount <= 0: raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if not self._is_active: raise RuntimeError("Заблокирован")
        amount = _validate_money(amount, "Сумма снятия")
        if amount <= 0: raise ValueError("Сумма снятия должна быть положительной")
        if amount > self._balance: raise ValueError("Недостаточно средств")
        self._balance -= amount

    def deactivate(self) -> None: self._is_active = False
    def activate(self) -> None: self._is_active = True

    # ---------- методы под Protocol-ы ----------

    def display(self) -> str:
        """Под Protocol Displayable. Никакого ABC, просто наличие метода."""
        status = "активен" if self._is_active else "заблокирован"
        return (f"{self.kind} №{self._account_number} | {self._holder_name} | "
                f"{self._balance:.2f} руб. | {status}")

    def score(self) -> float:
        """Под Protocol Scorable. Простая метрика — баланс."""
        return self._balance

    # ---------- стандартные dunder-методы ----------

    def __str__(self) -> str:
        return self.display()

    def __repr__(self) -> str:
        return (f"{type(self).__name__}(account_number={self._account_number!r}, "
                f"holder_name={self._holder_name!r}, balance={self._balance!r})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BankAccount): return NotImplemented
        return self._account_number == other._account_number

    def __hash__(self) -> int:
        return hash(self._account_number)


class CreditAccount(BankAccount):
    kind = "Кредитный"

    def __init__(self, account_number: str, holder_name: str,
                 balance: float = 0.0, interest_rate: float = 0.0,
                 credit_limit: float = 0.0, debt: float = 0.0) -> None:
        super().__init__(account_number, holder_name, balance, interest_rate)
        self._credit_limit: float = _validate_money(credit_limit, "Кредитный лимит")
        self._debt: float = _validate_money(debt, "Долг")
        if self._debt > self._credit_limit:
            raise ValueError("Долг не может превышать кредитный лимит")

    @property
    def credit_limit(self) -> float: return self._credit_limit
    @property
    def debt(self) -> float: return self._debt

    def display(self) -> str:
        # переопределение — добавили строчку про долг
        return super().display() + f" | долг {self._debt:.2f}/{self._credit_limit:.2f}"

    def score(self) -> float:
        # реальная "ценность" — баланс минус долг. Может быть и отрицательной
        return self._balance - self._debt


class DepositAccount(BankAccount):
    kind = "Депозитный"

    def __init__(self, account_number: str, holder_name: str,
                 balance: float = 0.0, interest_rate: float = 0.0,
                 term_months: int = 12) -> None:
        super().__init__(account_number, holder_name, balance, interest_rate)
        if not isinstance(term_months, int) or term_months <= 0:
            raise ValueError("Срок вклада должен быть положительным целым числом")
        self._term_months: int = term_months
        self._is_matured: bool = False

    @property
    def term_months(self) -> int: return self._term_months
    @property
    def is_matured(self) -> bool: return self._is_matured

    def mature(self) -> None: self._is_matured = True

    def display(self) -> str:
        suffix = "созрел" if self._is_matured else f"заморожен на {self._term_months} мес."
        return super().display() + f" | вклад: {suffix}"

    def score(self) -> float:
        # ценность вклада = баланс плюс прогноз процентов до конца срока.
        # вышло проще обычного: чем дольше срок и выше ставка, тем больше.
        # Считаем простыми процентами, для учебной задачи сойдёт
        return self._balance * (1 + self._interest_rate / 100.0 * self._term_months / 12)
