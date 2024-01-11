from typing import Union, Any
from uuid import UUID

from django.db.models import QuerySet
from django.utils.functional import SimpleLazyObject
from rest_framework import viewsets
from rest_framework.serializers import BaseSerializer

from app.infrastructure.mixin.cache_model_mixin import CacheModelMixin
from app.infrastructure.mixin.multi_serializer_mixin import MultiSerializerMixin
from app.security.permission.todo_permission import TodoPermission
from app.todo.models import Todo
from app.todo_list.models import TodoList
from app.todo_list.resources.serializers import TodoListSerializer, TodoListDetailSerializer
from app.todo_list.services.todo_list_api_service import TodoListApiService


class TodoListViewSet(MultiSerializerMixin, CacheModelMixin, viewsets.ModelViewSet):
    serializer_class = TodoListSerializer
    action_serializer_classes = {
        'retrieve': TodoListDetailSerializer
    }

    service: TodoListApiService = SimpleLazyObject(TodoListApiService)  # type: ignore
    permission_classes = [TodoPermission]

    def get_queryset(self) -> QuerySet:
        if self.action == 'retrieve':
            return self.service.queryset_detailed
        else:
            return self.service.queryset

    def get_cache_object(self, model_id: Union[str, UUID]) -> Any:
        return self.service.get_todo_list_from_cache(todo_list_id=model_id)

    def set_cache_object(self, model: Any) -> None:
        self.service.save_todo_list_in_cache(instance=model)

    def perform_create(self, serializer: BaseSerializer[TodoList]):
        serializer.instance = self.service.create_todo_list(
            **serializer.validated_data)

    def perform_update(self, serializer: BaseSerializer[TodoList]):
        assert serializer.instance
        serializer.instance = self.service.update_todo_list(
            instance=serializer.instance, **serializer.validated_data
        )

    def perform_destroy(self, instance: Todo) -> None:
        self.service.delete_todo_list(instance.id)
