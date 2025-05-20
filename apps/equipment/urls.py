from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentViewSet, MaintenanceRecordViewSet, FaultRecordViewSet

router = DefaultRouter()
router.register('equipment', EquipmentViewSet)
router.register('equipment-maintenance', MaintenanceRecordViewSet)
router.register('equipment-fault', FaultRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]