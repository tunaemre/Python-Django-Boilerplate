from common.client.mail_sender_client import MailSenderClient
from config import worker_config_manager
from worker import celery

mail_sender_client = MailSenderClient(
    api_key=worker_config_manager.get_config().MAIL_SERVICE_API_KEY)


@celery.task()
def send_expired_mail(todo_title: str, email: str) -> None:
    mail_sender_client.send_mail(
        recipient=email,
        todo_title=todo_title
    )
