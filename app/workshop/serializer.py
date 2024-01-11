from rest_framework import serializers

from app.workshop.models import Guest


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'
        read_only_fields = ('id', 'attend_on')