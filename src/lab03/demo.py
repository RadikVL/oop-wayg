"""
Демка по наследованию.

Сценарии:
  1) разные типы счетов в одной коллекции, общий вызов apply_interest()
     даёт разное поведение — это и есть полиморфизм без if-ов
  2) специфические методы потомков (pay_debt у кредита, mature у вклада)
  3) фильтрация коллекции по типу через isinstance

Запуск: python3 demo.py
"""

from base import BankAccount
from models import CreditAccount, DepositAccount
from collection import AccountBook


def header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def make_num(tail):
    base = "40817810099910000000"
    return base[: 20 - len(tail)] + tail


def main():
    # -------------------------------------------------------------
    header("Сценарий 1. Разные типы счетов через единую коллекцию")
    # -------------------------------------------------------------
    book = AccountBook()
    # обычный, кредитный, депозитный — все лежат в одной коллекции,
    # потому что все они BankAccount по сути
    book.add(BankAccount(make_num("0001"), "Иванов Иван", 1000, 5))
    book.add(CreditAccount(make_num("0002"), "Петров Пётр",
                           balance=500, interest_rate=12,
                           credit_limit=10000, debt=2000))
    book.add(DepositAccount(make_num("0003"), "Сидоров Сидор",
                            balance=20000, interest_rate=8,
                            term_months=12))

    print(book)

    # тут самое интересное: дёргаем apply_interest() для всех подряд,
    # но каждый делает по-своему — благодаря переопределению метода
    print("\napply_interest() для каждого:")
    for acc in book:
        before = (acc.balance,
                  acc.debt if isinstance(acc, CreditAccount) else None)
        try:
            acc.apply_interest()
        except RuntimeError as e:
            print(f"  {type(acc).__name__:<15} → {e}")
            continue
        after = (acc.balance,
                 acc.debt if isinstance(acc, CreditAccount) else None)
        print(f"  {type(acc).__name__:<15} баланс {before[0]:>8.2f} → {after[0]:>8.2f}", end="")
        if before[1] is not None:
            print(f"  | долг {before[1]:>8.2f} → {after[1]:>8.2f}")
        else:
            print()

    # тут видно: у обычного счёта вырос баланс,
    # у кредитного — вырос долг (что логично, проценты идут банку),
    # у депозита — тоже вырос баланс

    # -------------------------------------------------------------
    header("Сценарий 2. Специфические методы потомков")
    # -------------------------------------------------------------
    credit = book[1]   # это CreditAccount
    deposit = book[2]  # это DepositAccount

    print(f"До: {credit}")
    credit.withdraw(700)  # снимаем больше, чем есть на балансе
    print(f"withdraw(700) → {credit}")
    print(f"  баланс: {credit.balance:.2f}, долг: {credit.debt:.2f}, "
          f"свободно: {credit.available:.2f}")

    credit.pay_debt(500)
    print(f"\npay_debt(500) → долг: {credit.debt:.2f}")

    # пробуем снять с депозита, пока он заморожен — должно отбить
    print(f"\nПопытка снять с депозита (он ещё заморожен):")
    try:
        deposit.withdraw(100)
    except RuntimeError as e:
        print(f"  RuntimeError: {e}")

    deposit.mature()  # типа срок прошёл
    print(f"\nПосле mature(): {deposit}")
    deposit.withdraw(5000)
    print(f"После withdraw(5000): {deposit}")

    # -------------------------------------------------------------
    header("Сценарий 3. Фильтрация коллекции по типу")
    # -------------------------------------------------------------
    # добавим ещё пару счетов разных типов
    book.add(CreditAccount(make_num("0004"), "Кредитный Клиент",
                           balance=0, interest_rate=15, credit_limit=5000))
    book.add(DepositAccount(make_num("0005"), "Вкладчик Вкладов",
                            balance=100000, interest_rate=6, term_months=6))

    only_credit = book.get_only_credit()
    only_deposit = book.get_only_deposit()
    print(f"Всего в book: {len(book)}")
    print(f"Только кредитных: {len(only_credit)}")
    for acc in only_credit:
        print(f"  {acc}")
    print(f"Только депозитных: {len(only_deposit)}")
    for acc in only_deposit:
        print(f"  {acc}")

    # проверка через isinstance — что наследование на уровне типов работает
    print("\nПроверки isinstance:")
    for acc in book:
        print(f"  {type(acc).__name__:<15} "
              f"BankAccount={isinstance(acc, BankAccount)} "
              f"CreditAccount={isinstance(acc, CreditAccount)} "
              f"DepositAccount={isinstance(acc, DepositAccount)}")


if __name__ == "__main__":
    main()
