import random

from model_bakery import baker

from app.infrastructure.enum.todo_list.todo_list_statuses import TodoListStatuses
from app.infrastructure.enum.user.user_statuses import UserStatuses
from app.infrastructure.repository.todo_list.todo_list_repository import TodoListRepository
from app.security.permission import todo_scope
from test.auth_test_case import AuthTestCase, fake_permission


class TodoListViewTestCase(AuthTestCase):
    todo_lists_url = '/api/v1/todo_list/'
    todo_list_detail_url = '/api/v1/todo_list/{id}/'

    @fake_permission(todo_scope.write)  # Invalid permission for read
    def test_list_todo_lists_forbidden_case(self):
        response = self.client.get(self.todo_lists_url)
        self.assertEqual(response.status_code, 403)

    @fake_permission(todo_scope.read)
    def test_list_todo_lists_empty_case(self):
        response = self.client.get(self.todo_lists_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    @fake_permission(todo_scope.read)
    def test_list_todo_lists_success_case(self):
        _active_quantity = random.randint(5, 10)
        _deleted_quantity = random.randint(5, 10)
        _other_user_quantity = random.randint(5, 10)

        baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open,
            _quantity=_active_quantity)
        baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.deleted,
            _quantity=_deleted_quantity)

        _other_user = baker.make('user.User', status_id=UserStatuses.enabled)
        baker.make(
            'todo_list.TodoList', user_id=_other_user.id, status_id=TodoListStatuses.open,
            _quantity=_other_user_quantity)

        response = self.client.get(self.todo_lists_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), _active_quantity)

    @fake_permission(todo_scope.read)  # Invalid permission for write
    def test_create_todo_list_forbidden_case(self):
        response = self.client.post(self.todo_lists_url,
                                    content_type='application/json',
                                    data={
                                        'name': 'Test Name',
                                        'status': TodoListStatuses.open
                                    })
        self.assertEqual(response.status_code, 403)

    @fake_permission(todo_scope.write)
    def test_create_todo_list_success_case(self):
        response = self.client.post(self.todo_lists_url,
                                    content_type='application/json',
                                    data={
                                        'name': 'Test Name',
                                        'status': TodoListStatuses.open
                                    })
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['name'], 'Test Name')
        self.assertEqual(response.data['user'], str(self.user.pk))
        self.assertEqual(response.data['status'], TodoListStatuses.open)

        _cached_todo_list = TodoListRepository.lookup_from_cache(self.user.pk, response.data['id'])
        self.assertIsNotNone(_cached_todo_list)
        self.assertEqual(_cached_todo_list.name, 'Test Name')
        self.assertEqual(_cached_todo_list.user_id, str(self.user.pk))
        self.assertEqual(_cached_todo_list.status_id, TodoListStatuses.open)

    @fake_permission(todo_scope.write)  # Invalid permission for read
    def test_get_todo_list_forbidden_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.get(self.todo_list_detail_url.format(id=_todo_list.pk))
        self.assertEqual(response.status_code, 403)

    @fake_permission(todo_scope.read)
    def test_get_todo_list_not_owner_case(self):
        _other_user = baker.make('user.User', status_id=UserStatuses.enabled)

        _todo_list = baker.make(
            'todo_list.TodoList', user_id=_other_user.id, status_id=TodoListStatuses.open)

        response = self.client.get(self.todo_list_detail_url.format(id=_todo_list.pk))
        self.assertEqual(response.status_code, 404)

    @fake_permission(todo_scope.read)
    def test_get_todo_list_success_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.get(self.todo_list_detail_url.format(id=_todo_list.pk))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data)
        self.assertEqual(response.data['id'], str(_todo_list.pk))

    @fake_permission(todo_scope.read)
    def test_get_todo_list_already_deleted_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.deleted)

        response = self.client.get(self.todo_list_detail_url.format(id=_todo_list.pk))
        self.assertEqual(response.status_code, 404)

    @fake_permission(todo_scope.read)  # Invalid permission for write
    def test_update_todo_list_forbidden_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.put(self.todo_list_detail_url.format(id=_todo_list.pk),
                                   content_type='application/json',
                                   data={
                                       'name': 'Test Name',
                                       'status': _todo_list.status_id,
                                   })
        self.assertEqual(response.status_code, 403)

    @fake_permission(todo_scope.write)
    def test_update_todo_list_success_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.put(self.todo_list_detail_url.format(id=_todo_list.pk),
                                   content_type='application/json',
                                   data={
                                       'name': 'Test Name',
                                       'status': _todo_list.status_id,
                                   })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Test Name')
        self.assertEqual(response.data['status'], _todo_list.status_id)
        self.assertEqual(response.data['user'], str(self.user.pk))

        _cached_todo_list = TodoListRepository.lookup_from_cache(self.user.pk, _todo_list.pk)
        self.assertIsNone(_cached_todo_list)

    @fake_permission(todo_scope.read)  # Invalid permission for write
    def test_delete_todo_list_forbidden_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.delete(self.todo_list_detail_url.format(id=_todo_list.pk))
        self.assertEqual(response.status_code, 403)
        _todo_list.refresh_from_db()
        self.assertEqual(_todo_list.status_id, TodoListStatuses.open)

    @fake_permission(todo_scope.write)
    def test_delete_todo_list_success_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.open)

        response = self.client.delete(self.todo_list_detail_url.format(id=_todo_list.pk))
        self.assertEqual(response.status_code, 200)
        _todo_list.refresh_from_db()
        self.assertEqual(_todo_list.status_id, TodoListStatuses.deleted)

        _cached_todo_list = TodoListRepository.lookup_from_cache(self.user.pk, _todo_list.pk)
        self.assertIsNone(_cached_todo_list)

    @fake_permission(todo_scope.write)
    def test_delete_todo_already_deleted_case(self):
        _todo_list = baker.make(
            'todo_list.TodoList', user_id=self.user.id, status_id=TodoListStatuses.deleted)

        response = self.client.delete(self.todo_list_detail_url.format(id=_todo_list.pk))
        self.assertEqual(response.status_code, 404)
