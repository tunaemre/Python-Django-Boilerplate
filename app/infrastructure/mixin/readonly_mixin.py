from __future__ import annotations
from typing import Any

from rest_framework.fields import Field
from rest_framework.serializers import SerializerMetaclass


class ReadOnlyMixin(Field):

    def __new__(cls, *args: Any, **kwargs: Any) -> ReadOnlyMixin:
        assert isinstance(cls, SerializerMetaclass), 'ReadOnlyMixin could only used in Serializers.'
        if hasattr(cls, 'Meta'):
            setattr(
                cls.Meta,
                'read_only_fields',
                [f.name for f in cls.Meta.model._meta.get_fields()])
        return super(ReadOnlyMixin, cls).__new__(cls, *args, **kwargs)
