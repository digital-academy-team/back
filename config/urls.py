from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views import welcome, get_logged_errors


class UserSchemaView(SpectacularAPIView):
    urlconf = 'api.users.urls'
    custom_settings = {
        'TITLE': 'Digital Academy User API',
        'SERVERS': [{'url': f'{settings.SITE_URL}/api/users'}],
    }


class TeacherSchemaView(SpectacularAPIView):
    urlconf = 'api.teachers.urls'
    custom_settings = {
        'TITLE': 'Digital Academy Teacher API',
        'SERVERS': [{'url': f'{settings.SITE_URL}/api/teachers'}],
    }


urlpatterns = [
    path('', welcome, name='index'),
    path('logs-all/', get_logged_errors, name='errors'),
    path('admin/', admin.site.urls),

    path('api/users/', include('api.users.urls')),
    path('api/teachers/', include('api.teachers.urls')),

    path('api/schema/users/', UserSchemaView.as_view(), name='users-schema'),
    path('swagger/users/', SpectacularSwaggerView.as_view(url_name='users-schema'), name='users-swagger-ui'),

    path('api/schema/teachers/', TeacherSchemaView.as_view(), name='teachers-schema'),
    path('swagger/teachers/', SpectacularSwaggerView.as_view(url_name='teachers-schema'), name='teachers-swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)