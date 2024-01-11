import logging
from typing import Optional, Any

import graypy
from graypy import GELFUDPHandler

from common.logger.filters import StaticFieldsFilter, RequestFilter
from config import get_environment
from config.base.base_config import BaseConfig

_graylog: Optional[GELFUDPHandler] = None


def init_graylog(sender: BaseConfig, **kwargs: Any) -> None:
    assert isinstance(sender, BaseConfig), 'Method init_graylog need a config instance as sender.'
    global _graylog
    if _graylog is not None:
        return

    env = get_environment()

    if env not in ('test', 'local') and sender.ENABLE_GRAYLOG:
        logger = logging.getLogger()

        logger.setLevel(sender.GRAYLOG_LOGGING_LEVEL)
        logging.getLogger('werkzeug').setLevel(sender.GRAYLOG_LOGGING_LEVEL)

        assert sender.GRAYLOG_IP is not None, 'Graylog IP must be provided.'
        assert sender.GRAYLOG_PORT is not None, 'Graylog port must be provided.'
        _graylog = graypy.GELFUDPHandler(sender.GRAYLOG_IP, sender.GRAYLOG_PORT)

        _graylog.addFilter(StaticFieldsFilter({
            'environment': env}
        ))
        _graylog.addFilter(RequestFilter())

        logger.addHandler(_graylog)
