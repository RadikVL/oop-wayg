# ЛР-6 — Generics и typing

## 1. Цель работы

- Освоить аннотации типов (`typing`) и расставить их в существующем коде.
- Создать обобщённый (generic) контейнер с `TypeVar` и `Generic`.
- Понять структурную типизацию через `typing.Protocol`.

## 2. Описание реализованных типов и контейнеров

### Аннотации типов в модели

В `model.py` все классы и методы аннотированы — параметры конструктора,
возвращаемые значения, типы атрибутов в `__init__`. Например:

```python
class BankAccount:
    bank_name: str = "z-bank_ZOV_GOYDA"

    def __init__(self, account_number: str, holder_name: str,
                 balance: float = 0.0, interest_rate: float = 0.0) -> None:
        self._account_number: str = ...
        ...
```

### `TypedCollection[T]` (`container.py`)

Generic-контейнер, типизированный параметром `T`:

```python
T = TypeVar("T")

class TypedCollection(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
```

Реализованы методы:

| Метод                                                  | Сигнатура                                |
| ------------------------------------------------------ | ---------------------------------------- |
| `add(item)`, `remove(item)`, `get_all()`               | базовая работа с `T`                     |
| `__len__`, `__iter__`, `__getitem__`, `__contains__`   | стандартные dunder-ы                     |
| `find(predicate) -> Optional[T]`                       | первый подходящий или `None`             |
| `filter(predicate) -> list[T]`                         | все подходящие                           |
| `map(transform) -> list[R]`                            | преобразование с другим TypeVar `R`      |

Второй TypeVar `R` нужен в `map`, потому что результат преобразования
может быть любого типа. Из `TypedCollection[BankAccount]` через
`map(lambda a: a.holder_name)` получаем `list[str]`, через
`map(lambda a: a.balance)` — `list[float]`.

### Protocol-ы (`container.py`)

```python
@runtime_checkable
class Displayable(Protocol):
    def display(self) -> str: ...

@runtime_checkable
class Scorable(Protocol):
    def score(self) -> float: ...
```

`@runtime_checkable` нужен, чтобы работало `isinstance(obj, Displayable)`
в рантайме. Без него `Protocol` проверяется только статически (`mypy`).

Классы `BankAccount` / `CreditAccount` / `DepositAccount` **не
наследуются** от `Displayable` или `Scorable`. У них просто есть методы
`display()` и `score()`. Этого достаточно — структурная типизация
сравнивает по интерфейсу, а не по родословной.

Реализация `score()` у разных классов:

| Класс            | `score()` возвращает                                       |
| ---------------- | ---------------------------------------------------------- |
| `BankAccount`    | `balance`                                                  |
| `CreditAccount`  | `balance - debt` (реальная чистая стоимость, может быть < 0) |
| `DepositAccount` | `balance` плюс прогноз процентов до конца срока            |

### TypeVar с ограничением

```python
D = TypeVar("D", bound=Displayable)
S = TypeVar("S", bound=Scorable)
```

Теперь `TypedCollection[D]` — это коллекция не «чего угодно», а только
тех объектов, у которых есть метод `display()`. Внутри коллекции (и в
коде, который её использует) можно безопасно вызывать `item.display()`.

## 3. Демонстрация работы

В `demo.py` три сценария.

**Сценарий 1.** `TypedCollection[BankAccount]`. Показаны базовые
операции, плюс:
- `find()` — один раз нашли, один раз получили `None`;
- `filter()` — отфильтрованный список;
- `map()` дважды с разными функциями: `list[str]` (имена) и `list[float]`
  (балансы) — наглядно видно, зачем второй TypeVar `R`.

**Сценарий 2.** `TypedCollection[Displayable]` с объектами разных
типов из иерархии. Видно, что:
- классы `BankAccount`, `CreditAccount`, `DepositAccount` **не
  наследуются** от `Displayable`, но `isinstance(obj, Displayable) == True`
  для каждого;
- единый цикл вызывает `item.display()` для всех — у каждого свой формат.

**Сценарий 3.** Тот же `TypedCollection`, но параметризован
протоколом `Scorable`. `score()` считается по-разному в каждом классе,
и коллекция сортируется по этому методу. Видно, что один и тот же
generic-контейнер работает с разными ограничениями.

> Скриншоты — в `images/lab06/`.

![Сценарий 1](../../images/lab06/scenario1.png)
![Сценарий 2](../../images/lab06/scenario2.png)
![Сценарий 3](../../images/lab06/scenario3.png)

## 4. Вывод

- Аннотации типов делают код документированным «бесплатно»: видно, что
  принимает функция и что возвращает, без чтения тела.
- `Generic[T]` + `TypeVar` дают переиспользуемый контейнер, который
  работает с любым типом, но при этом сохраняет типобезопасность.
- Второй TypeVar (`R` в `map`) нужен, когда тип результата отличается
  от типа исходных элементов.
- `Protocol` решает классическую проблему наследования: не надо тащить
  чужой класс в иерархию, чтобы реализовать «интерфейс». Достаточно
  просто иметь нужный метод. Это структурная типизация в чистом виде.
- Связка `TypeVar(bound=Protocol)` — самое мощное средство:
  generic-контейнер с гарантией, что внутри лежат объекты с конкретными
  методами.
