from rest_framework.routers import SimpleRouter

from app.worker.resources.views import WorkerViewSet

_router = SimpleRouter()

# Register view sets
_router.register(r'worker', WorkerViewSet, basename='Worker Methods')

urlpatterns = [
    # Custom URL patterns
]

urlpatterns += _router.urls
