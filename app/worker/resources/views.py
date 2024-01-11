from typing import Any

from django.utils.functional import SimpleLazyObject
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.security.permission.worker_permission import WorkerPermission
from app.worker.resources.serializers import TodoSerializer
from app.worker.services.worker_service import WorkerService


class WorkerViewSet(ViewSet):
    permission_classes = [WorkerPermission]

    service: WorkerService = SimpleLazyObject(WorkerService)  # type: ignore

    @action(detail=False, methods=['PUT'], url_path='expired')
    def update_expired_todos(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        expired_todos = self.service.update_expired_todos()
        serializer = TodoSerializer(instance=expired_todos, many=True)
        return Response(serializer.data)
