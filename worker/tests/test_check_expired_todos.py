from http import HTTPStatus
from unittest import mock

import requests_mock
from django.test.testcases import SimpleTestCase
from requests import HTTPError
from requests_mock import Mocker

from worker import celery
from config import worker_config_manager
from worker.tests import get_mocker_response

from worker.task.beats import beat_check_expired_todos


class BeatSchedulesTestCase(SimpleTestCase):
    _mocker_response_path = 'test_check_expired_todos'
    _config = worker_config_manager.get_config()

    def setUp(self) -> None:
        super().setUp()
        _celery = celery
        _celery.conf.update(
            task_always_eager=True,
            task_eager_propagates=True
        )

    def tearDown(self) -> None:
        _celery = celery
        _celery.conf.update(
            task_always_eager=False,
            task_eager_propagates=False
        )
        super().tearDown()

    @requests_mock.Mocker()
    def test_check_expired_todos_empty(self, mocker: Mocker):
        mocker.post(
            f'https://{self._config.AUTH0_DOMAIN}/oauth/token',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='worker_auth-success'
            )
        )

        mocker.put(
            f'{self._config.TODO_API_URL}/api/v1/worker/expired/',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='check_expired_todos-empty'
            )
        )

        with mock.patch('common.client.mail_sender_client.MailSenderClient.send_mail') \
                as _mocked_send_expired_mail:
            beat_check_expired_todos.delay()
            assert not _mocked_send_expired_mail.called
            assert _mocked_send_expired_mail.call_count == 0

    @requests_mock.Mocker()
    def test_check_expired_todos_success(self, mocker: Mocker):
        mocker.post(
            f'https://{self._config.AUTH0_DOMAIN}/oauth/token',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='worker_auth-success'
            )
        )

        mocker.put(
            f'{self._config.TODO_API_URL}/api/v1/worker/expired/',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='check_expired_todos-success'
            )
        )

        with mock.patch('common.client.mail_sender_client.MailSenderClient.send_mail') \
                as _mocked_send_expired_mail:
            beat_check_expired_todos.delay()

            assert _mocked_send_expired_mail.called
            assert _mocked_send_expired_mail.call_count == 7

    @requests_mock.Mocker()
    def test_check_expired_todos_error(self, mocker: Mocker):
        mocker.post(
            f'https://{self._config.AUTH0_DOMAIN}/oauth/token',
            json=get_mocker_response(
                path=self._mocker_response_path,
                file_name='worker_auth-success'
            )
        )

        mocker.put(
            f'{self._config.TODO_API_URL}/api/v1/worker/expired/',
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

        with self.assertRaises(HTTPError):
            beat_check_expired_todos.delay()
