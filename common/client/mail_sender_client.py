from typing import Any


class MailSenderClient:

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def send_mail(self, recipient: str, **email_data: Any) -> None:
        # Send mail
        pass
