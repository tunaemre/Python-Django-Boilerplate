import logging

from worker import celery
from worker.base.task_lock import TaskLock
from worker.task.status.status_worker_service import StatusWorkerService
from worker.task.mail.tasks import send_expired_mail

logger = logging.getLogger(__name__)


@celery.task(base=TaskLock)
def update_expired_todos() -> None:
    todo_list = StatusWorkerService.update_expired_todos()
    if not todo_list:
        logger.info('No expired todo found.')
        return

    for todo in todo_list:
        send_expired_mail.delay(todo['title'], todo['user']['email'])
