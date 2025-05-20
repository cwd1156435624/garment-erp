from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, TaskReminderViewSet

router = DefaultRouter()
router.register('customers', CustomerViewSet)
router.register('task-reminders', TaskReminderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]