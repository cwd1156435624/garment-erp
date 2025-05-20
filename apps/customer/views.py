from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Customer, TaskReminder
from .serializers import CustomerSerializer, TaskReminderSerializer
from apps.system.utils import ResponseWrapper
from rest_framework.permissions import IsAuthenticated

class CustomerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    """客户管理视图集"""
    queryset = Customer.objects.filter(is_deleted=False)
    serializer_class = CustomerSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def update_credit_limit(self, request, pk=None):
        """更新客户信用额度"""
        try:
            customer = self.get_object()
            new_limit = request.data.get('credit_limit')
            if new_limit is None:
                return ResponseWrapper.error('信用额度不能为空')
            customer.credit_limit = new_limit
            customer.save()
            return ResponseWrapper.success(CustomerSerializer(customer).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class TaskReminderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    """任务提醒视图集"""
    queryset = TaskReminder.objects.filter(is_deleted=False)
    serializer_class = TaskReminderSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        """完成任务"""
        try:
            task = self.get_object()
            if task.status == 'completed':
                return ResponseWrapper.error('任务已完成')
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.completed_by = request.user
            task.save()
            return ResponseWrapper.success(TaskReminderSerializer(task).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))