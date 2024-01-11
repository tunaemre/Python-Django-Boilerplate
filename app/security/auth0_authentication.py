from typing import Tuple, Optional

from django.contrib.auth import user_logged_in, get_user_model
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.functional import SimpleLazyObject
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from app.infrastructure.enum.user.user_statuses import UserStatuses
from app.security.auth0_service import Auth0Service


class Auth0Authentication(BaseAuthentication):
    """
    Auth0 bearer token based authentication.

    Authorization: Bearer <token>
    """

    keyword: str = 'Bearer'
    auth0_service: Auth0Service = SimpleLazyObject(Auth0Service)  # type: ignore

    def authenticate(self, request: Request) -> Optional[Tuple[Optional[AbstractBaseUser], str]]:
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise AuthenticationFailed('Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise AuthenticationFailed('Invalid token header. Token string should not contain spaces.')

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed('Invalid token header. Token string should not contain invalid characters.')

        return self._authenticate_credentials(request, token)

    def authenticate_header(self, request: Request) -> str:
        return self.keyword

    def _authenticate_credentials(self, request: Request, token: str) -> Tuple[Optional[AbstractBaseUser], str]:
        jwt = self.auth0_service.validate_jwt(token)

        sub = jwt.get('sub')
        if not sub:
            raise AuthenticationFailed('Invalid JWT data. Subject must be provided.')

        if jwt.get('gty') != 'client-credentials':
            # Not a machine to machine token
            user = self._get_or_create_user(token, sub)
            setattr(request, 'user', user)
            user_logged_in.send(sender=user.__class__, request=request, user=user)
        else:
            user = None

        permissions = jwt.get('permissions')
        setattr(request, 'permissions', permissions)

        return user, token

    def _get_or_create_user(self, token: str, sub: str) -> AbstractBaseUser:
        user_model = get_user_model()
        try:
            user = user_model.objects.get(sub_id=sub)
            if user.status_id != UserStatuses.enabled:
                raise AuthenticationFailed
            return user
        except user_model.DoesNotExist:
            pass

        sub, email = self.auth0_service.get_user_info(token)
        try:
            user = user_model.objects.get(email=email)
            if user.status_id != UserStatuses.enabled:
                raise AuthenticationFailed

            user.sub_id = sub
            user.save(update_fields=['sub_id'])
            return user
        except user_model.DoesNotExist:
            pass

        if hasattr(user_model, 'create'):
            return user_model.create(sub_id=sub, email=email)
        else:
            return user_model.objects.create(sub_id=sub, email=email, status_id=UserStatuses.enabled)
