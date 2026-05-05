"""
Демка по Generics и Protocol.

Сценарии:
  1) TypedCollection[BankAccount] + find/filter/map (с разными типами R)
  2) TypedCollection с Protocol Displayable — структурная типизация без
     наследования: классы реализуют display(), но не наследуются от Displayable
  3) Тот же класс TypedCollection с другим протоколом — Scorable

Запуск: python3 demo.py
"""

from typing import cast

from model import BankAccount, CreditAccount, DepositAccount
from container import TypedCollection, Displayable, Scorable


def header(text: str) -> None:
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def make_num(tail: str) -> str:
    base = "40817810099910000000"
    return base[: 20 - len(tail)] + tail


def main() -> None:
    # -------------------------------------------------------------
    header("Сценарий 1. TypedCollection[BankAccount] + find/filter/map")
    # -------------------------------------------------------------
    accounts: TypedCollection[BankAccount] = TypedCollection()
    accounts.add(BankAccount(make_num("0001"), "Иванов Иван", 1500, 5))
    accounts.add(BankAccount(make_num("0002"), "Петров Пётр", 800, 3))
    accounts.add(BankAccount(make_num("0003"), "Сидоров Сидор", 5000, 7))

    print(f"len(accounts) = {len(accounts)}")
    for acc in accounts:
        print(f"  {acc}")

    # find: один раз нашли, один раз не нашли
    found = accounts.find(lambda a: a.holder_name == "Петров Пётр")
    print(f"\nfind(holder == 'Петров Пётр') → {found}")

    not_found = accounts.find(lambda a: a.balance > 1_000_000)
    print(f"find(balance > 1_000_000) → {not_found}")

    # filter
    rich = accounts.filter(lambda a: a.balance > 1000)
    print(f"\nfilter(balance > 1000) → {len(rich)} счёт(ов):")
    for acc in rich: print(f"  {acc}")

    # map с разными R: один раз → list[str], другой раз → list[float]
    names: list[str] = accounts.map(lambda a: a.holder_name)
    print(f"\nmap(holder_name) → list[str]:   {names}")

    balances: list[float] = accounts.map(lambda a: a.balance)
    print(f"map(balance)     → list[float]: {balances}")

    # -------------------------------------------------------------
    header("Сценарий 2. TypedCollection с Protocol Displayable")
    # -------------------------------------------------------------
    # Главная мысль: BankAccount, CreditAccount, DepositAccount НЕ
    # наследуются от Displayable. У них просто есть метод display().
    # Этого Protocol-у достаточно — структурная типизация рулит.

    displayables: TypedCollection[Displayable] = TypedCollection()
    displayables.add(BankAccount(make_num("0010"), "Иванов Иван", 1500, 5))
    displayables.add(CreditAccount(make_num("0011"), "Петров Пётр",
                                   balance=500, interest_rate=12,
                                   credit_limit=10000, debt=2000))
    displayables.add(DepositAccount(make_num("0012"), "Сидоров Сидор",
                                    balance=20000, interest_rate=8,
                                    term_months=12))

    # доказываем, что Protocol реально проверяется через isinstance
    print("isinstance-проверки на Displayable:")
    for item in displayables:
        # cast чисто чтоб mypy не ругался — мы и так знаем, что item имеет display()
        print(f"  {type(item).__name__:<15} → "
              f"isinstance(item, Displayable) = {isinstance(item, Displayable)}")

    print("\nдёргаем display() для каждого:")
    for item in displayables:
        # тут IDE знает, что у item точно есть display() → можно вызывать
        # без жалоб, хотя BankAccount не наследуется от Displayable
        print(f"  {item.display()}")

    # -------------------------------------------------------------
    header("Сценарий 3. Тот же TypedCollection — но с Protocol Scorable")
    # -------------------------------------------------------------
    # Один и тот же класс TypedCollection работает с разными ограничениями.
    # Это и есть смысл генериков.

    scorables: TypedCollection[Scorable] = TypedCollection()
    scorables.add(BankAccount(make_num("0020"), "Богатый Богатов", 100000, 5))
    scorables.add(CreditAccount(make_num("0021"), "Должник Долгов",
                                balance=1000, interest_rate=15,
                                credit_limit=50000, debt=30000))
    scorables.add(DepositAccount(make_num("0022"), "Вкладчик Вкладов",
                                 balance=20000, interest_rate=10,
                                 term_months=24))

    # для каждого классa — score() считается по-своему:
    #   BankAccount   → balance
    #   CreditAccount → balance - debt
    #   DepositAccount → balance + проекция процентов
    print("score() для каждого:")
    for item in scorables:
        # IDE знает, что у item есть score() → safe
        print(f"  {type(item).__name__:<15} score = {item.score():>10.2f}")

    # сортировка через score() — Protocol даёт нам доступ к нужному методу
    print("\nотсортировано по score() (убыв.):")
    sorted_items = sorted(scorables, key=lambda x: x.score(), reverse=True)
    for item in sorted_items:
        # cast тут чисто чтоб IDE могла одновременно дёрнуть display() —
        # потому что оба наших класса фактически реализуют оба протокола
        showable = cast(Displayable, item)
        print(f"  {item.score():>10.2f}  ::  {showable.display()}")


if __name__ == "__main__":
    main()
