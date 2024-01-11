import random
from datetime import timedelta

from django.utils import timezone
from model_bakery import baker

from app.infrastructure.enum.todo.todo_statuses import TodoStatuses
from app.infrastructure.enum.todo_list.todo_list_statuses import TodoListStatuses
from app.infrastructure.enum.user.user_statuses import UserStatuses
from app.infrastructure.repository.todo.todo_repository import TodoRepository
from app.security.permission import todo_scope
from test.auth_test_case import AuthTestCase, fake_permission


class TodoViewTestCase(AuthTestCase):
    todos_url = '/api/v1/todo/'
    todo_detail_url = '/api/v1/todo/{id}/'

    @fake_permission(todo_scope.write)  # Invalid permission for read
    def test_list_todos_forbidden_case(self):
        response = self.client.get(self.todos_url)
        self.assertEqual(response.status_code, 403)

    @fake_permission(todo_scope.read)
    def test_list_todos_empty_case(self):
        response = self.client.get(self.todos_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    @fake_permission(todo_scope.read)
    def test_list_todos_success_case(self):
        _active_quantity = random.randint(5, 10)
        _deleted_quantity = random.randint(5, 10)
        _other_user_quantity = random.randint(5, 10)

        baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.open,
            _quantity=_active_quantity)
        baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.deleted,
            _quantity=_deleted_quantity)

        _other_user = baker.make('user.User', status_id=UserStatuses.enabled)
        baker.make(
            'todo.Todo', user_id=_other_user.id, status_id=TodoStatuses.open,
            _quantity=_other_user_quantity)

        response = self.client.get(self.todos_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), _active_quantity)

    @fake_permission(todo_scope.read)  # Invalid permission for write
    def test_create_todo_forbidden_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.post(self.todos_url,
                                    content_type='application/json',
                                    data={
                                        'title': 'Test Title',
                                        'description': 'Test Description',
                                        'valid_until': timezone.now() + timedelta(days=random.randint(1, 10)),
                                        'todo_list': _todo_list.pk,
                                        'status': TodoStatuses.open
                                    })
        self.assertEqual(response.status_code, 403)
        _todo_list.refresh_from_db()
        self.assertEqual(_todo_list.todos.count(), 0)

    @fake_permission(todo_scope.write)
    def test_create_todo_success_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.post(self.todos_url,
                                    content_type='application/json',
                                    data={
                                        'title': 'Test Title',
                                        'description': 'Test Description',
                                        'valid_until': timezone.now() + timedelta(days=random.randint(1, 10)),
                                        'todo_list': _todo_list.pk,
                                        'status': TodoStatuses.open
                                    })
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['title'], 'Test Title')
        self.assertEqual(response.data['description'], 'Test Description')
        self.assertEqual(response.data['todo_list'], _todo_list.pk)
        self.assertEqual(response.data['user'], str(self.user.pk))
        self.assertEqual(response.data['status'], TodoStatuses.open)
        _todo_list.refresh_from_db()
        self.assertEqual(_todo_list.todos.count(), 1)

        _cached_todo = TodoRepository.lookup_from_cache(self.user.pk, response.data['id'])
        self.assertIsNotNone(_cached_todo)
        self.assertEqual(_cached_todo.title, 'Test Title')
        self.assertEqual(_cached_todo.description, 'Test Description')
        self.assertEqual(_cached_todo.todo_list_id, _todo_list.pk)
        self.assertEqual(_cached_todo.user_id, str(self.user.pk))
        self.assertEqual(_cached_todo.status_id, TodoStatuses.open)

    @fake_permission(todo_scope.write)
    def test_create_todo_valid_until_error_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.post(self.todos_url,
                                    content_type='application/json',
                                    data={
                                        'title': 'Test Title',
                                        'description': 'Test Description',
                                        'valid_until': timezone.now() - timedelta(days=random.randint(1, 10)),
                                        'todo_list': _todo_list.pk,
                                        'status': TodoStatuses.open
                                    })
        self.assertEqual(response.status_code, 400)
        _todo_list.refresh_from_db()
        self.assertEqual(_todo_list.todos.count(), 0)

    @fake_permission(todo_scope.write)
    def test_create_todo_invalid_todo_list_case(self):
        _other_user = baker.make('user.User', status_id=UserStatuses.enabled)
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=_other_user.id, status_id=TodoListStatuses.open)

        response = self.client.post(self.todos_url,
                                    content_type='application/json',
                                    data={
                                        'title': 'Test Title',
                                        'description': 'Test Description',
                                        'valid_until': timezone.now() + timedelta(days=random.randint(1, 10)),
                                        'todo_list': _todo_list.pk,
                                        'status': TodoStatuses.open
                                    })
        self.assertEqual(response.status_code, 400)
        _todo_list.refresh_from_db()
        self.assertEqual(_todo_list.todos.count(), 0)

    @fake_permission(todo_scope.write)  # Invalid permission for read
    def test_get_todo_forbidden_case(self):
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.open)

        response = self.client.get(self.todo_detail_url.format(id=_todo.pk))
        self.assertEqual(response.status_code, 403)

    @fake_permission(todo_scope.read)
    def test_get_todo_not_owner_case(self):
        _other_user = baker.make('user.User', status_id=UserStatuses.enabled)

        _todo = baker.make(
            'todo.Todo', user_id=_other_user.id, status_id=TodoStatuses.open)

        response = self.client.get(self.todo_detail_url.format(id=_todo.pk))
        self.assertEqual(response.status_code, 404)

    @fake_permission(todo_scope.read)
    def test_get_todo_success_case(self):
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.open)

        response = self.client.get(self.todo_detail_url.format(id=_todo.pk))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['id'], str(_todo.pk))

    @fake_permission(todo_scope.read)
    def test_get_todo_already_deleted_case(self):
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.deleted)

        response = self.client.get(self.todo_detail_url.format(id=_todo.pk))
        self.assertEqual(response.status_code, 404)

    @fake_permission(todo_scope.read)  # Invalid permission for write
    def test_update_todo_forbidden_case(self):
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.open)

        response = self.client.put(self.todo_detail_url.format(id=_todo.pk),
                                   content_type='application/json',
                                   data={
                                       'title': 'Test Title',
                                       'description': 'Test Description',
                                       'valid_until': _todo.valid_until,
                                       'todo_list': _todo.todo_list_id,
                                       'status': _todo.status_id,
                                   })
        self.assertEqual(response.status_code, 403)

    @fake_permission(todo_scope.write)
    def test_update_todo_success_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, todo_list_id=_todo_list.pk,
            valid_until=timezone.now() + timedelta(days=random.randint(1, 10)),
            status_id=TodoStatuses.open)

        response = self.client.put(self.todo_detail_url.format(id=_todo.pk),
                                   content_type='application/json',
                                   data={
                                       'title': 'Test Title',
                                       'description': 'Test Description',
                                       'valid_until': _todo.valid_until,
                                       'todo_list': _todo.todo_list_id,
                                       'status': _todo.status_id,
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Test Title')
        self.assertEqual(response.data['description'], 'Test Description')
        self.assertEqual(response.data['todo_list'], _todo.todo_list_id)
        self.assertEqual(response.data['status'], _todo.status_id)
        self.assertEqual(response.data['user'], str(self.user.pk))

        _cached_todo = TodoRepository.lookup_from_cache(self.user.pk, _todo.pk)
        self.assertIsNone(_cached_todo)

    @fake_permission(todo_scope.read)  # Invalid permission for write
    def test_delete_todo_forbidden_case(self):
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.open)

        response = self.client.delete(self.todo_detail_url.format(id=_todo.pk))
        self.assertEqual(response.status_code, 403)
        _todo.refresh_from_db()
        self.assertEqual(_todo.status_id, TodoStatuses.open)

    @fake_permission(todo_scope.write)
    def test_delete_todo_success_case(self):
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.open)

        response = self.client.delete(self.todo_detail_url.format(id=_todo.pk))
        self.assertEqual(response.status_code, 200)
        _todo.refresh_from_db()
        self.assertEqual(_todo.status_id, TodoStatuses.deleted)

        _cached_todo = TodoRepository.lookup_from_cache(self.user.pk, _todo.pk)
        self.assertIsNone(_cached_todo)

    @fake_permission(todo_scope.write)
    def test_delete_todo_already_deleted_case(self):
        _todo = baker.make(
            'todo.Todo', user_id=self.user.id, status_id=TodoStatuses.deleted)

        response = self.client.delete(self.todo_detail_url.format(id=_todo.pk))
        self.assertEqual(response.status_code, 404)
