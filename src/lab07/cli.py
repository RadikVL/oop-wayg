"""
CLI-слой: меню, ввод, вывод. И ничего больше.

Жёсткое правило: тут вообще нет импортов из models / container / storage.
Всё, что нужно про устройство счетов — берётся из app: фабрики
(create_basic / create_credit / create_deposit), вью-функция account_view
и константы ACCOUNT_KINDS / SORT_STRATEGIES. Это позволяет завтра
поменять модели или хранилище и не лазить сюда.

Если юзер ввёл фигню — отлавливаем тут же, выводим понятный текст,
возвращаемся в меню. До app.py долетают только валидные по форме данные
(само содержание уже валидируется в моделях / сервисе).
"""

from __future__ import annotations

from typing import Any, Callable

from app import ACCOUNT_KINDS, AccountService, SORT_STRATEGIES, account_view
from exceptions import (
    AccountError,
    AccountNotFoundError,
    DuplicateAccountError,
    OperationCancelled,
)


# ============================================================
# Помогаторы для ввода (приватные)
# ============================================================

def _ask(prompt: str) -> str:
    """Спросить строку. EOF (Ctrl-D) трактуем как 'отмена'.

    Это удобно когда юзер в середине диалога понял что не туда полез —
    жмёт Ctrl-D, его выкидывает в главное меню.
    """
    try:
        return input(prompt).strip()
    except EOFError:
        raise OperationCancelled("Ввод прерван")


def _ask_int(prompt: str) -> int:
    raw = _ask(prompt)
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"Ожидалось целое число, получено: {raw!r}")


def _ask_float(prompt: str) -> float:
    raw = _ask(prompt)
    try:
        # запятую тоже принимаем — юзеру так удобней
        return float(raw.replace(",", "."))
    except ValueError:
        raise ValueError(f"Ожидалось число, получено: {raw!r}")


def _confirm(prompt: str) -> None:
    """Подтверждение опасной операции. 'нет' → OperationCancelled."""
    answer = _ask(f"{prompt} (y/n): ").lower()
    if answer not in ("y", "yes", "д", "да"):
        raise OperationCancelled("Отменено пользователем")


def _pick_kind_code(prompt_title: str) -> str:
    """Спросить тип счёта пунктом меню. Возвращает код из ACCOUNT_KINDS.

    Меню рисуется по ACCOUNT_KINDS — добавится новый тип в app, тут
    ничего менять не надо.
    """
    print(f"\n{prompt_title}")
    codes = list(ACCOUNT_KINDS.keys())
    for i, code in enumerate(codes, start=1):
        print(f"  {i}. {ACCOUNT_KINDS[code]}")
    idx = _ask_int("Выбор: ")
    if not (1 <= idx <= len(codes)):
        raise ValueError(f"Нет такого варианта: {idx}")
    return codes[idx - 1]


# ============================================================
# Форматированный вывод (таблица)
# ============================================================

def _print_table(accounts: list[Any]) -> None:
    """Аккуратная таблица счетов. Если пусто — так и говорим.

    Тип в аннотации — Any, потому что cli.py намеренно не импортирует
    BankAccount. Рендерим через account_view из app — получаем dict
    с понятными ключами, и больше про устройство счёта тут знать
    ничего не надо.
    """
    if not accounts:
        print("  (счетов нет)")
        return

    # колонки фиксированной ширины — для глаз приятней, чем pretty-print
    header = f"  {'№ счёта':<22} {'Тип':<11} {'Владелец':<22} {'Баланс':>14}  Статус"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for acc in accounts:
        row = account_view(acc)
        status = "активен" if row["active"] else "блок"
        print(f"  {row['number']:<22} {row['kind']:<11} "
              f"{row['holder']:<22} {row['balance']:>12.2f} р.  {status}")
        # вторая строка с деталями подтипа — если app решил, что она нужна
        if row["extra"] is not None:
            print(f"  {'':<22} {'':<11} {row['extra']}")


# ============================================================
# Команды меню
# ============================================================

def _cmd_show_all(service: AccountService) -> None:
    print(f"\nВсего счетов: {service.count()}")
    _print_table(service.all())


def _cmd_add(service: AccountService) -> None:
    code = _pick_kind_code("Какой тип счёта добавляем?")

    number = _ask("Номер счёта (20 цифр): ")
    holder = _ask("Имя владельца: ")
    balance = _ask_float("Стартовый баланс: ")
    rate = _ask_float("Процентная ставка (0..100): ")

    # фабрики живут в сервисе — cli про конструкторы моделей не знает
    if code == "bank":
        acc = service.create_basic(number, holder, balance, rate)
    elif code == "credit":
        limit = _ask_float("Кредитный лимит: ")
        debt = _ask_float("Текущий долг: ")
        acc = service.create_credit(number, holder, balance, rate, limit, debt)
    elif code == "deposit":
        term = _ask_int("Срок вклада (мес.): ")
        acc = service.create_deposit(number, holder, balance, rate, term)
    else:
        # _pick_kind_code сюда такое не пропустит, но на всякий
        raise ValueError(f"Неизвестный код типа: {code!r}")

    print(f"  → счёт {acc.account_number} ({ACCOUNT_KINDS[code]}) добавлен")


def _cmd_find(service: AccountService) -> None:
    number = _ask("\nНомер счёта для поиска: ")
    acc = service.get(number)
    print("Нашли:")
    _print_table([acc])


