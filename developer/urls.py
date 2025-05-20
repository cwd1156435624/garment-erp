from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SystemMonitorViewSet, APIMetricViewSet, SystemLogViewSet,
    ConfigItemViewSet, WebSocketSessionViewSet, WebSocketMessageViewSet,
    APITestView, SystemHealthView, SessionManagementView, DebugModeView
)

router = DefaultRouter()
router.register('system-monitor', SystemMonitorViewSet)
router.register('api-metrics', APIMetricViewSet)
router.register('system-logs', SystemLogViewSet)
router.register('config-items', ConfigItemViewSet)
router.register('websocket-sessions', WebSocketSessionViewSet)
router.register('websocket-messages', WebSocketMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 从apps/system/urls_developer.py合并的路由
    path('test-endpoint/', APITestView.as_view(), name='test-endpoint'),
    path('health/', SystemHealthView.as_view(), name='system-health'),
    path('sessions/', SessionManagementView.as_view(), name='session-management'),
    path('debug-mode/', DebugModeView.as_view(), name='debug-mode'),
]
