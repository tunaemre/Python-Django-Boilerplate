from datetime import datetime
from typing import Union, Tuple

from django.utils import timezone
from rest_framework import serializers

from app.infrastructure.mixin.user_mixin import UserFilteredPrimaryKeyRelatedField
from app.infrastructure.repository.todo_list.todo_list_repository import TodoListRepository
from app.todo.models import Todo


class TodoSerializer(serializers.ModelSerializer):
    todo_list = UserFilteredPrimaryKeyRelatedField(queryset=TodoListRepository.default_queryset)

    class Meta:
        model = Todo
        fields: Union[str, Tuple] = '__all__'
        read_only_fields: Tuple = ('id', 'user')

    def validate_valid_until(self, obj: datetime) -> datetime:
        if obj < timezone.now():
            raise serializers.ValidationError(f'Invalid valid_until "{obj}" - value must be a future date.')
        return obj
