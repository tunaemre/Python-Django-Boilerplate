from enum import IntEnum


class TodoStatuses(IntEnum):
    open: int = 1
    closed: int = 2
    expired: int = 3
    deleted: int = 4