def _cmd_filter_by_kind(service: AccountService) -> None:
    code = _pick_kind_code("Фильтр по типу:")
    result = service.filter_by_kind(code)
    print(f"Найдено: {len(result)}")
    _print_table(result)


def _cmd_filter_by_balance(service: AccountService) -> None:
    lo = _ask_float("\nМинимальный баланс: ")
    hi = _ask_float("Максимальный баланс: ")
    # проверка lo > hi теперь живёт в service.filter_by_balance —
    # это бизнес-правило, а не валидация ввода
    result = service.filter_by_balance(lo, hi)
    print(f"Найдено: {len(result)} (баланс в [{lo:.2f}; {hi:.2f}])")
    _print_table(result)


def _cmd_sort(service: AccountService) -> None:
    print("\nСортировать по:")
    names = list(SORT_STRATEGIES.keys())
    for i, name in enumerate(names, start=1):
        print(f"  {i}. {name}")
    idx = _ask_int("Выбор: ")
    if not (1 <= idx <= len(names)):
        raise ValueError(f"Нет такого варианта: {idx}")
    direction = _ask("По возрастанию или убыванию? (asc/desc): ").lower()
    if direction not in ("asc", "desc"):
        raise ValueError(f"Ожидалось 'asc' или 'desc', получено: {direction!r}")
    result = service.sorted_by(names[idx - 1], reverse=(direction == "desc"))
    print(f"Отсортировано: {names[idx - 1]} ({direction})")
    _print_table(result)


def _cmd_deposit_withdraw(service: AccountService) -> None:
    print("\n1. Пополнить")
    print("2. Снять")
    choice = _ask("Выбор: ")
    if choice not in ("1", "2"):
        raise ValueError(f"Нет такого варианта: {choice!r}")
    number = _ask("Номер счёта: ")
    amount = _ask_float("Сумма: ")
    if choice == "1":
        service.deposit(number, amount)
        print(f"  → пополнили на {amount:.2f}")
    else:
        service.withdraw(number, amount)
        print(f"  → сняли {amount:.2f}")


def _cmd_remove(service: AccountService) -> None:
    number = _ask("\nНомер счёта для удаления: ")
    # сначала находим — чтоб в подтверждении показать кого именно прибиваем
    acc = service.get(number)
    print("Будет удалён:")
    _print_table([acc])
    _confirm(f"Удалить счёт №{number}?")
    service.remove(number)
    print("  → удалили")


def _cmd_save_now(service: AccountService, save_callback: Callable[[], None]) -> None:
    save_callback()
    print(f"\n  → сохранено ({service.count()} счёт(ов))")


# ============================================================
# Главный цикл
# ============================================================

def _print_menu() -> None:
    print("\n" + "=" * 50)
    print("  Меню")
    print("=" * 50)
    print("  1. Показать все счета")
    print("  2. Добавить счёт")
    print("  3. Найти по номеру")
    print("  4. Фильтр по типу")
    print("  5. Фильтр по балансу")
    print("  6. Сортировка (выбор стратегии)")
    print("  7. Пополнить / снять")
    print("  8. Удалить счёт")
    print("  9. Сохранить сейчас")
    print("  0. Выход")


def run(service: AccountService, save_callback: Callable[[], None]) -> None:
    """Запустить главный цикл CLI.

    save_callback — функция без аргументов, по которой сохраняем
    состояние. Сюда её прокидывает main.py, тут мы про файлы ничего
    не знаем (правильное разделение слоёв).
    """
    print("=" * 50)
    print("  Банковская система — консоль (ЛР-7)")
    print("=" * 50)
    print(f"Стартовая загрузка: в коллекции {service.count()} счёт(ов)")

    # таблица команд — чтоб не лепить громадный if/elif
    commands: dict[str, Callable[[], None]] = {
        "1": lambda: _cmd_show_all(service),
        "2": lambda: _cmd_add(service),
        "3": lambda: _cmd_find(service),
        "4": lambda: _cmd_filter_by_kind(service),
        "5": lambda: _cmd_filter_by_balance(service),
        "6": lambda: _cmd_sort(service),
        "7": lambda: _cmd_deposit_withdraw(service),
        "8": lambda: _cmd_remove(service),
        "9": lambda: _cmd_save_now(service, save_callback),
    }

    while True:
        _print_menu()
        try:
            choice = _ask("Выберите пункт: ")
        except OperationCancelled:
            # Ctrl-D в самом меню — корректный выход
            print("\nПока!")
            return

        if choice == "0":
            print("\nПока!")
            return

        cmd = commands.get(choice)
        if cmd is None:
            print(f"Ошибка: нет пункта {choice!r}, выбери из меню")
            continue

        # ловим всё, что может вылететь из команды. Своё — отдельно
        # с понятным текстом; ValueError — это валидация в моделях или
        # числовой ввод; всё остальное — пусть всплывает (это уже баг)
        try:
            cmd()
        except OperationCancelled as e:
            print(f"  ← {e}")
        except (AccountNotFoundError, DuplicateAccountError) as e:
            # эти исключения сами знают человеческий текст
            print(f"Ошибка: {e}")
        except AccountError as e:
            # ловушка под все остальные наши — на случай если ещё добавим
            print(f"Ошибка предметки: {e}")
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
        except RuntimeError as e:
            # счёт заблокирован и т.п.
            print(f"Ошибка: {e}")
