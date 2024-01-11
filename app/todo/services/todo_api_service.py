from typing import Any, Union, Optional
from uuid import UUID

from django.db.models import QuerySet

from app.infrastructure.enum.todo.todo_statuses import TodoStatuses
from app.infrastructure.mixin.user_mixin import UserMixin
from app.infrastructure.repository.todo.todo_repository import TodoRepository
from app.todo.models import Todo


class TodoApiService(UserMixin):

    @property
    def queryset(self) -> QuerySet:
        if self.user.is_authenticated:
            return TodoRepository.default_queryset.filter(user_id=self.user.pk)
        else:
            return TodoRepository.none_queryset

    def get_todo_from_cache(self, todo_id: Union[str, UUID]) -> Optional[Todo]:
        """
        Try to get object from cache belongs to user.
        :return: Cached object
        """
        return TodoRepository.lookup_from_cache(user_id=self.user_id, todo_id=todo_id)

    def save_todo_in_cache(self, instance: Todo) -> None:
        """
        Save instance into cache belongs to user.
        :return: Cached object
        """
        return TodoRepository.save_in_cache(instance)

    def create_todo(self, **kwargs: Any) -> Todo:
        """
        Create a new object belongs to user.
        :return: Created object
        """
        return TodoRepository.create(user_id=self.user_id, **kwargs)

    def update_todo(self, instance: Todo, **kwargs: Any) -> Todo:
        """
        Update an object belongs to user.
        :return: Updated object
        """
        return TodoRepository.update(instance=instance, user_id=self.user_id, **kwargs)

    def delete_todo(self, todo_id: Union[str, UUID]) -> None:
        """
        Soft delete an existing object

        :param todo_id: ID of object
        """
        TodoRepository.user_update_status(user_id=self.user_id, todo_id=todo_id, status=TodoStatuses.deleted)
