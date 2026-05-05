"""
Generic-коллекция и протоколы для типобезопасной работы с объектами.

Что тут:
  - TypedCollection[T] — обобщённая коллекция, типизирована параметром T.
    Та же логика, что в ЛР-2, но теперь IDE и mypy понимают, что
    внутри лежит конкретный тип.
  - Protocol Displayable — кто угодно с методом display() -> str.
  - Protocol Scorable    — кто угодно с методом score() -> float.
  - TypeVar с bound=Protocol — ограничивает T только теми типами,
    что реализуют нужный контракт. Внутри коллекции можно тыкать
    item.display() — и IDE не ругается.

Главная мысль: Protocol — это структурная типизация. Класс не должен
наследоваться от Protocol-а, достаточно чтоб у него был нужный метод.
"""

from typing import Generic, TypeVar, Callable, Optional, Protocol, runtime_checkable


# ============================================================
# Протоколы — контракты "что должен уметь объект"
# ============================================================

@runtime_checkable
class Displayable(Protocol):
    """Объект, умеющий красиво показать себя в виде строки.

    @runtime_checkable нужен, чтоб работала проверка isinstance(obj, Displayable).
    Без неё Protocol проверяется только статически (mypy), а в рантайме нет.
    """

    def display(self) -> str:
        ...


@runtime_checkable
class Scorable(Protocol):
    """Объект, у которого есть численная оценка."""

    def score(self) -> float:
        ...


# ============================================================
# Generic-коллекция
# ============================================================

T = TypeVar("T")
R = TypeVar("R")  # для map() — тип результата может отличаться от T

# отдельные TypeVar-ы с ограничением — для сценариев, где коллекция
# должна работать только с теми, кто реализует протокол
D = TypeVar("D", bound=Displayable)
S = TypeVar("S", bound=Scorable)


class TypedCollection(Generic[T]):
    """Типизированная коллекция произвольных объектов типа T.

    Зачем нужна: обычный список list[Any] про тип ничего не знает.
    А TypedCollection[BankAccount] говорит IDE и mypy:
    "тут только BankAccount-ы, не лезь сюда со строками".
    """

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

    # ---------- find / filter / map ----------

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
        """Применить transform к каждому, вернуть list[R].

        Тип R может отличаться от T — на то и нужен второй TypeVar.
        Например, было TypedCollection[BankAccount], применили
        transform=lambda a: a.holder_name — получили list[str].
        """
        return [transform(item) for item in self._items]
