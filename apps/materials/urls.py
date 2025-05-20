from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MaterialViewSet, LocationViewSet, InventoryViewSet, SupplierViewSet,
    ProcurementRequirementViewSet, ProcurementOrderViewSet
)

router = DefaultRouter()
router.register(r'materials', MaterialViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'procurement/requirements', ProcurementRequirementViewSet)
router.register(r'procurement/orders', ProcurementOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]