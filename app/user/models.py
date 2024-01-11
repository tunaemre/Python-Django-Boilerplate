from __future__ import annotations

from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

from app.infrastructure.entity.base.base_model import BaseModel, BaseEnum
from app.infrastructure.enum.user.user_statuses import UserStatuses


# Create your models here.

class User(BaseModel, AbstractBaseUser):
    sub_id = models.CharField(max_length=50, null=False, blank=False, db_index=True)
    email = models.EmailField(null=False, blank=False, unique=True, db_index=True)
    status = models.ForeignKey('user.UserStatus', on_delete=models.PROTECT)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['sub_id', 'email']

    @classmethod
    def create(cls, sub_id: str, email: str) -> User:
        user = User(
            sub_id=sub_id,
            email=email,
            status_id=UserStatuses.enabled)
        # AbstractBaseUser has password field as default
        # set_unusable_password makes the password field unusable
        user.set_unusable_password()
        user.save()
        return user

    def __repr__(self) -> str:
        return f'{self.email} <{self.pk}>'


class UnauthenticatedUser:
    id = None
    pk = None
    username = ''

    def __str__(self) -> str:
        return 'UnauthenticatedUser'

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__)

    def __hash__(self) -> int:
        return hash(str(self))  # instances always return the same hash value

    def __int__(self) -> int:
        raise TypeError

    def save(self) -> None:
        raise NotImplementedError

    def delete(self) -> None:
        raise NotImplementedError

    def set_password(self, raw_password: str) -> None:
        raise NotImplementedError

    def check_password(self, raw_password: str) -> bool:
        raise NotImplementedError

    @property
    def is_anonymous(self) -> bool:
        return True

    @property
    def is_authenticated(self) -> bool:
        return False

    def get_username(self) -> str:
        return self.username


class UserStatus(BaseEnum):
    pass
