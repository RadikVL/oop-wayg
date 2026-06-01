"""
Свои исключения предметки.

Зачем вообще: ловить ValueError из чужого кода — стрёмно, потому что
ValueError кидают все кому не лень. А вот AccountNotFoundError — это уже
наш конкретный кейс, по нему точно понятно что произошло.

Базовый AccountError — чтоб можно было одним except-ом поймать всё своё,
если припрёт.
"""


class AccountError(Exception):
    """База для всех наших ошибок — удобно ловить пачкой."""


class AccountNotFoundError(AccountError):
    """Счёта с таким номером в коллекции нет."""

    def __init__(self, account_number: str) -> None:
        super().__init__(f"Счёт №{account_number} не найден")
        self.account_number = account_number


class DuplicateAccountError(AccountError):
    """Счёт с таким номером уже лежит в коллекции."""

    def __init__(self, account_number: str) -> None:
        super().__init__(f"Счёт №{account_number} уже существует")
        self.account_number = account_number


class StorageError(AccountError):
    """Что-то пошло не так при сохранении/загрузке (битый JSON, нет прав и т.д.)."""


class OperationCancelled(AccountError):
    """Юзер сказал 'нет' на подтверждение опасной операции.

    Это не совсем ошибка, скорее сигнал «прервать без шума». Делаем
    исключением, чтоб удобно было всплыть из глубины ввода до меню.
    """
