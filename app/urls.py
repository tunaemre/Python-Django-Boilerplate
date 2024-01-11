"""URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import json

from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseNotFound, HttpRequest, HttpResponse
from django.urls import path, re_path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def __api_not_found(request: HttpRequest) -> HttpResponse:
    response = {
        'success': False,
        'message': f'Requested API {request.path} was not found on this server.',
        'code': 'not_found',
        'data': None
    }
    return HttpResponseNotFound(
        content=json.dumps(response),
        content_type='application/json'
    )


_schema_view = get_schema_view(
    openapi.Info(
        title="Boilerplate",
        default_version='v1'
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', _schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', _schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', _schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/v1/', include('app.todo.urls')),
    path('api/v1/', include('app.todo_list.urls')),
    path('api/v1/', include('app.worker.urls')),
    path('api/v1/', include('app.workshop.urls')),

    # Invalid API endpoints
    re_path(r'^api/v1/(?:.*)?$', __api_not_found),
]

# Serve static files in debug mode
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
