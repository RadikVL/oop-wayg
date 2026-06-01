"""
Точка входа. Запускать так:

    cd src/lab07
    python3 main.py

Что делает:
  1. На старте — пытается загрузить data.json (рядом с этим файлом).
     Файла нет → стартуем с пустой коллекцией, это норма.
  2. Запускает CLI-цикл (см. cli.py).
  3. На выходе (и через "Выход" из меню, и через Ctrl-C) — сохраняет
     текущее состояние обратно в data.json. Если упало в сохранении —
     честно говорим, не молчим в тряпочку.
"""

from __future__ import annotations

import os
import sys

import cli
import storage
from app import AccountService
from exceptions import StorageError


# data.json кладём рядом с main.py, а не в cwd — чтоб независимо от того,
# откуда запустили (cd src/lab07/ или из корня проекта), файл был там же
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")


def main() -> int:
    service = AccountService()

    # --- автозагрузка ---
    try:
        loaded = storage.load(DATA_FILE)
        service.load_from(loaded)
        if loaded:
            print(f"[storage] загрузил {len(loaded)} счёт(ов) из {DATA_FILE}")
        else:
            print(f"[storage] файла нет или он пустой — стартуем с чистого листа")
    except StorageError as e:
        # битый файл — не стартуем, мало ли что юзер туда положил.
        # Лучше пусть руками разберётся, чем мы данные затрём пустотой
        print(f"[storage] ОШИБКА: {e}")
        print("[storage] чтобы не затереть файл случайно — выходим. Поправь JSON и запусти снова")
        return 1

    # --- callback для ручного сохранения из меню ---
    def save_now() -> None:
        storage.save(service.all(), DATA_FILE)

    # --- основной цикл ---
    try:
        cli.run(service, save_now)
    except KeyboardInterrupt:
        # Ctrl-C — тоже нормальный выход, не падаем стектрейсом
        print("\n[main] прервано Ctrl-C")

    # --- автосохранение на выход ---
    try:
        storage.save(service.all(), DATA_FILE)
        print(f"[storage] сохранено в {DATA_FILE} ({service.count()} счёт(ов))")
    except StorageError as e:
        print(f"[storage] не удалось сохранить: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
