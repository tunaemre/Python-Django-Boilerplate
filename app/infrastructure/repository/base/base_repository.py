import abc
from typing import Generic, Any

from app.infrastructure.repository.base import BaseModelType


class BaseRepository(Generic[BaseModelType]):

    @staticmethod
    @abc.abstractmethod
    def create(**kwargs: Any) -> BaseModelType:
        raise NotImplemented

    @staticmethod
    @abc.abstractmethod
    def update(instance: BaseModelType, **kwargs: Any) -> BaseModelType:
        raise NotImplemented

    @staticmethod
    @abc.abstractmethod
    def delete(instance: BaseModelType) -> None:
        raise NotImplemented
