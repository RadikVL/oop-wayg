"""
Демка по интерфейсам (ABC) — Printable и Comparable.

Сценарии:
  1) одинаковый вызов to_string() для разных типов даёт разный вывод —
     это полиморфизм через интерфейс
  2) универсальные функции работают через интерфейс (print_all, find_max)
  3) фильтрация коллекции по интерфейсу + сортировка через compare_to
  4) проверка, что нельзя создать класс, забывший реализовать @abstractmethod

Запуск: python3 demo.py
"""

from abc import ABC, abstractmethod

from interfaces import Printable, Comparable
from models import BankAccount, CreditAccount, DepositAccount
from collection import AccountBook, print_all, find_max


def header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def make_num(tail):
    base = "40817810099910000000"
    return base[: 20 - len(tail)] + tail


def main():
    # -------------------------------------------------------------
    header("Сценарий 1. Один интерфейс — разные реализации")
    # -------------------------------------------------------------
    accounts = [
        BankAccount(make_num("0001"), "Иванов Иван", 1000, 5),
        CreditAccount(make_num("0002"), "Петров Пётр",
                      balance=500, interest_rate=12,
                      credit_limit=10000, debt=2000),
        DepositAccount(make_num("0003"), "Сидоров Сидор",
                       balance=20000, interest_rate=8, term_months=12),
    ]

    # к одной строчке кода — три разных красивых отчёта,
    # потому что каждый класс свой to_string() сделал по-своему
    for acc in accounts:
        print(acc.to_string())
        print()

    # -------------------------------------------------------------
    header("Сценарий 2. Универсальные функции через интерфейс")
    # -------------------------------------------------------------
    # print_all() и find_max() ничего не знают про BankAccount.
    # Они знают только про Printable / Comparable. И работают.
    print(">>> find_max() через Comparable:")
    biggest = find_max(accounts)
    print(f"  Самый жирный счёт: {biggest}")

    print("\n>>> isinstance-проверки:")
    for acc in accounts:
        print(f"  {type(acc).__name__:<15} "
              f"Printable={isinstance(acc, Printable)} "
              f"Comparable={isinstance(acc, Comparable)}")

    # -------------------------------------------------------------
    header("Сценарий 3. Коллекция: фильтр и сортировка через интерфейс")
    # -------------------------------------------------------------
    book = AccountBook()
    for acc in accounts:
        book.add(acc)
    book.add(BankAccount(make_num("0004"), "Кузнецов Кузьма", 750, 4))
    book.add(CreditAccount(make_num("0005"), "Должник Долгов",
                           balance=0, interest_rate=20,
                           credit_limit=3000, debt=2500))

    print(f"len(book) = {len(book)}")
    print(f"Printable объектов: {len(book.get_printable())}")
    print(f"Comparable объектов: {len(book.get_comparable())}")

    # сортируем через compare_to — без указания ключа сортировки.
    # объекты сами разберутся, кто из них больше
    book.sort_via_comparable()
    print("\nПосле sort_via_comparable() (по балансу через compare_to):")
    for acc in book:
        print(f"  {acc}")

    # -------------------------------------------------------------
    header("Сценарий 4. ABC реально форсит реализацию методов")
    # -------------------------------------------------------------
    # пробуем создать класс, который наследуется от Printable, но забыл
    # реализовать to_string() — Python должен ругнуться при попытке
    # создать объект
    class BrokenClass(Printable):
        pass  # ха-ха я не реализую to_string()

    try:
        _ = BrokenClass()
    except TypeError as e:
        print(f"  Создать BrokenClass нельзя — TypeError: {e}")

    # а если реализовали — всё ок
    class NormalClass(Printable):
        def to_string(self) -> str:
            return "я норм"

    obj = NormalClass()
    print(f"  NormalClass с to_string() — создаётся ок: {obj.to_string()}")


if __name__ == "__main__":
    main()
