from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FactorySettlementViewSet, OutsourceSettlementViewSet, PaymentViewSet, CostCalculationViewSet

router = DefaultRouter()
router.register('factory-settlements', FactorySettlementViewSet)
router.register('outsource-settlements', OutsourceSettlementViewSet)
router.register('payments', PaymentViewSet)
router.register('cost-calculations', CostCalculationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]