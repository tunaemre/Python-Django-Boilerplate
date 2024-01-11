from typing import Union, Tuple

from rest_framework import serializers

from app.infrastructure.mixin.readonly_mixin import ReadOnlyMixin
from app.todo.models import Todo
from app.user.resources.serializers import UserSerializer


class TodoSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Todo
        fields: Union[str, Tuple] = '__all__'
