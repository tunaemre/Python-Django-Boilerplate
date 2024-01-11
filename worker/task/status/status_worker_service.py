from typing import Any, List

from common.client.todo_api_client import TodoApiClient
from config import worker_config_manager

with worker_config_manager as config:
    todo_api_client = TodoApiClient(
        base_url=config.TODO_API_URL,
        auth0_config={
            'AUTH0_DOMAIN': config.AUTH0_DOMAIN,
            'AUTH0_AUDIENCE': config.AUTH0_AUDIENCE,
            'AUTH0_M2M_CLIENT_ID': config.AUTH0_M2M_CLIENT_ID,
            'AUTH0_M2M_CLIENT_SECRET': config.AUTH0_M2M_CLIENT_SECRET,
    })


class StatusWorkerService:

    @staticmethod
    def update_expired_todos() -> List[Any]:
        return todo_api_client.update_expired_todos()
