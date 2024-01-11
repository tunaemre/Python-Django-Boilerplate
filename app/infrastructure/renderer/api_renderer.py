from typing import Any, Optional, Mapping

from rest_framework.permissions import SAFE_METHODS
from rest_framework.renderers import JSONRenderer


class APIRenderer(JSONRenderer):

    def render(self, data: Any, accepted_media_type: Optional[str] = None,
               renderer_context: Optional[Mapping[str, Any]] = None) -> bytes:
        _method = None
        _success = False
        _exception = False
        _data = None
        _message = None
        _code = None

        if renderer_context:
            if _request := renderer_context.get('request'):
                _method = _request.method

            if _response := renderer_context.get('response'):
                _success = 200 <= _response.status_code < 400
                _exception = _response.exception

                # Override default delete operation status
                if _response.status_code == 204:
                    _response.status_code = 200

        if _success:
            _data = data
            if _method in SAFE_METHODS:
                if _data:
                    _message = 'Data obtained.'
                else:
                    _message = 'No data found.'
            else:
                _message = 'Operation completed.'
        else:
            _data = data
            _message = 'An error occurred.'
            _code = 'fatal_error'

        base_response = {
            'success': _success,
            'message': _message,
            'code': _code,
            'data': _data
        }
        return super().render(base_response, accepted_media_type, renderer_context)
