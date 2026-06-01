"""
TypedCollection[T] — копия из ЛР-6, чтоб лаба запускалась автономно.

Тут без протоколов — для ЛР-7 нам хватит обобщённого контейнера, в нём
живут счета. Find/filter/map оставлены, в app.py они дёргаются.
"""

from __future__ import annotations

from typing import Generic, TypeVar, Callable, Optional


T = TypeVar("T")
R = TypeVar("R")


class TypedCollection(Generic[T]):
    """Типизированная коллекция произвольных объектов типа T."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def add(self, item: T) -> None:
        self._items.append(item)

    def remove(self, item: T) -> None:
        self._items.remove(item)

    def get_all(self) -> list[T]:
        # копию отдаём — чтоб снаружи внутреннее состояние не лапали
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __contains__(self, item: object) -> bool:
        return item in self._items

    def find(self, predicate: Callable[[T], bool]) -> Optional[T]:
        """Первый подходящий элемент или None."""
        for item in self._items:
            if predicate(item):
                return item
        return None

    def filter(self, predicate: Callable[[T], bool]) -> list[T]:
        """Все подходящие элементы — обычный list[T]."""
        return [item for item in self._items if predicate(item)]

    def map(self, transform: Callable[[T], R]) -> list[R]:
        """Применить transform к каждому, вернуть list[R]."""
        return [transform(item) for item in self._items]
