from typing import Tuple, Any

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from app.infrastructure.entity.base.base_model import BaseModel, BaseEnum


# Create models here

class Todo(BaseModel):
    title = models.CharField(max_length=50, null=False, blank=False)
    description = models.CharField(max_length=255, null=True, blank=True)
    valid_until = models.DateTimeField()
    todo_list = models.ForeignKey('todo_list.TodoList', on_delete=models.CASCADE, related_name="todos")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.ForeignKey('todo.TodoStatus', on_delete=models.PROTECT)

    def __repr__(self) -> str:
        return f'{self.title} <{self.pk}>'

    class Meta:
        ordering: Tuple[str] = ('-created_date',)


class TodoStatus(BaseEnum):
    pass


# Observe django model signals
# https://docs.djangoproject.com/en/4.1/ref/signals/

@receiver(post_save, sender=Todo)
def todo_post_save(sender: Any, instance: Todo, **kwargs: Any) -> None:
    from app.infrastructure.repository.todo.todo_repository import TodoRepository
    TodoRepository.on_todo_commit(instance)


@receiver(post_delete, sender=Todo)
def todo_post_delete(sender: Any, instance: Todo, **kwargs: Any) -> None:
    from app.infrastructure.repository.todo.todo_repository import TodoRepository
    TodoRepository.on_todo_commit(instance)
