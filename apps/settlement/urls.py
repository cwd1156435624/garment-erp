from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SettlementViewSet, FactoryViewSet

router = DefaultRouter()
router.register('settlements', SettlementViewSet, basename='settlement')
router.register('factories', FactoryViewSet, basename='factory')

urlpatterns = [
    path('', include(router.urls)),
    # 结算单批量操作
    path('settlements/batch/export/', SettlementViewSet.as_view({'post': 'batch_export'}), name='settlement-batch-export'),
    path('settlements/batch/delete/', SettlementViewSet.as_view({'post': 'batch_delete'}), name='settlement-batch-delete'),
    # 工厂批量操作
    path('factories/batch/export/', FactoryViewSet.as_view({'post': 'batch_export'}), name='factory-batch-export'),
    path('factories/batch/delete/', FactoryViewSet.as_view({'post': 'batch_delete'}), name='factory-batch-delete'),
]