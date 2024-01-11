from typing import Tuple, Union

from rest_framework import serializers

from app.infrastructure.mixin.readonly_mixin import ReadOnlyMixin
from app.user.models import User


class UserSerializer(ReadOnlyMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields: Union[str, Tuple] = ('id', 'sub_id', 'email')
