#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main() -> None:
    """Run administrative tasks."""
    # Set django settings module if not provided
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Set environment in test if not provided
    try:
        command = sys.argv[1]
        if command.lower() == 'test':
            os.environ.setdefault('ENVIRONMENT', 'test')
    except IndexError:
        pass

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
