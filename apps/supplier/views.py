from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Supplier, SupplierPerformance, SupplierContract
from .serializers import SupplierSerializer, SupplierPerformanceSerializer, SupplierContractSerializer
from apps.system.utils import ResponseWrapper

class SupplierViewSet(viewsets.ModelViewSet):
    """供应商管理视图集"""
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = SupplierSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """更改供应商状态"""
        try:
            supplier = self.get_object()
            new_status = request.data.get('status')
            if new_status not in dict(Supplier.STATUS_CHOICES):
                return ResponseWrapper.error('无效的状态值')
            supplier.status = new_status
            supplier.save()
            return ResponseWrapper.success(SupplierSerializer(supplier).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class SupplierPerformanceViewSet(viewsets.ModelViewSet):
    """供应商绩效评估视图集"""
    queryset = SupplierPerformance.objects.filter(is_deleted=False)
    serializer_class = SupplierPerformanceSerializer
    
    def perform_create(self, serializer):
        serializer.save(evaluated_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class SupplierContractViewSet(viewsets.ModelViewSet):
    """供应商合同视图集"""
    queryset = SupplierContract.objects.filter(is_deleted=False)
    serializer_class = SupplierContractSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def activate_contract(self, request, pk=None):
        """激活合同"""
        try:
            contract = self.get_object()
            if contract.status != 'draft':
                return ResponseWrapper.error('合同状态不正确')
            contract.status = 'active'
            contract.save()
            return ResponseWrapper.success(SupplierContractSerializer(contract).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))