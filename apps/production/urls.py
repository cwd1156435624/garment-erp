from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, ProductionPlanViewSet, CuttingTaskViewSet, ProductionExceptionViewSet, BatchViewSet
from .views_schedule import ScheduleViewSet
from .views_progress import ProgressView, ProgressUpdateView, IssueReportView
from .views_cutting import CuttingTaskCreateView, CuttingResultView
from .views_exception import ExceptionListView, ExceptionReportView, ExceptionHandlingView

router = DefaultRouter()
router.register('orders', OrderViewSet)
router.register('production-plans', ProductionPlanViewSet)
router.register('cutting-tasks', CuttingTaskViewSet)
router.register('exceptions', ProductionExceptionViewSet)
router.register('batches', BatchViewSet)
router.register('schedules', ScheduleViewSet, basename='schedules')

urlpatterns = [
    path('', include(router.urls)),
    # 生产进度相关接口
    path('progress/', ProgressView.as_view(), name='production-progress'),
    path('progress/<int:process_id>/', ProgressUpdateView.as_view(), name='progress-update'),
    path('progress/<int:process_id>/issues/', IssueReportView.as_view(), name='issue-report'),
    # 生产资源接口
    path('resources/available/', ScheduleViewSet.as_view({'get': 'available_resources'}), name='available-resources'),
    # 裁剪管理接口
    path('cutting/tasks/', CuttingTaskCreateView.as_view(), name='cutting-task-create'),
    path('cutting/results/', CuttingResultView.as_view(), name='cutting-result'),
    # 异常管理接口
    path('exceptions/', ExceptionListView.as_view({'get': 'list', 'post': 'create'}), name='exception-list'),
    path('exceptions/<int:id>/handling/', ExceptionHandlingView.as_view(), name='exception-handling'),
]