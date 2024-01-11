import random
from datetime import timedelta

from django.utils import timezone
from model_bakery import baker

from app.infrastructure.enum.todo.todo_statuses import TodoStatuses
from app.infrastructure.enum.todo_list.todo_list_statuses import TodoListStatuses
from app.infrastructure.enum.user.user_statuses import UserStatuses
from app.security.permission import todo_scope, worker_scope
from test.auth_test_case import AuthTestCase, fake_permission


class WorkerViewTestCase(AuthTestCase):
    expired_todos_url = '/api/v1/worker/expired/'

    @fake_permission(todo_scope.write)  # Invalid permission for worker
    def test_list_todos_forbidden_case(self):
        response = self.client.put(self.expired_todos_url)
        self.assertEqual(response.status_code, 403)

    @fake_permission(worker_scope.worker)
    def test_list_todos_empty_case(self):
        _not_expired_quantity = random.randint(5, 10)
        baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.open,
            valid_until=timezone.now() + timedelta(days=random.randint(1, 10)),
            _quantity=_not_expired_quantity)

        response = self.client.put(self.expired_todos_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    @fake_permission(worker_scope.worker)
    def test_list_todos_success_case(self):
        _enabled_user = baker.make('user.User', status_id=UserStatuses.enabled)
        _disabled_user = baker.make('user.User', status_id=UserStatuses.disabled)

        _enabled_user_todo_list = baker.make(
            'todo_list.TodoList', user_id=_enabled_user.id, status_id=TodoListStatuses.open)

        _disabled_user_todo_list = baker.make(
            'todo_list.TodoList', user_id=_disabled_user.id, status_id=TodoListStatuses.open)

        _expired_quantity_of_enabled_user = random.randint(5, 10)
        _not_expired_quantity_of_enabled_user = random.randint(5, 10)

        _expired_quantity_of_disabled_user = random.randint(5, 10)
        _not_expired_quantity_of_disabled_user = random.randint(5, 10)

        _expired_todos = baker.make(
            'todo.Todo', status_id=TodoStatuses.open,
            user_id=_enabled_user.id,
            todo_list_id=_enabled_user_todo_list.pk,
            valid_until=timezone.now() - timedelta(days=random.randint(1, 10)),
            _quantity=_expired_quantity_of_enabled_user)

        baker.make(
            'todo.Todo', status_id=TodoStatuses.open,
            user_id=_enabled_user.id,
            todo_list_id=_enabled_user_todo_list.pk,
            valid_until=timezone.now() + timedelta(days=random.randint(1, 10)),
            _quantity=_not_expired_quantity_of_enabled_user)

        baker.make(
            'todo.Todo', status_id=TodoStatuses.open,
            user_id=_disabled_user.id,
            todo_list_id=_disabled_user_todo_list.pk,
            valid_until=timezone.now() - timedelta(days=random.randint(1, 10)),
            _quantity=_expired_quantity_of_disabled_user)
        baker.make(
            'todo.Todo', status_id=TodoStatuses.open,
            user_id=_disabled_user.id,
            todo_list_id=_disabled_user_todo_list.pk,
            valid_until=timezone.now() + timedelta(days=random.randint(1, 10)),
            _quantity=_not_expired_quantity_of_disabled_user)

        response = self.client.put(self.expired_todos_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), _expired_quantity_of_enabled_user)
        for _todo in response.data:
            self.assertEqual(_todo['user']['email'], _enabled_user.email)

        for _expired_todo in _expired_todos:
            _expired_todo.refresh_from_db()
            self.assertEqual(_expired_todo.status_id, TodoStatuses.expired)

