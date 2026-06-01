"""
Слой бизнес-логики. CLI сюда стучится за всем, что касается счетов —
напрямую к коллекции или к моделям из CLI ходить нельзя по условию.

Внутри держим TypedCollection[BankAccount] (Generic из ЛР-6) — она
типизирована, ничего лишнего сюда не запихнёшь.

Что тут лежит, помимо сервиса:
  - SORT_STRATEGIES — словарь стратегий сортировки. CLI берёт ключи
    для меню, app — значения для sorted(). Меняем стратегии в одном
    месте.
  - ACCOUNT_KINDS — словарь "код типа → человеческое имя". CLI рисует
    из него менюшку добавления и фильтра по типу. Без этой константы
    CLI пришлось бы знать про подклассы моделей.
  - account_view — формат-агностичный рендер строки счёта (dict).
    CLI просто печатает поля по ключам, не зная про CreditAccount /
    DepositAccount. Это и есть «не пускать модели в cli.py».
"""

from __future__ import annotations

from typing import Any, Callable

from exceptions import AccountNotFoundError, DuplicateAccountError
from models import BankAccount, CreditAccount, DepositAccount
from container import TypedCollection


# ============================================================
# Стратегии сортировки (функции-ключи под sorted(key=...))
# Те же самые, что были в ЛР-5
# ============================================================

def _by_holder(acc: BankAccount) -> str:
    return acc.holder_name


def _by_balance(acc: BankAccount) -> float:
    return acc.balance


def _by_score(acc: BankAccount) -> float:
    return acc.score()


# словарь "имя → функция-ключ". CLI берёт ключи для меню,
# app берёт значения для sorted(). Имена на русском — это юзер их увидит
SORT_STRATEGIES: dict[str, Callable[[BankAccount], object]] = {
    "По имени владельца": _by_holder,
    "По балансу": _by_balance,
    "По оценке (score из ЛР-6)": _by_score,
}


# ============================================================
# Типы счетов — словарь "внутренний код → короткое имя для людей"
# CLI этим пользуется для меню "добавить" и фильтра по типу.
# Если в моделях появится новый класс — добавляем сюда + фабрику + ветку
# в _filter_predicate_for_kind, и CLI ничего вообще менять не надо
# ============================================================

ACCOUNT_KINDS: dict[str, str] = {
    "bank": "Базовый",
    "credit": "Кредитный",
    "deposit": "Депозитный",
}


def _kind_of(acc: BankAccount) -> str:
    """Внутренний код типа счёта по экземпляру. Inverse от фабрик."""
    # порядок важен: CreditAccount/DepositAccount — наследники BankAccount,
    # сначала проверяем подклассы, потом базу
    if isinstance(acc, CreditAccount):
        return "credit"
    if isinstance(acc, DepositAccount):
        return "deposit"
    return "bank"


# ============================================================
# Вью-функция: счёт → словарь под печать таблицы.
# CLI этим пользуется и больше ничего про модели знать не хочет
# ============================================================

def account_view(acc: BankAccount) -> dict[str, Any]:
    """Развернуть счёт в плоский dict под табличный вывод.

    Поля:
      number  — номер счёта (str)
      kind    — короткое читаемое имя типа ("Базовый" / ...)
      holder  — владелец
      balance — баланс (float)
      active  — True/False
      extra   — вторая строка с деталями подкласса, либо None

    Сделано в app.py намеренно: подклассовые поля (.debt, .term_months
    и т.п.) — внутрянка предметки, CLI про них знать не должен.
    """
    code = _kind_of(acc)
    extra: str | None = None
    if isinstance(acc, CreditAccount):
        extra = f"долг {acc.debt:.2f} из {acc.credit_limit:.2f}"
    elif isinstance(acc, DepositAccount):
        extra = "созрел" if acc.is_matured else f"заморожен на {acc.term_months} мес."

    return {
        "number": acc.account_number,
        "kind": ACCOUNT_KINDS[code],
        "holder": acc.holder_name,
        "balance": acc.balance,
        "active": acc.is_active,
        "extra": extra,
    }


# ============================================================
# Сервис — фасад над коллекцией
# ============================================================

