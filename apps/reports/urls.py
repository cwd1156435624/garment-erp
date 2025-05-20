from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportTemplateViewSet, SavedReportViewSet,
    ProductionReportViewSet, InventoryReportViewSet, CostReportViewSet
)

router = DefaultRouter()
router.register('templates', ReportTemplateViewSet)
router.register('saved-reports', SavedReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # 生产报表路由
    path('production/statistics/', ProductionReportViewSet.as_view({'get': 'statistics'})),
    path('production/efficiency/', ProductionReportViewSet.as_view({'get': 'efficiency'})),
    path('production/quality/', ProductionReportViewSet.as_view({'get': 'quality'})),
    
    # 库存报表路由
    path('inventory/status/', InventoryReportViewSet.as_view({'get': 'status'})),
    path('inventory/turnover/', InventoryReportViewSet.as_view({'get': 'turnover'})),
    path('inventory/consumption/', InventoryReportViewSet.as_view({'get': 'consumption'})),
    path('inventory/statistics/', InventoryReportViewSet.as_view({'get': 'statistics'})),
    
    # 成本报表路由
    path('cost/production/', CostReportViewSet.as_view({'get': 'production'})),
    path('cost/procurement/', CostReportViewSet.as_view({'get': 'procurement'})),
    path('cost/variance/', CostReportViewSet.as_view({'get': 'variance'})),
]