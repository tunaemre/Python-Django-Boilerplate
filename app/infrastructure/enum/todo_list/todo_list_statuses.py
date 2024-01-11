from enum import IntEnum


class TodoListStatuses(IntEnum):
    open: int = 1
    closed: int = 2
    deleted: int = 3
