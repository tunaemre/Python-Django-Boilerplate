from typing import Any

from django.apps import AppConfig
from django.contrib.auth import get_user_model, user_logged_in
from django.db.models.query_utils import DeferredAttribute
from django.utils import timezone


def _update_last_login(sender: Any, user: Any, **kwargs: Any) -> None:
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    from django.contrib.auth.base_user import AbstractBaseUser
    assert isinstance(user, AbstractBaseUser)

    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])


class UserConfig(AppConfig):
    name = 'app.user'

    def ready(self) -> None:
        last_login_field = getattr(get_user_model(), 'last_login', None)
        # Register the handler only if UserModel.last_login is a field.
        if isinstance(last_login_field, DeferredAttribute):
            user_logged_in.connect(_update_last_login, dispatch_uid='update_last_login')
