from rest_framework.routers import SimpleRouter

from app.workshop.views import GuestViewSet

router = SimpleRouter()
router.register('workshop/guest', GuestViewSet, basename='Guests')

urlpatterns = [

]

urlpatterns += router.urls
