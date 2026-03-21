from rest_framework.routers import DefaultRouter

from api.users.certificate.views import CertificateViewSet

router = DefaultRouter()

router.register('', CertificateViewSet, basename='certificate')


urlpatterns = router.urls