class AccountService:
    """Бизнес-логика поверх TypedCollection[BankAccount].

    CLI знает только про этот класс, ACCOUNT_KINDS, SORT_STRATEGIES,
    account_view и наши исключения. Никаких импортов моделей в cli.py
    — это и есть разделение на слои.
    """

    def __init__(self) -> None:
        self._book: TypedCollection[BankAccount] = TypedCollection()

    # ---------- доступ к данным ----------

    def all(self) -> list[BankAccount]:
        """Все счета списком — копия, чтоб снаружи не лапали."""
        return self._book.get_all()

    def count(self) -> int:
        return len(self._book)

    def get(self, account_number: str) -> BankAccount:
        """Найти счёт по номеру. Нет — ругаемся AccountNotFoundError."""
        found = self._book.find(lambda a: a.account_number == account_number)
        if found is None:
            raise AccountNotFoundError(account_number)
        return found

    # ---------- мутации ----------

    def add(self, account: BankAccount) -> None:
        """Добавить готовый счёт. Дубли по номеру — ошибка.

        Обычно из CLI зовутся фабрики ниже (create_basic/credit/deposit),
        этот метод тут для load_from и для тестов.
        """
        if self._book.find(lambda a: a.account_number == account.account_number) is not None:
            raise DuplicateAccountError(account.account_number)
        self._book.add(account)

    # ---------- фабрики: единственное место, где CLI получает новый счёт ----------

    def create_basic(self, number: str, holder: str,
                     balance: float, rate: float) -> BankAccount:
        """Создать и добавить базовый счёт. Возвращает добавленный счёт."""
        acc = BankAccount(number, holder, balance, rate)
        self.add(acc)
        return acc

    def create_credit(self, number: str, holder: str,
                      balance: float, rate: float,
                      credit_limit: float, debt: float) -> BankAccount:
        """Создать и добавить кредитный счёт."""
        acc = CreditAccount(number, holder, balance, rate, credit_limit, debt)
        self.add(acc)
        return acc

    def create_deposit(self, number: str, holder: str,
                       balance: float, rate: float,
                       term_months: int) -> BankAccount:
        """Создать и добавить депозитный счёт."""
        acc = DepositAccount(number, holder, balance, rate, term_months)
        self.add(acc)
        return acc

    def remove(self, account_number: str) -> BankAccount:
        """Удалить счёт по номеру. Возвращаем удалённый — чтоб CLI мог
        в подтверждении показать, кого именно прибили."""
        acc = self.get(account_number)
        self._book.remove(acc)
        return acc

    def deposit(self, account_number: str, amount: float) -> None:
        """Пополнить счёт. Сам деньги валидирует BankAccount.deposit."""
        self.get(account_number).deposit(amount)

    def withdraw(self, account_number: str, amount: float) -> None:
        """Снять со счёта. Валидация — внутри метода счёта."""
        self.get(account_number).withdraw(amount)

    # ---------- фильтры (из ЛР-5) ----------

    def filter_by_kind(self, kind: str) -> list[BankAccount]:
        """Фильтр по типу: ключ из ACCOUNT_KINDS ('bank' | 'credit' | 'deposit').

        Делаем через isinstance — это надёжнее, чем сравнивать .kind
        строкой (вдруг кто-то поменяет константу класса)
        """
        if kind == "bank":
            # именно базовый — не наследники. type(...) is, без isinstance
            return self._book.filter(lambda a: type(a) is BankAccount)
        if kind == "credit":
            return self._book.filter(lambda a: isinstance(a, CreditAccount))
        if kind == "deposit":
            return self._book.filter(lambda a: isinstance(a, DepositAccount))
        raise ValueError(f"Неизвестный тип счёта: {kind!r}")

    def filter_by_balance(self, min_value: float, max_value: float) -> list[BankAccount]:
        """Счета с балансом в диапазоне [min, max].

        Проверка корректности диапазона — тут, в бизнес-логике. CLI
        просто прокидывает два числа, а валидно ли это — наше дело.
        """
        if min_value > max_value:
            raise ValueError("Минимум больше максимума — такой диапазон не имеет смысла")
        return self._book.filter(lambda a: min_value <= a.balance <= max_value)

    # ---------- сортировка (стратегия выбирается снаружи) ----------

    def sorted_by(self, strategy_name: str, reverse: bool = False) -> list[BankAccount]:
        """Отсортировать копию списка по выбранной стратегии.

        strategy_name — ключ из SORT_STRATEGIES. CLI его получает из юзера
        через меню (см. cli.py).
        """
        if strategy_name not in SORT_STRATEGIES:
            raise ValueError(f"Неизвестная стратегия сортировки: {strategy_name!r}")
        key = SORT_STRATEGIES[strategy_name]
        return sorted(self._book, key=key, reverse=reverse)

    # ---------- загрузка из storage ----------

    def load_from(self, accounts: list[BankAccount]) -> None:
        """Залить уже распарсенные счета в коллекцию (вызывает main на старте).

        Сам storage сюда не дёргаем — оставляем main-у, чтоб service
        не знал про файловую систему. Так слои не мешаются.
        """
        # стартовое состояние затираем — на случай, если кто-то решит перезагрузить
        self._book = TypedCollection()
        for acc in accounts:
            self._book.add(acc)
