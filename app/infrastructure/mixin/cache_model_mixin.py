from typing import Any, Union
from uuid import UUID

from rest_framework.mixins import RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class CacheModelMixin:
    """
    Try to retrieve a model instance from cache.
    """

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        assert isinstance(self, RetrieveModelMixin) and isinstance(self, GenericViewSet), \
            'CacheModelMixin could only used in RetrieveModelMixin and GenericViewSet.'

        _id = kwargs.get('pk') or kwargs.get('id')
        if _id:
            if cached := self.get_cache_object(_id):
                serializer = self.get_serializer(cached)
                return Response(serializer.data)

        _instance = self.get_object()
        if _instance is not None:
            self.set_cache_object(_instance)
        serializer = self.get_serializer(_instance)
        return Response(serializer.data)

    def get_cache_object(self, model_id: Union[str, UUID]) -> Any:
        raise NotImplemented

    def set_cache_object(self, model: Any) -> None:
        raise NotImplemented
