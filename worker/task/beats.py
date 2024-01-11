from worker import celery
from worker.task.status.tasks import update_expired_todos


@celery.task()
def beat_check_expired_todos() -> None:
    update_expired_todos.delay()
