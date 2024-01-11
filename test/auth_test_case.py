from __future__ import annotations

from contextlib import ContextDecorator
from typing import Tuple
from unittest import mock

from django.contrib.auth.base_user import AbstractBaseUser
from django.test import TestCase
from model_bakery import baker
from rest_framework.request import Request

from app.infrastructure.enum.user.user_statuses import UserStatuses
from app.security.auth0_authentication import Auth0Authentication
from app.user.models import User

_permissions = None


class _FakePermission(ContextDecorator):
    def __init__(self, *permission: str) -> None:
        self.permissions = permission

    def __enter__(self) -> _FakePermission:
        global _permissions
        _permissions = self.permissions
        return self

    def __exit__(self, *exc) -> None:
        global _permissions
        _permissions = None


fake_permission = _FakePermission


class AuthTestCase(TestCase):

    def mock_authenticate(self, request: Request) -> Tuple[AbstractBaseUser, str]:
        setattr(request, 'user', self.user)
        if _permissions:
            setattr(request, 'permissions', _permissions)

        return self.user, 'test_token'

    def setUp(self) -> None:
        super().setUp()
        self.user: User = baker.make('user.User', status_id=UserStatuses.enabled)
        self.mocked_auth = mock.patch.object(
            Auth0Authentication, 'authenticate', side_effect=self.mock_authenticate)
        self.mocked_auth.start()

    def tearDown(self) -> None:
        self.mocked_auth.stop()
        super().tearDown()
