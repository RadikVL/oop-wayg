"""
Демка по AccountBook (коллекции счетов).

Сценарии:
  1) добавление, вывод, удаление
  2) поиск, len, итерация, защита от дубликатов
  3) индексация, сортировка, фильтрация (новая коллекция на выходе)

Запуск: python3 demo.py
"""

from model import BankAccount
from collection import AccountBook


def header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def make_account(num_tail, holder, balance=0.0, rate=0.0):
    # хелпер чисто чтоб в demo номера счетов не выглядели как простыня —
    # генерим 20-значный номер по короткому хвосту
    base = "40817810099910000000"
    full = base[: 20 - len(num_tail)] + num_tail
    return BankAccount(full, holder, balance, rate)


def main():
    # -------------------------------------------------------------
    header("Сценарий 1. Добавление, вывод, удаление")
    # -------------------------------------------------------------
    book = AccountBook()
    a1 = make_account("0001", "Иванов Иван", 1000, 5)
    a2 = make_account("0002", "Петров Пётр", 5000, 3)
    a3 = make_account("0003", "Сидоров Сидор", 250, 8)

    book.add(a1)
    book.add(a2)
    book.add(a3)
    print(book)

    print("\nУдаляем счёт Петрова...")
    book.remove(a2)
    print(book)

    # пробуем подсунуть не-BankAccount — должно ругнуться
    print("\nПробуем добавить строку вместо счёта:")
    try:
        book.add("я тут типа счёт")
    except TypeError as e:
        print(f"  TypeError: {e}")

    # -------------------------------------------------------------
    header("Сценарий 2. Поиск, len, for, защита от дубликатов")
    # -------------------------------------------------------------
    book.add(a2)  # вернём его обратно, чтоб дальше было что искать
    book.add(make_account("0004", "Иванов Иван", 700, 2))
    book.add(make_account("0005", "Иванов Иван", 12345, 4))

    print(f"len(book) = {len(book)}")

    found = book.find_by_number(a1.account_number)
    print(f"\nfind_by_number({a1.account_number[-4:]}...) → {found}")

    not_found = book.find_by_number("99999999999999999999")
    print(f"find_by_number(несуществующий) → {not_found}")

    print("\nfind_by_holder('Иванов Иван'):")
    for acc in book.find_by_holder("Иванов Иван"):
        print(f"  {acc}")

    print("\nИтерация for по коллекции:")
    for acc in book:
        print(f"  {acc.account_number} | {acc.balance:.2f}")

    print("\nПопытка добавить дубликат (тот же номер):")
    try:
        book.add(make_account("0001", "Кто-то Другой", 999, 1))
    except ValueError as e:
        print(f"  ValueError: {e}")

    # -------------------------------------------------------------
    header("Сценарий 3. Индексация, сортировка, фильтры")
    # -------------------------------------------------------------
    print(f"book[0]  = {book[0]}")
    print(f"book[-1] = {book[-1]}")

    print("\nСрез book[1:3]:")
    for acc in book[1:3]:
        print(f"  {acc}")

    book.sort_by_balance(reverse=True)
    print("\nПосле sort_by_balance(reverse=True) — по балансу убыв.:")
    for acc in book:
        print(f"  {acc.holder_name:<20} {acc.balance:>10.2f}")

    book.sort_by_holder()
    print("\nПосле sort_by_holder() — по алфавиту:")
    for acc in book:
        print(f"  {acc.holder_name:<20} {acc.balance:>10.2f}")

    # пара счетов заблокирована — потом покажем фильтр
    book[0].deactivate()
    book[1].deactivate()

    active = book.get_active()
    blocked = book.get_blocked()
    rich = book.get_richer_than(1000)
    print(f"\nget_active()  → {len(active)} счёт(ов)")
    print(f"get_blocked() → {len(blocked)} счёт(ов)")
    print(f"get_richer_than(1000) → {len(rich)} счёт(ов):")
    for acc in rich:
        print(f"  {acc}")

    # фильтр возвращает НОВЫЙ AccountBook — оригинал не трогается.
    # это важно: если бы мы фильтровали in-place, потеряли бы данные
    print(f"\nПри этом исходный book как был на {len(book)}, так и остался")

    # удаление по индексу
    print("\nremove_at(0):")
    book.remove_at(0)
    print(f"  теперь в book {len(book)} счёт(ов)")


if __name__ == "__main__":
    main()
