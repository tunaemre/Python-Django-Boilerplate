from typing import Dict, Any, Tuple

import jwt
import requests
from jwt import ExpiredSignatureError
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from config import app_config_manager


class UserInfoSerializer(serializers.Serializer):
    sub = serializers.CharField(max_length=50, required=True, allow_blank=False, allow_null=False)
    email = serializers.EmailField(max_length=320, required=True, allow_blank=False, allow_null=False)


class Auth0Service:
    """Perform JSON Web Token (JWT) validation using PyJWT"""

    def __init__(self) -> None:
        config = app_config_manager.get_config()
        self.algorithm = ['RS256']
        self.issuer_url = f'https://{config.AUTH0_DOMAIN}/'
        self.jwks_uri = f'{self.issuer_url}.well-known/jwks.json'
        self.audience = config.AUTH0_AUDIENCE

    def get_signing_key(self, token: str) -> str:
        assert self.jwks_uri, 'Auth0 jwks.json url must be defined.'
        jwks_client = jwt.PyJWKClient(self.jwks_uri)

        return jwks_client.get_signing_key_from_jwt(token).key

    def validate_jwt(self, token: str) -> Dict[str, Any]:
        try:
            jwt_signing_key = self.get_signing_key(token)

            payload = jwt.decode(
                token,
                jwt_signing_key,
                algorithms=self.algorithm,
                audience=self.audience,
                issuer=self.issuer_url,
            )
            return payload
        except ExpiredSignatureError as e:
            raise AuthenticationFailed('Expired token.') from e
        except Exception as e:
            raise AuthenticationFailed from e

    def get_user_info(self, token: str) -> Tuple[str, str]:
        response = requests.post(f'{self.issuer_url}userinfo',
                                 headers={f'Authorization': f'Bearer {token}'},
                                 timeout=4.0)

        serializer = UserInfoSerializer(data=response.json())
        if not serializer.is_valid(raise_exception=False):
            raise AuthenticationFailed('Invalid user info data.')
        return serializer.validated_data['sub'], serializer.validated_data['email']
