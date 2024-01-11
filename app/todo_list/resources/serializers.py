from typing import Union, Tuple

from rest_framework import serializers

from app.todo.resources.serializers import TodoSerializer
from app.todo_list.models import TodoList


class TodoListSerializer(serializers.ModelSerializer):

    class Meta:
        model = TodoList
        fields: Union[str, Tuple] = '__all__'
        read_only_fields: Tuple = ('id', 'user')


class TodoListDetailSerializer(serializers.ModelSerializer):
    todos = TodoSerializer(many=True, read_only=True)

    class Meta:
        model = TodoList
        fields: Union[str, Tuple] = '__all__'
        read_only_fields: Tuple = ('id', 'user')
