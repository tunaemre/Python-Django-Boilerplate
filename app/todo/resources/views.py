from typing import Union, Any
from uuid import UUID

from django.db.models import QuerySet
from django.utils.functional import SimpleLazyObject
from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from app.infrastructure.mixin.cache_model_mixin import CacheModelMixin
from app.security.permission.todo_permission import TodoPermission
from app.todo.models import Todo
from app.todo.resources.serializers import TodoSerializer
from app.todo.services.todo_api_service import TodoApiService


class TodoViewSet(CacheModelMixin, viewsets.ModelViewSet):
    serializer_class = TodoSerializer
    service: TodoApiService = SimpleLazyObject(TodoApiService)  # type: ignore
    permission_classes = [TodoPermission]

    def get_queryset(self) -> QuerySet:
        return self.service.queryset

    def get_cache_object(self, model_id: Union[str, UUID]) -> Any:
        return self.service.get_todo_from_cache(todo_id=model_id)

    def set_cache_object(self, model: Any) -> None:
        self.service.save_todo_in_cache(instance=model)

    def perform_create(self, serializer: BaseSerializer[Todo]):
        serializer.instance = self.service.create_todo(
            **serializer.validated_data)

    def perform_update(self, serializer: BaseSerializer[Todo]):
        assert serializer.instance
        serializer.instance = self.service.update_todo(
            instance=serializer.instance, **serializer.validated_data
        )

    def perform_destroy(self, instance: Todo) -> None:
        self.service.delete_todo(instance.id)
