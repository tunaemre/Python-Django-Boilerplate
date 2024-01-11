from typing import Tuple, Any

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from app.infrastructure.entity.base.base_model import BaseModel, BaseEnum


# Create models here

class TodoList(BaseModel):
    name = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="todo_lists")
    status = models.ForeignKey('todo_list.TodoListStatus', on_delete=models.PROTECT)

    def __repr__(self) -> str:
        return f'{self.name} <{self.pk}>'

    class Meta:
        ordering: Tuple[str] = ('-created_date',)


class TodoListStatus(BaseEnum):
    pass


# Observe django model signals
# https://docs.djangoproject.com/en/4.1/ref/signals/

@receiver(post_save, sender=TodoList)
def todo_list_post_save(sender: Any, instance: TodoList, **kwargs: Any) -> None:
    from app.infrastructure.repository.todo_list.todo_list_repository import TodoListRepository
    TodoListRepository.on_todo_list_commit(instance)


@receiver(post_delete, sender=TodoList)
def todo_list_post_delete(sender: Any, instance: TodoList, **kwargs: Any) -> None:
    from app.infrastructure.repository.todo_list.todo_list_repository import TodoListRepository
    TodoListRepository.on_todo_list_commit(instance)
