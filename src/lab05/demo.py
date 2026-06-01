"""
Демка по функциям как аргументам и паттерну «Стратегия».

Сценарии:
  1) сортировки с тремя разными стратегиями + фильтры
  2) map(), фабрика функций, методы sort_by/filter_by на коллекции
  3) цепочка filter → sort → apply, замена стратегии налету,
     callable-объект как стратегия

Запуск: python3 demo.py
"""

from model import BankAccount, CreditAccount, DepositAccount
from collection import AccountBook
from strategies import (
    by_balance, by_holder, by_rate, by_kind_then_balance,
    is_active, is_blocked, is_credit,
    make_richer_than, make_holder_filter, make_rate_in_range,
    to_summary, to_balance, to_holder,
    DiscountStrategy, InterestStrategy,
)


def header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def make_num(tail):
    base = "40817810099910000000"
    return base[: 20 - len(tail)] + tail


def build_book():
    """Соберём базовый набор счетов — чтоб дальше не дублироваться."""
    book = AccountBook()
    book.add(BankAccount(make_num("0001"), "Иванов Иван", 1500, 5))
    book.add(BankAccount(make_num("0002"), "Петров Пётр", 800, 3))
    book.add(CreditAccount(make_num("0003"), "Сидоров Сидор",
                           balance=2000, interest_rate=12,
                           credit_limit=10000, debt=500))
    book.add(DepositAccount(make_num("0004"), "Кузнецов Кузьма",
                            balance=50000, interest_rate=8, term_months=12))
    book.add(BankAccount(make_num("0005"), "Должник Должников", 100, 10))
    return book


def main():
    # -------------------------------------------------------------
    header("Сценарий 1. Три стратегии сортировки + два фильтра")
    # -------------------------------------------------------------
    book = build_book()
    print(book)

    print("\n>>> sorted(book, key=by_balance):")
    for acc in sorted(book, key=by_balance):
        print(f"  {to_summary(acc)}")

    print("\n>>> sorted(book, key=by_holder):")
    for acc in sorted(book, key=by_holder):
        print(f"  {to_summary(acc)}")

    print("\n>>> sorted(book, key=by_kind_then_balance) — двухуровневая:")
    for acc in sorted(book, key=by_kind_then_balance):
        print(f"  [{acc.kind:<12}] {to_summary(acc)}")

    print("\n>>> filter(is_active, book):")
    for acc in filter(is_active, book):
        print(f"  {to_summary(acc)}")

    # пометим часть счетов как заблокированные — чтоб фильтр был не пустой
    book[1].deactivate()
    book[4].deactivate()

    print("\n>>> filter(is_blocked, book) после блокировки двух:")
    for acc in filter(is_blocked, book):
        print(f"  {to_summary(acc)}")

    # -------------------------------------------------------------
    header("Сценарий 2. map(), фабрика функций, sort_by/filter_by")
    # -------------------------------------------------------------
    book = build_book()  # возьмём свежий набор без блокировок

    # --- map() через встроенный + через метод коллекции ---
    summaries = list(map(to_summary, book))
    print(">>> map(to_summary, book):")
    for s in summaries: print(f"  {s}")

    print("\n>>> book.map(to_balance):")
    print(f"  {book.map(to_balance)}")

    print("\n>>> book.map(lambda a: a.holder_name.upper()):")
    print(f"  {book.map(lambda a: a.holder_name.upper())}")

    # --- фабрика функций ---
    is_rich = make_richer_than(1000)
    rich_book = book.filter_by(is_rich)
    print(f"\n>>> book.filter_by(make_richer_than(1000)) — {len(rich_book)} счёт(ов):")
    for acc in rich_book: print(f"  {to_summary(acc)}")

    in_range = make_rate_in_range(5, 10)
    print(f"\n>>> filter_by(make_rate_in_range(5, 10)):")
    for acc in book.filter_by(in_range):
        print(f"  ставка {acc.interest_rate:.1f}%: {to_summary(acc)}")

    # --- именованная функция vs lambda — результат одинаковый ---
    by_lambda = sorted(book, key=lambda a: a.balance)
    by_function = sorted(book, key=by_balance)
    print(f"\n>>> lambda и by_balance дают один и тот же порядок: "
          f"{[a.account_number for a in by_lambda] == [a.account_number for a in by_function]}")

    # -------------------------------------------------------------
    header("Сценарий 3. Цепочка filter → sort → apply + замена стратегии")
    # -------------------------------------------------------------
    book = build_book()
    book[4].deactivate()  # один заблокированный, чтоб фильтр имел смысл

    # вот ОНА — цепочка операций. filter_by даёт новую коллекцию,
    # sort_by сортирует её, apply прогоняет функцию по элементам
    print(">>> цепочка filter_by(is_active).sort_by(by_balance).apply(InterestStrategy(2)):")
    result = (book
              .filter_by(is_active)
              .sort_by(by_balance)
              .apply(InterestStrategy(bonus_percent=2)))
    print(f"  результат — {len(result)} счёт(ов), отсортированных по балансу,")
    print(f"  на каждом начислены проценты с бонусом +2%:")
    for acc in result:
        print(f"  {to_summary(acc)}")

    # --- замена стратегии без изменения кода коллекции ---
    print("\n>>> та же цепочка, но вместо InterestStrategy — DiscountStrategy(0.1):")
    book2 = build_book()
    discounted = (book2
                  .filter_by(is_active)
                  .sort_by(by_balance)
                  .apply(DiscountStrategy(0.1)))
    for acc in discounted:
        print(f"  {to_summary(acc)}")

    # коллекции код один и тот же, поведение разное — потому что стратегия другая.
    # это и есть смысл паттерна Стратегия

    # --- callable-объект как стратегия ---
    print("\n>>> DiscountStrategy сам по себе вызывается как функция:")
    cut = DiscountStrategy(0.5)
    one_account = BankAccount(make_num("0099"), "Тест Тестов", 1000, 0)
    print(f"  до:    {one_account.balance:.2f}")
    cut(one_account)   # тыкаем экземпляр класса, он работает как функция
    print(f"  после: {one_account.balance:.2f}")
    print(f"  repr:  {cut!r}")

    af = [1, 2, 3]
    af = list(filter(lambda x: x > 1, af))  # коллекция может быть любой, если у неё есть нужные методы
    print(af)
    

if __name__ == "__main__":
    main()
