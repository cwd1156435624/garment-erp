from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import FactorySettlement, OutsourceSettlement, Payment, CostCalculation
from .serializers import FactorySettlementSerializer, OutsourceSettlementSerializer, PaymentSerializer, CostCalculationSerializer
from apps.system.utils import ResponseWrapper
from rest_framework.permissions import IsAuthenticated

class FactorySettlementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    """工厂结算单视图集"""
    queryset = FactorySettlement.objects.filter(is_deleted=False)
    serializer_class = FactorySettlementSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审核结算单"""
        try:
            settlement = self.get_object()
            if settlement.status != 'pending':
                return ResponseWrapper.error('结算单状态不正确')
            settlement.status = 'approved'
            settlement.approved_by = request.user
            settlement.approved_at = timezone.now()
            settlement.save()
            return ResponseWrapper.success(FactorySettlementSerializer(settlement).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class OutsourceSettlementViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    """外发结算单视图集"""
    queryset = OutsourceSettlement.objects.filter(is_deleted=False)
    serializer_class = OutsourceSettlementSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审核结算单"""
        try:
            settlement = self.get_object()
            if settlement.status != 'pending':
                return ResponseWrapper.error('结算单状态不正确')
            settlement.status = 'approved'
            settlement.approved_by = request.user
            settlement.approved_at = timezone.now()
            settlement.save()
            return ResponseWrapper.success(OutsourceSettlementSerializer(settlement).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class PaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    """付款计划视图集"""
    queryset = Payment.objects.filter(is_deleted=False)
    serializer_class = PaymentSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def complete_payment(self, request, pk=None):
        """完成付款"""
        try:
            payment = self.get_object()
            if payment.status == 'completed':
                return ResponseWrapper.error('付款已完成')
            payment.status = 'completed'
            payment.payment_date = timezone.now()
            payment.save()
            return ResponseWrapper.success(PaymentSerializer(payment).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class CostCalculationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    """成本核算视图集"""
    queryset = CostCalculation.objects.filter(is_deleted=False)
    serializer_class = CostCalculationSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()