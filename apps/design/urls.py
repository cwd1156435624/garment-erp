from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DesignFileViewSet, DesignTemplateViewSet, DesignSampleViewSet,
    DesignVersionViewSet, DesignReviewViewSet
)

router = DefaultRouter()
router.register('files', DesignFileViewSet)
router.register('templates', DesignTemplateViewSet)
router.register('samples', DesignSampleViewSet)
router.register('versions', DesignVersionViewSet)
router.register('reviews', DesignReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]