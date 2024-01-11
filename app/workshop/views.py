from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet

from app.workshop.models import Guest
from app.workshop.serializer import GuestSerializer


# Create your views here.

class GuestViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = GuestSerializer
    queryset = Guest.objects.all()
