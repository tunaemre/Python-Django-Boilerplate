from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from app.security.permission import todo_scope


class TodoPermission(permissions.BasePermission):
    _permission_map = {
        'GET': todo_scope.read,
        'HEAD': todo_scope.read,
        'POST': todo_scope.write,
        'PUT': todo_scope.write,
        'PATCH': todo_scope.write,
        'DELETE': todo_scope.write
    }

    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        assert request.method
        _required_permission = self._permission_map.get(request.method)
        if not _required_permission:
            return True

        _permissions = getattr(request, 'permissions', [])
        if not permissions:
            return False

        return _required_permission in _permissions

