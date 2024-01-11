from typing import List

from app.infrastructure.repository.todo.todo_repository import TodoRepository
from app.todo.models import Todo


class WorkerService:

    def update_expired_todos(self) -> List[Todo]:
        """
        Soft delete an existing object
        """
        return TodoRepository.worker_update_expired_todos()
