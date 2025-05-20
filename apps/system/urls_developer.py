from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_developer import (
    APILogViewSet, SystemLogViewSet, PerformanceMetricViewSet,
    ConfigOverrideViewSet, APITestView, SystemHealthView,
    SessionManagementView, DebugModeView
)

router = DefaultRouter()
router.register('logs/api', APILogViewSet)
router.register('logs/system', SystemLogViewSet)
router.register('performance', PerformanceMetricViewSet)
router.register('config-overrides', ConfigOverrideViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('test-endpoint/', APITestView.as_view(), name='test-endpoint'),
    path('health/', SystemHealthView.as_view(), name='system-health'),
    path('sessions/', SessionManagementView.as_view(), name='session-management'),
    path('debug-mode/', DebugModeView.as_view(), name='debug-mode'),
]