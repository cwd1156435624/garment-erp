from django.urls import path
from rest_framework.routers import DefaultRouter
from .views_alerts import AlertViewSet

router = DefaultRouter()
router.register('', AlertViewSet, basename='alerts')

urlpatterns = router.urls