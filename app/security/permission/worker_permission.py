from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from app.security.permission import worker_scope


class WorkerPermission(permissions.BasePermission):
    _permission_map = {
        'GET': worker_scope.worker,
        'HEAD': worker_scope.worker,
        'POST': worker_scope.worker,
        'PUT': worker_scope.worker,
        'PATCH': worker_scope.worker,
        'DELETE': worker_scope.worker
    }

    def has_permission(self, request: Request, view: APIView) -> bool:
        # Worker permission does not assert user, but permissions
        assert request.method
        _required_permission = self._permission_map.get(request.method)
        if not _required_permission:
            return True

        _permissions = getattr(request, 'permissions', [])
        if not permissions:
            return False

        return _required_permission in _permissions
