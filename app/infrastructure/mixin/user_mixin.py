from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import QuerySet
from rest_framework import serializers

from app.infrastructure.middleware.thread_local_middleware import local_user


class UserMixin:

    @property
    def user(self) -> AbstractBaseUser:
        return local_user()

    @property
    def user_id(self) -> str:
        return str(self.user.pk)


class UserFilteredPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self) -> QuerySet:
        request = self.context.get('request', None)
        queryset = super(UserFilteredPrimaryKeyRelatedField, self).get_queryset()
        if not request or not request.user:
            queryset.none()
        return queryset.filter(user=request.user)
