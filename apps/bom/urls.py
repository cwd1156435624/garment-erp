from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BOMViewSet, MaterialListViewSet, ProcessRequirementViewSet,
    TechnicalSpecViewSet, QualityStandardViewSet
)

router = DefaultRouter()
router.register('bom-list', BOMViewSet, basename='bom')
router.register('material-list', MaterialListViewSet, basename='material-list')
router.register('process-requirements', ProcessRequirementViewSet, basename='process-requirements')
router.register('technical-specs', TechnicalSpecViewSet, basename='technical-specs')
router.register('quality-standards', QualityStandardViewSet, basename='quality-standards')

urlpatterns = [
    path('', include(router.urls)),
]