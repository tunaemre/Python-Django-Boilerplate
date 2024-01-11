import logging
from typing import Dict


class StaticFieldsFilter(logging.Filter):
    """
    Python logging filter that inserts static fields into logging record.
    """

    def __init__(self, fields: Dict[str, str]) -> None:
        super().__init__()
        self._fields = fields

    def filter(self, record: logging.LogRecord) -> bool:
        for k, v in self._fields.items():
            setattr(record, k, v)
        return True


class RequestFilter(logging.Filter):
    """
    Python logging filter that removes the (non-pickable) Django request object from the logging record.
    """

    def filter(self, record) -> bool:
        if hasattr(record, 'request'):
            del record.request
        return True
