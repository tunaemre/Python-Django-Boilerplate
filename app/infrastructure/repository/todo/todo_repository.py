from typing import Any, Union, List, Optional
from uuid import UUID

from django.db.transaction import atomic
from django.utils import timezone

from app.infrastructure.enum.todo.todo_statuses import TodoStatuses
from app.infrastructure.enum.todo_list.todo_list_statuses import TodoListStatuses
from app.infrastructure.enum.user.user_statuses import UserStatuses
from app.infrastructure.repository.base.base_repository import BaseRepository
from app.infrastructure.repository.base.cache_repository import CacheRepository
from app.todo.models import Todo


class TodoRepository(BaseRepository[Todo], CacheRepository[Todo]):
    default_queryset = Todo.objects.exclude(status_id=TodoStatuses.deleted)
    none_queryset = Todo.objects.none()

    @staticmethod
    def _cache_key(user_id: Union[str, UUID], model_id: Union[str, UUID]) -> str:
        return f'todo:{user_id}:{model_id}'

    @staticmethod
    def create(**kwargs: Any) -> Todo:
        instance = Todo.objects.create(**kwargs)
        TodoRepository.save_in_cache(instance)
        return instance

    @staticmethod
    def update(instance: Todo, **kwargs: Any) -> Todo:
        update_fields = []
        for k, v in kwargs.items():
            if hasattr(instance, k):
                setattr(instance, k, v)
                update_fields.append(k)
        instance.save(update_fields=update_fields)
        return instance

    @staticmethod
    def delete(instance: Todo) -> None:
        instance.status_id = TodoStatuses.deleted
        instance.save(update_fields=['status'])

    @staticmethod
    def user_update_status(user_id: Union[str, UUID], todo_id: Union[str, UUID], status: TodoStatuses) -> bool:
        result = TodoRepository.default_queryset.filter(id=todo_id, user_id=user_id) \
            .exclude(status_id=status) \
            .update(status_id=status)

        if result > 0:
            TodoRepository.remove_from_cache(user_id=user_id, todo_id=todo_id)

        return result > 0

    @staticmethod
    def worker_update_expired_todos() -> List[Todo]:
        with atomic():
            # Convert queryset to list for eager execution of sql query
            todos = list(Todo.objects.select_related('user', 'todo_list')
                         .filter(status_id=TodoStatuses.open,
                                 valid_until__lt=timezone.now(),
                                 user__status_id=UserStatuses.enabled,
                                 todo_list__status_id=TodoListStatuses.open)
                         .all())

            id_list = []
            for todo in todos:
                id_list.append(todo.id)
                TodoRepository.remove_from_cache(user_id=todo.user_id, todo_id=todo.id)

            Todo.objects.filter(id__in=id_list, status_id=TodoStatuses.open) \
                .update(status_id=TodoStatuses.expired)

            return todos

    @staticmethod
    def lookup_from_cache(user_id: Union[str, UUID], todo_id: Union[str, UUID]) -> Optional[Todo]:
        _key = TodoRepository._cache_key(user_id=user_id, model_id=todo_id)
        _cached = TodoRepository.get_cache(_key)
        if _cached is not None:
            assert isinstance(_cached, Todo)
        return _cached

    @staticmethod
    def save_in_cache(instance: Todo) -> None:
        _key = TodoRepository._cache_key(user_id=instance.user_id, model_id=instance.id)
        TodoRepository.set_cache(_key, instance)  # type: ignore

    @staticmethod
    def remove_from_cache(user_id: Union[str, UUID], todo_id: Union[str, UUID]) -> None:
        _key = TodoRepository._cache_key(user_id=user_id, model_id=todo_id)
        TodoRepository.invalidate_cache(_key)

    # Model signals observer method
    @staticmethod
    def on_todo_commit(instance: Todo) -> None:
        TodoRepository.remove_from_cache(user_id=instance.user_id, todo_id=instance.id)
