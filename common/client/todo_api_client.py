from datetime import datetime, timedelta
from typing import Optional, Any, Tuple, Final, List, Dict
from urllib.parse import urljoin

import requests
from requests import PreparedRequest, Response
from requests.auth import AuthBase
from rest_framework import serializers


class DataField(serializers.Field):
    def to_representation(self, value: Any) -> Any:
        return value

    def to_internal_value(self, data: Any) -> Any:
        return data


class TodoApiSerializer(serializers.Serializer):

    def __init__(self, data: Dict[str, Any], **kwargs: Any) -> None:
        self.response_data = data.pop('data', None)
        super().__init__(data=data, **kwargs)

    success = serializers.BooleanField(required=True)
    message = serializers.CharField(required=False, allow_null=True)
    code = serializers.CharField(required=False, allow_null=True)


class TodoApiAuthBase(AuthBase):
    def __init__(self, token: str, expires_in: int) -> None:
        self.token = token
        self.expired_at = datetime.utcnow() + timedelta(seconds=expires_in)

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expired_at

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r


class TodoApiClient:
    __auth: Optional[TodoApiAuthBase] = None
    __default_timeout: Final = 4.0

    __update_expired_todos_url: Final = 'api/v1/worker/expired/'

    def __init__(self, base_url: str, auth0_config: Dict[str, str]) -> None:
        self.base_url = base_url
        self.auth0_config = auth0_config

    def __get_endpoint(self, service_url: str) -> str:
        return urljoin(self.base_url, service_url)

    def __get_auth(self) -> TodoApiAuthBase:
        if not self.__auth or self.__auth.is_expired:
            token, expires_in = self.__get_token()
            self.__auth = TodoApiAuthBase(token=token, expires_in=expires_in)

        return self.__auth

    def __get_token(self) -> Tuple[str, int]:
        token_request = {
            'client_id': self.auth0_config['AUTH0_M2M_CLIENT_ID'],
            'client_secret': self.auth0_config['AUTH0_M2M_CLIENT_SECRET'],
            'audience': self.auth0_config['AUTH0_AUDIENCE'],
            'grant_type': 'client_credentials'
        }

        response = requests.post(
            f'https://{self.auth0_config["AUTH0_DOMAIN"]}/oauth/token',
            json=token_request,
            timeout=self.__default_timeout)
        response.raise_for_status()

        data = response.json()
        return data['access_token'], data['expires_in']

    def __clear_auth(self) -> None:
        self.__auth = None

    def __check_response(self, response: Response) -> Any:
        response = self.__check_unauthorized(response)
        response.raise_for_status()
        serializer = TodoApiSerializer(data=response.json())
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data['success']:
            raise Exception(f'Todo API error, message: {serializer.validated_data["message"]}')
        return serializer.response_data

    def __check_unauthorized(self, response: Response) -> Response:
        if response.status_code == 401:
            # Renew auth
            self.__clear_auth()
            request = response.request.copy()
            request.prepare_auth(self.__get_auth())
            with requests.session() as s:
                response = s.send(request)
        return response

    def update_expired_todos(self) -> List[Any]:
        endpoint = self.__get_endpoint(self.__update_expired_todos_url)
        response = requests.put(endpoint,
                                auth=self.__get_auth(),
                                timeout=self.__default_timeout)

        data = self.__check_response(response)
        assert isinstance(data, list)
        return data
