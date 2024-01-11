from rest_framework.routers import SimpleRouter

from app.todo.resources.views import TodoViewSet

_router = SimpleRouter()

# Register view sets
_router.register(r'todo', TodoViewSet, basename='Todos')

urlpatterns = [
    # Custom URL patterns
]

urlpatterns += _router.urls
