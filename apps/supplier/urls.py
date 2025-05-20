from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, SupplierPerformanceViewSet, SupplierContractViewSet

router = DefaultRouter()
router.register('suppliers', SupplierViewSet)
router.register('performances', SupplierPerformanceViewSet)
router.register('contracts', SupplierContractViewSet)

urlpatterns = [
    path('', include(router.urls)),
]