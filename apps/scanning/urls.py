from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BarcodeViewSet, ScanningHistoryViewSet

router = DefaultRouter()
router.register('barcodes', BarcodeViewSet, basename='barcode')
router.register('scan-records', ScanningHistoryViewSet, basename='scan-record')

urlpatterns = [
    path('', include(router.urls)),
    # 条码批量操作
    path('barcodes/batch/', BarcodeViewSet.as_view({'post': 'batch_generate'}), name='barcode-batch-generate'),
    path('barcodes/batch/export/', BarcodeViewSet.as_view({'post': 'batch_export'}), name='barcode-batch-export'),
    path('barcodes/batch/delete/', BarcodeViewSet.as_view({'post': 'batch_delete'}), name='barcode-batch-delete'),
    # 条码特殊操作
    path('barcodes/<int:pk>/invalidate/', BarcodeViewSet.as_view({'post': 'invalidate'}), name='barcode-invalidate'),
    path('barcodes/<int:pk>/scan-history/', BarcodeViewSet.as_view({'get': 'scan_history'}), name='barcode-scan-history'),
]