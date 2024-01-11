from typing import Dict, Type

from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import ModelViewSet


class MultiSerializerMixin:
    action_serializer_classes: Dict[str, Type[BaseSerializer]] = {}

    def get_serializer_class(self) -> Type[BaseSerializer]:
        assert isinstance(self, ModelViewSet) and isinstance(self, MultiSerializerMixin), \
            'MultiSerializerMixin could only used in ModelViewSets.'

        if self.action in self.action_serializer_classes:
            return self.action_serializer_classes[self.action]
        else:
            return super(MultiSerializerMixin, self).get_serializer_class()
