from rest_framework.routers import SimpleRouter

from app.todo_list.resources.views import TodoListViewSet

_router = SimpleRouter()

# Register view sets
_router.register(r'todo_list', TodoListViewSet, basename='Todo Lists')

urlpatterns = [
    # Custom URL patterns
]

urlpatterns += _router.urls
