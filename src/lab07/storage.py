"""
Сохранение/загрузка коллекции счетов в JSON.

Тут чисто сериализация — никакой бизнес-логики. AccountService дёргает
эти функции на старте и на выходе.

JSON-формат: массив объектов, у каждого есть поле "_type" — дискриминатор
типа счёта ("bank" | "credit" | "deposit"). По нему на загрузке решаем,
какой класс инстанцировать. Плюс храним is_active / is_matured, чтоб
состояние не терялось между запусками.

Пример файла:
    [
      {"_type": "bank", "account_number": "...", "holder_name": "...",
       "balance": 100.0, "interest_rate": 5.0, "is_active": true},
      {"_type": "credit", ..., "credit_limit": 10000, "debt": 2000},
      {"_type": "deposit", ..., "term_months": 12, "is_matured": false}
    ]
"""

from __future__ import annotations

import json
import os
from typing import Any

from exceptions import StorageError
from models import BankAccount, CreditAccount, DepositAccount


# ============================================================
# Сериализация: объект → dict
# ============================================================

def _account_to_dict(acc: BankAccount) -> dict[str, Any]:
    """Превращаем счёт в обычный dict под json.dump."""
    base: dict[str, Any] = {
        "account_number": acc.account_number,
        "holder_name": acc.holder_name,
        "balance": acc.balance,
        "interest_rate": acc.interest_rate,
        "is_active": acc.is_active,
    }
    # порядок проверки важен: CreditAccount и DepositAccount — наследники
    # BankAccount, поэтому isinstance(acc, BankAccount) для них тоже True.
    # Сначала проверяем более узкие типы
    if isinstance(acc, CreditAccount):
        base["_type"] = "credit"
        base["credit_limit"] = acc.credit_limit
        base["debt"] = acc.debt
    elif isinstance(acc, DepositAccount):
        base["_type"] = "deposit"
        base["term_months"] = acc.term_months
        base["is_matured"] = acc.is_matured
    else:
        base["_type"] = "bank"
    return base


# ============================================================
# Десериализация: dict → объект
# ============================================================

def _dict_to_account(data: dict[str, Any]) -> BankAccount:
    """Из dict-а восстанавливаем нужный класс по полю _type."""
    kind = data.get("_type")
    if kind is None:
        raise StorageError("В записи нет поля '_type' — не понимаем какой это счёт")

    common = {
        "account_number": data["account_number"],
        "holder_name": data["holder_name"],
        "balance": data["balance"],
        "interest_rate": data["interest_rate"],
    }

    if kind == "bank":
        acc: BankAccount = BankAccount(**common)
    elif kind == "credit":
        acc = CreditAccount(
            **common,
            credit_limit=data["credit_limit"],
            debt=data["debt"],
        )
    elif kind == "deposit":
        acc = DepositAccount(**common, term_months=data["term_months"])
        if data.get("is_matured", False):
            acc.mature()
    else:
        raise StorageError(f"Неизвестный тип счёта в файле: {kind!r}")

    # is_active восстанавливаем последним — чтоб не мешало конструктору
    if not data.get("is_active", True):
        acc.deactivate()

    return acc


# ============================================================
# Публичные функции — save/load
# ============================================================

def save(accounts: list[BankAccount], filepath: str) -> None:
    """Сохранить список счетов в JSON-файл.

    Пишем с indent=2 — чтоб глазами можно было файл прочитать,
    при дебаге это золото. ensure_ascii=False — чтоб кириллица была
    кириллицей, а не \\uXXXX-кашей.
    """
    try:
        payload = [_account_to_dict(acc) for acc in accounts]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
    except (OSError, TypeError) as e:
        # OSError — нет прав, диск битый и т.п. TypeError — внезапно
        # попался несериализуемый объект (на всякий случай)
        raise StorageError(f"Не получилось сохранить в {filepath}: {e}") from e


def load(filepath: str) -> list[BankAccount]:
    """Загрузить счета из JSON-файла.

    Если файла нет — это норма (первый запуск), вернём пустой список,
    никаких ошибок. Если файл есть, но в нём мусор — ругнёмся StorageError,
    пусть юзер разбирается.
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError(f"Файл {filepath} — битый JSON: {e}") from e
    except OSError as e:
        raise StorageError(f"Не получилось прочитать {filepath}: {e}") from e

    if not isinstance(payload, list):
        raise StorageError(f"Ожидали список счетов, а в файле {type(payload).__name__}")

    accounts: list[BankAccount] = []
    for i, item in enumerate(payload):
        if not isinstance(item, dict):
            raise StorageError(f"Запись #{i} — не словарь, не понимаю как её парсить")
        try:
            accounts.append(_dict_to_account(item))
        except (KeyError, ValueError) as e:
            # KeyError — нет обязательного поля; ValueError — валидаторы
            # из models.py ругнулись на содержимое
            raise StorageError(f"Запись #{i} битая: {e}") from e
    return accounts
