from typing import Any, Union, Optional
from uuid import UUID

from app.infrastructure.enum.todo_list.todo_list_statuses import TodoListStatuses
from app.infrastructure.repository.base.base_repository import BaseRepository
from app.infrastructure.repository.base.cache_repository import CacheRepository
from app.todo_list.models import TodoList


class TodoListRepository(BaseRepository[TodoList], CacheRepository[TodoList]):
    default_queryset = TodoList.objects.exclude(status_id=TodoListStatuses.deleted)
    none_queryset = TodoList.objects.none()

    @staticmethod
    def _cache_key(user_id: Union[str, UUID], model_id: Union[str, UUID]) -> str:
        return f'todo_list:{user_id}:{model_id}'

    @staticmethod
    def create(**kwargs: Any) -> TodoList:
        instance = TodoList.objects.create(**kwargs)
        TodoListRepository.save_in_cache(instance)
        return instance

    @staticmethod
    def update(instance: TodoList, **kwargs: Any) -> TodoList:
        update_fields = []
        for k, v in kwargs.items():
            if hasattr(instance, k):
                setattr(instance, k, v)
                update_fields.append(k)
        instance.save(update_fields=update_fields)
        return instance

    @staticmethod
    def delete(instance: TodoList) -> None:
        instance.status_id = TodoListStatuses.deleted
        instance.save(update_fields=['status'])

    @staticmethod
    def user_update_status(user_id: Union[str, UUID], todo_list_id: Union[str, UUID], status: TodoListStatuses) -> bool:
        result = TodoListRepository.default_queryset.filter(id=todo_list_id, user_id=user_id) \
            .exclude(status_id=status) \
            .update(status_id=status)

        if result > 0:
            TodoListRepository.remove_from_cache(user_id=user_id, todo_list_id=todo_list_id)

        return result > 0

    @staticmethod
    def lookup_from_cache(user_id: Union[str, UUID], todo_list_id: Union[str, UUID]) -> Optional[TodoList]:
        _key = TodoListRepository._cache_key(user_id=user_id, model_id=todo_list_id)
        _cached = TodoListRepository.get_cache(_key)
        if _cached is not None:
            assert isinstance(_cached, TodoList)
        return _cached

    @staticmethod
    def save_in_cache(instance: TodoList) -> None:
        _key = TodoListRepository._cache_key(user_id=instance.user_id, model_id=instance.id)
        TodoListRepository.set_cache(_key, instance)  # type: ignore

    @staticmethod
    def remove_from_cache(user_id: Union[str, UUID], todo_list_id: Union[str, UUID]) -> None:
        _key = TodoListRepository._cache_key(user_id=user_id, model_id=todo_list_id)
        TodoListRepository.invalidate_cache(_key)

    # Model signals observer method
    @staticmethod
    def on_todo_list_commit(instance: TodoList) -> None:
        TodoListRepository.remove_from_cache(user_id=instance.user_id, todo_list_id=instance.id)
