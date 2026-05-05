"""
Класс BankAccount — банковский счёт.

Что лежит внутри (всё закрытое, снаружи дёргаем через свойства):
    _account_number — номер счёта (20 цифр), после создания не трогаем
    _holder_name    — ФИО владельца
    _balance        — сколько денег на счёте прямо сейчас
    _interest_rate  — процентная ставка (% годовых)
    _is_active      — состояние: счёт жив или заморожен

Атрибут класса:
    bank_name — название банка, оно одно на всех, поэтому не на экземпляре
"""

from validate import (
    validate_account_number,
    validate_holder_name,
    validate_balance,
    validate_interest_rate,
)


class BankAccount:
    # банк один на все счета, поэтому держим на классе, а не дублируем
    # в каждом экземпляре — ибо нефиг память жечь
    bank_name = "z-bank_ZOV_GOYDA"

    def __init__(self, account_number, holder_name,
                 balance=0.0, interest_rate=0.0):
        # всё валидируем сразу при создании — если кривое, объект просто
        # не родится, и дальше с ним ничего сломанного делать не придётся
        self._account_number = validate_account_number(account_number)
        self._holder_name = validate_holder_name(holder_name)
        self._balance = validate_balance(balance)
        self._interest_rate = validate_interest_rate(interest_rate)
        # свежий счёт сразу активен — заблокированный с рождения смысла не имеет
        self._is_active = True

    # ---------- свойства (где-то только чтение, где-то с сеттером) ----------

    @property
    def account_number(self):
        # номер счёта менять нельзя в принципе — поэтому только геттер
        return self._account_number

    @property
    def holder_name(self):
        return self._holder_name

    @holder_name.setter
    def holder_name(self, new_name):
        # при смене имени гоним через ту же валидацию, что и в конструкторе —
        # чтоб не было хитрого пути обойти проверку через присваивание
        self._holder_name = validate_holder_name(new_name)

    @property
    def balance(self):
        # снаружи только смотрим. Менять — только через deposit/withdraw,
        # чтоб мимо проверок никто бабло не подкрутил
        return self._balance

    @property
    def interest_rate(self):
        return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, new_rate):
        self._interest_rate = validate_interest_rate(new_rate)

    @property
    def is_active(self):
        # is_active напрямую не присваиваем — для этого есть activate/deactivate,
        # чтоб смена состояния всегда шла через нормальные методы
        return self._is_active

    # ---------- бизнес-методы ----------

    def deposit(self, amount):
        """Положить деньги на счёт."""
        # на замороженный счёт деньги не льём
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — пополнение недоступно")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Сумма пополнения должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма пополнения должна быть положительной")
        self._balance += amount

    def withdraw(self, amount):
        """Снять деньги со счёта."""
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — снятие недоступно")
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise ValueError("Сумма снятия должна быть числом")
        if amount <= 0:
            raise ValueError("Сумма снятия должна быть положительной")
        # вот эта проверка — чтоб баланс не уехал в минус. Нефиг снимать то,
        # чего нет
        if amount > self._balance:
            raise ValueError("Недостаточно средств на счёте")
        self._balance -= amount

    def apply_interest(self):
        """Накинуть проценты по ставке на текущий остаток."""
        if not self._is_active:
            raise RuntimeError("Счёт заблокирован — проценты не начисляются")
        self._balance += self._balance * (self._interest_rate / 100.0)

    # ---------- управление состоянием ----------

    def deactivate(self):
        """Заморозить счёт (например, по заявлению клиента)."""
        self._is_active = False

    def activate(self):
        """Разморозить — счёт снова рабочий."""
        self._is_active = True

    # ---------- магические методы ----------

    def __str__(self):
        # это то, что увидит человек через print() — поэтому красиво и понятно
        status = "активен" if self._is_active else "заблокирован"
        return (
            f"Счёт №{self._account_number}\n"
            f"  Владелец: {self._holder_name}\n"
            f"  Баланс: {self._balance:.2f} руб.\n"
            f"  Ставка: {self._interest_rate:.1f}% годовых\n"
            f"  Статус: {status}\n"
            f"  Банк: {BankAccount.bank_name}"
        )

    def __repr__(self):
        # это для разработчика — формально, чтоб строку можно было
        # тупо скопировать и пересоздать такой же объект
        return (
            f"BankAccount(account_number={self._account_number!r}, "
            f"holder_name={self._holder_name!r}, "
            f"balance={self._balance!r}, "
            f"interest_rate={self._interest_rate!r})"
        )

    def __eq__(self, other):
        # два счёта равны, только если совпал номер. Имя/баланс/ставка
        # могут различаться сколько угодно — это всё равно один и тот же счёт.
        # Если сравнивают с чем-то не-BankAccount — отдаём NotImplemented,
        # пусть Python сам разруливает, не наша забота
        if not isinstance(other, BankAccount):
            return NotImplemented
        return self._account_number == other._account_number
