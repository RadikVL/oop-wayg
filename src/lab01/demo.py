"""
Демка по BankAccount.

Тут три больших сценария — каждый показывает свою фичу класса:
  1) обычная работа со счётом (создали, пополнили, сняли, проценты)
  2) состояние счёта (заморозили → пробуем дёргать → разморозили)
  3) валидация (через сеттеры и при создании)

Запуск:  python3 demo.py
"""

from model import BankAccount


def header(text):
    # чисто чтоб в консоли каждый сценарий было видно, а не каша
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)


def main():
    # -------------------------------------------------------------
    header("Сценарий 1. Создание счёта и базовые операции")
    # -------------------------------------------------------------
    acc = BankAccount(
        account_number="40817810099910004321",
        holder_name="иванов иван иванович",   # специально с маленькой буквы — посмотрим, как title() это причешет
        balance=1000.0,
        interest_rate=5.0,
    )

    print(acc)                       # дёрнется __str__
    print("\nrepr:", repr(acc))      # дёрнется __repr__

    # пополняем
    acc.deposit(500)
    print(f"\nПосле deposit(500)  баланс = {acc.balance:.2f}")

    # снимаем
    acc.withdraw(200)
    print(f"После withdraw(200) баланс = {acc.balance:.2f}")

    # начислили проценты: 1300 + 5% = 1365
    acc.apply_interest()
    print(f"После apply_interest() баланс = {acc.balance:.2f}")

    # -------------------------------------------------------------
    header("Сценарий 2. Состояние счёта (активен / заблокирован)")
    # -------------------------------------------------------------
    acc.deactivate()
    print("Заблокировали счёт. is_active =", acc.is_active)

    # на замороженном счёте все денежные движухи должны падать с RuntimeError —
    # вот это и проверяем: тычем по очереди и ловим исключения
    for action_name, action in [
        ("deposit(100)",   lambda: acc.deposit(100)),
        ("withdraw(50)",   lambda: acc.withdraw(50)),
        ("apply_interest", lambda: acc.apply_interest()),
    ]:
        try:
            action()
        except RuntimeError as e:
            print(f"  {action_name:<16} → RuntimeError: {e}")

    # размораживаем — снова всё работает
    acc.activate()
    print("\nРазблокировали. is_active =", acc.is_active)
    acc.deposit(100)
    print(f"После deposit(100) баланс = {acc.balance:.2f}")

    # -------------------------------------------------------------
    header("Сценарий 3. Валидация — сеттеры и создание объекта")
    # -------------------------------------------------------------

    # --- сеттер ставки ---
    acc.interest_rate = 7.5
    print(f"Поставили ставку 7.5  → interest_rate = {acc.interest_rate}")
    try:
        acc.interest_rate = 150
    except ValueError as e:
        print(f"  ставка 150       → ValueError: {e}")

    # --- сеттер имени (с авто-причёсыванием) ---
    acc.holder_name = "петров пётр петрович"
    print(f"\nПоменяли имя (с маленькой буквы)  → '{acc.holder_name}'")
    try:
        acc.holder_name = "Иван123"
    except ValueError as e:
        print(f"  имя 'Иван123'    → ValueError: {e}")

    # --- кривые аргументы конструктора ---
    # каждая строчка — своя проверка, чтоб видно было, что валидатор ловит
    # именно ту ошибку, которую ждём, а не падает где попало
    print("\nПроверка валидации в конструкторе:")
    bad_cases = [
        ("пустой номер счёта",
         lambda: BankAccount("", "Иван Иванов", 100, 5)),
        ("номер не 20 цифр",
         lambda: BankAccount("123", "Иван Иванов", 100, 5)),
        ("имя с цифрами",
         lambda: BankAccount("40817810099910004321", "Иван123", 100, 5)),
        ("отрицательный баланс",
         lambda: BankAccount("40817810099910004321", "Иван Иванов", -100, 5)),
        ("ставка > 100",
         lambda: BankAccount("40817810099910004321", "Иван Иванов", 100, 150)),
    ]
    for description, ctor in bad_cases:
        try:
            ctor()
        except ValueError as e:
            print(f"  {description:<22} → ValueError: {e}")

    # --- защита от снятия больше, чем есть ---
    print("\nПопытка снять больше, чем есть на счёте:")
    try:
        acc.withdraw(10 ** 9)
    except ValueError as e:
        print(f"  withdraw(1_000_000_000) → ValueError: {e}")

    # -------------------------------------------------------------
    header("Бонус: сравнение объектов и атрибут класса")
    # -------------------------------------------------------------
    # два счёта с одинаковым номером, но разным содержимым — должны быть равны,
    # ибо __eq__ смотрит чисто на номер счёта
    acc_same_number = BankAccount(
        "40817810099910004321", "Совершенно Другой Человек",
        balance=99999, interest_rate=1,
    )
    acc_other = BankAccount(
        "40817810099910009999", "Иванов Иван Иванович", 0, 0,
    )
    print("acc == acc_same_number (тот же номер счёта)? ->", acc == acc_same_number)
    print("acc == acc_other       (другой номер счёта)? ->", acc == acc_other)

    # к атрибуту класса можно тыкать и через сам класс, и через экземпляр —
    # значение одно и то же, потому что хранится оно на классе
    print("\nBankAccount.bank_name =", BankAccount.bank_name)
    print("acc.bank_name         =", acc.bank_name)


if __name__ == "__main__":
    main()
