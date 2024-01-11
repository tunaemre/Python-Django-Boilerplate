from threading import local

from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import NotAuthenticated, APIException
from rest_framework.request import Request
from rest_framework.response import Response

_thread_locals = local()


class ThreadLocalMiddleware(MiddlewareMixin):

    def process_request(self, request: Request) -> None:
        setattr(_thread_locals, 'request', request)

    def process_response(self, request: Request, response: Response) -> Response:
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response


def _local_request() -> Request:
    request = getattr(_thread_locals, 'request', None)
    if not request:
        raise APIException
    return request


def local_user() -> AbstractBaseUser:
    user = getattr(_local_request(), 'user', None)
    if not user:
        raise NotAuthenticated
    return user
