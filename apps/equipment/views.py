from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Equipment, MaintenanceRecord, FaultRecord
from .serializers import EquipmentSerializer, MaintenanceRecordSerializer, FaultRecordSerializer

class EquipmentViewSet(viewsets.ModelViewSet):
    """
    设备管理视图集
    提供设备的增删改查功能
    """
    queryset = Equipment.objects.filter(is_deleted=False)
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_destroy(self, instance):
        """
        重写删除方法，实现软删除
        """
        instance.is_deleted = True
        instance.save()
    
    def get_queryset(self):
        """
        重写查询集方法，支持按设备类型、状态等筛选
        """
        queryset = super().get_queryset()
        equipment_type = self.request.query_params.get('equipment_type')
        status = self.request.query_params.get('status')
        location = self.request.query_params.get('location')
        
        if equipment_type:
            queryset = queryset.filter(equipment_type=equipment_type)
        if status:
            queryset = queryset.filter(status=status)
        if location:
            queryset = queryset.filter(location=location)
            
        return queryset

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """
    设备维护记录视图集
    提供维护记录的增删改查功能
    """
    queryset = MaintenanceRecord.objects.filter(is_deleted=False)
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_destroy(self, instance):
        """
        重写删除方法，实现软删除
        """
        instance.is_deleted = True
        instance.save()
    
    def get_queryset(self):
        """
        重写查询集方法，支持按设备、维护类型等筛选
        """
        queryset = super().get_queryset()
        equipment_id = self.request.query_params.get('equipment_id')
        maintenance_type = self.request.query_params.get('maintenance_type')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        
        if equipment_id:
            queryset = queryset.filter(equipment_id=equipment_id)
        if maintenance_type:
            queryset = queryset.filter(maintenance_type=maintenance_type)
        if start_time:
            queryset = queryset.filter(start_time__gte=start_time)
        if end_time:
            queryset = queryset.filter(end_time__lte=end_time)
            
        return queryset

class FaultRecordViewSet(viewsets.ModelViewSet):
    """
    故障记录视图集
    提供故障记录的增删改查功能
    """
    queryset = FaultRecord.objects.filter(is_deleted=False)
    serializer_class = FaultRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_destroy(self, instance):
        """
        重写删除方法，实现软删除
        """
        instance.is_deleted = True
        instance.save()
    
    def get_queryset(self):
        """
        重写查询集方法，支持按设备、状态等筛选
        """
        queryset = super().get_queryset()
        equipment_id = self.request.query_params.get('equipment_id')
        status = self.request.query_params.get('status')
        severity = self.request.query_params.get('severity')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        
        if equipment_id:
            queryset = queryset.filter(equipment_id=equipment_id)
        if status:
            queryset = queryset.filter(status=status)
        if severity:
            queryset = queryset.filter(severity=severity)
        if start_time:
            queryset = queryset.filter(occurrence_time__gte=start_time)
        if end_time:
            queryset = queryset.filter(occurrence_time__lte=end_time)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """
        更新故障记录状态
        """
        instance = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(FaultRecord.STATUS_CHOICES):
            return Response({'error': '无效的状态值'}, status=status.HTTP_400_BAD_REQUEST)
        
        instance.status = new_status
        if new_status == 'resolved':
            instance.resolution_time = timezone.now()
            instance.downtime = instance.resolution_time - instance.occurrence_time
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        分配故障处理人员
        """
        instance = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        if not assigned_to_id:
            return Response({'error': '请指定处理人员'}, status=status.HTTP_400_BAD_REQUEST)
        
        instance.assigned_to_id = assigned_to_id
        instance.status = 'processing'
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取故障统计信息
        """
        total_count = self.get_queryset().count()
        pending_count = self.get_queryset().filter(status='pending').count()
        processing_count = self.get_queryset().filter(status='processing').count()
        resolved_count = self.get_queryset().filter(status='resolved').count()
        closed_count = self.get_queryset().filter(status='closed').count()
        
        by_severity = {
            severity: self.get_queryset().filter(severity=severity).count()
            for severity, _ in FaultRecord.SEVERITY_CHOICES
        }
        
        return Response({
            'total': total_count,
            'by_status': {
                'pending': pending_count,
                'processing': processing_count,
                'resolved': resolved_count,
                'closed': closed_count
            },
            'by_severity': by_severity
        })