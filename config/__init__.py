import os
from pathlib import Path

from environ import Env

from config.app import _ConfigManager as AppConfigManager
from config.worker import _ConfigManager as WorkerConfigManager

app_config_manager = AppConfigManager
worker_config_manager = WorkerConfigManager


def get_environment() -> str:
    return os.environ.get('ENVIRONMENT') or 'local'


def read_env_file() -> None:
    env_file = os.path.join(Path(__file__).parent.parent.absolute(), 'env', f'{get_environment()}.env')
    if os.path.exists(env_file):
        Env.read_env(env_file=env_file)
    else:
        raise FileNotFoundError(f'Environment file not found: {env_file}')


# Read env file if exists."""
read_env_file()
