from typing import Any, Union, Optional
from uuid import UUID

from django.db.models import QuerySet, Prefetch

from app.infrastructure.enum.todo_list.todo_list_statuses import TodoListStatuses
from app.infrastructure.mixin.user_mixin import UserMixin
from app.infrastructure.repository.todo.todo_repository import TodoRepository
from app.infrastructure.repository.todo_list.todo_list_repository import TodoListRepository
from app.todo_list.models import TodoList


class TodoListApiService(UserMixin):

    @property
    def queryset(self) -> QuerySet:
        if self.user.is_authenticated:
            return TodoListRepository.default_queryset.filter(user_id=self.user.pk)
        else:
            return TodoListRepository.none_queryset

    @property
    def queryset_detailed(self) -> QuerySet:
        if self.user.is_authenticated:
            return TodoListRepository.default_queryset.filter(user_id=self.user.pk) \
                .prefetch_related(Prefetch('todos', queryset=TodoRepository.default_queryset))
        else:
            return TodoListRepository.none_queryset

    def get_todo_list_from_cache(self, todo_list_id: Union[str, UUID]) -> Optional[TodoList]:
        """
        Try to get object from cache belongs to user.
        :return: Cached object
        """
        return TodoListRepository.lookup_from_cache(user_id=self.user_id, todo_list_id=todo_list_id)

    def save_todo_list_in_cache(self, instance: TodoList) -> None:
        """
        Save instance into cache belongs to user.
        :return: Cached object
        """
        return TodoListRepository.save_in_cache(instance)

    def create_todo_list(self, **kwargs: Any) -> TodoList:
        """
        Create a new object belongs to user.
        :return: Created object
        """
        return TodoListRepository.create(user_id=self.user_id, **kwargs)

    def update_todo_list(self, instance: TodoList, **kwargs: Any) -> TodoList:
        """
        Update an object belongs to user.
        :return: Updated object
        """
        return TodoListRepository.update(instance=instance, user_id=self.user_id, **kwargs)

    def delete_todo_list(self, todo_list_id: Union[str, UUID]) -> None:
        """
        Soft delete an existing object

        :param todo_list_id: ID of object
        """
        TodoListRepository.user_update_status(user_id=self.user_id,
                                              todo_list_id=todo_list_id,
                                              status=TodoListStatuses.deleted)
