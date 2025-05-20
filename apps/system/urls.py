from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views
from .views import MetricsView
from .views_log import LogViewSet
from .views_notice import NoticeViewSet

router = DefaultRouter()
router.register('logs', LogViewSet, basename='logs')
router.register('notices', NoticeViewSet, basename='notices')

urlpatterns = [
    # Prometheus指标导出
    path('metrics/', MetricsView.as_view(), name='metrics'),
    # 操作日志导出
    path('logs/export/', LogViewSet.as_view({'get': 'export'}), name='logs-export'),
]

urlpatterns += router.urls