"""
Производные классы — наследуемся от BankAccount из base.py.

Реализованы:
  - CreditAccount  — кредитный счёт. Можно уйти в минус до credit_limit,
                     долг копится, проценты капают на ДОЛГ (а не на остаток).
  - DepositAccount — вклад. Снимать нельзя, пока вклад не "созрел".
                     Когда созрел — снимается как обычный счёт.

Полиморфизм здесь — в переопределении withdraw() и apply_interest():
снаружи мы дёргаем одно и то же имя метода, а делает он разное
в зависимости от типа объекта. Никаких if isinstance() в вызывающем коде.
"""

from base import BankAccount, _validate_money


class CreditAccount(BankAccount):
    """Кредитный счёт.

    Помимо обычного баланса есть кредитный лимит. Если снять больше,
    чем есть на балансе, остаток уходит в долг. Долг растёт, если на
    него начислять проценты. Чтоб погасить долг — pay_debt(amount).
    """

    kind = "Кредитный"

    def __init__(self, account_number, holder_name,
                 balance=0.0, interest_rate=0.0,
                 credit_limit=0.0, debt=0.0):
        # super() — чтоб не дублировать всю валидацию из родителя.
        # тупо отдаём ему то, что он умеет проверять, а сами добиваем своё
        super().__init__(account_number, holder_name, balance, interest_rate)
        self._credit_limit = _validate_money(credit_limit, "Кредитный лимит")
        self._debt = _validate_money(debt, "Долг")
        if self._debt > self._credit_limit:
            raise ValueError("Долг не может превышать кредитный лимит")

    @property
    def credit_limit(self): return self._credit_limit

    @property
    def debt(self): return self._debt

    @property
    def available(self):
        """Сколько ещё можно потратить: остаток на балансе плюс свободный лимит."""
        return self._balance + (self._credit_limit - self._debt)

    def withdraw(self, amount):
        """Снятие — переопределяем: можно уйти в долг до credit_limit."""
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — снятие недоступно")
        amount = _validate_money(amount, "Сумма снятия")
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        if amount > self.available:
            # вот тут принципиальное отличие от базового класса:
            # лимит у нас не баланс, а balance + (credit_limit - debt)
            raise ValueError("Недостаточно средств с учётом кредитного лимита")
        if amount <= self._balance:
            # снимаем чисто с баланса — никакого долга
            self._balance -= amount
        else:
            # сначала съедаем весь остаток на балансе, недостающее идёт в долг
            remainder = amount - self._balance
            self._balance = 0.0
            self._debt += remainder

    def pay_debt(self, amount):
        """Погасить долг (полностью или частично)."""
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — погашение недоступно")
        amount = _validate_money(amount, "Сумма погашения")
        if amount <= 0:
            raise ValueError("Сумма погашения должна быть положительной")
        if amount > self._debt:
            # пускай сами не лажают и не платят больше, чем должны
            raise ValueError("Сумма погашения больше текущего долга")
        self._debt -= amount

    def apply_interest(self):
        """Проценты на ДОЛГ, а не на остаток.

        Это и есть полиморфизм: имя метода то же, что у базового,
        но смысл другой. Кредит работает наоборот — банк начисляет
        проценты НА ВАС, а не вам.
        """
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — проценты не начисляются")
        # на положительный баланс тоже начислим — мало ли (это уже доход клиента),
        # но основное действие — рост долга
        self._balance += self._balance * (self._interest_rate / 100.0)
        self._debt += self._debt * (self._interest_rate / 100.0)

    def __str__(self):
        # дёргаем базовый __str__ и добавляем своё
        base = super().__str__()
        return base + f" | долг {self._debt:.2f}/{self._credit_limit:.2f}"


class DepositAccount(BankAccount):
    """Депозитный счёт (вклад).

    Главная фишка — пока вклад не "созрел" (mature()), снимать нельзя.
    Кладут туда деньги, держат, потом размораживают и снимают.
    """

    kind = "Депозитный"

    def __init__(self, account_number, holder_name,
                 balance=0.0, interest_rate=0.0,
                 term_months=12):
        super().__init__(account_number, holder_name, balance, interest_rate)
        if not isinstance(term_months, int) or term_months <= 0:
            raise ValueError("Срок вклада должен быть положительным целым числом")
        self._term_months = term_months
        self._is_matured = False  # сначала вклад заморожен по сроку

    @property
    def term_months(self): return self._term_months

    @property
    def is_matured(self): return self._is_matured

    def mature(self):
        """Открыть вклад: срок истёк, теперь можно снимать."""
        self._is_matured = True

    def withdraw(self, amount):
        """Пока вклад не созрел — снимать нельзя, хоть стой, хоть падай."""
        if not self._is_matured:
            raise RuntimeError("Вклад ещё не созрел — снятие запрещено")
        # дальше — обычная логика родителя
        super().withdraw(amount)

    def __str__(self):
        base = super().__str__()
        suffix = "созрел" if self._is_matured else f"заморожен на {self._term_months} мес."
        return base + f" | {suffix}"
