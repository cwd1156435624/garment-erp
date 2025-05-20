from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Employee, Attendance, PerformanceEvaluation
from .serializers import EmployeeSerializer, AttendanceSerializer, PerformanceEvaluationSerializer
from apps.system.utils import ResponseWrapper

class EmployeeViewSet(viewsets.ModelViewSet):
    """员工管理视图集"""
    queryset = Employee.objects.filter(is_deleted=False)
    serializer_class = EmployeeSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """更改员工状态"""
        try:
            employee = self.get_object()
            new_status = request.data.get('status')
            if new_status not in dict(Employee.STATUS_CHOICES):
                return ResponseWrapper.error('无效的状态值')
            employee.status = new_status
            employee.save()
            return ResponseWrapper.success(EmployeeSerializer(employee).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class AttendanceViewSet(viewsets.ModelViewSet):
    """考勤记录视图集"""
    queryset = Attendance.objects.filter(is_deleted=False)
    serializer_class = AttendanceSerializer
    
    def perform_create(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        """员工打卡"""
        try:
            employee_id = request.data.get('employee')
            attendance_type = request.data.get('attendance_type')
            location = request.data.get('location')
            
            if not all([employee_id, attendance_type]):
                return ResponseWrapper.error('缺少必要参数')
                
            attendance = Attendance.objects.create(
                employee_id=employee_id,
                attendance_type=attendance_type,
                attendance_date=timezone.now().date(),
                attendance_time=timezone.now(),
                location=location,
                device=request.META.get('HTTP_USER_AGENT', '')
            )
            return ResponseWrapper.success(AttendanceSerializer(attendance).data)
        except Exception as e:
            return ResponseWrapper.error(str(e))

class PerformanceEvaluationViewSet(viewsets.ModelViewSet):
    """绩效评估视图集"""
    queryset = PerformanceEvaluation.objects.filter(is_deleted=False)
    serializer_class = PerformanceEvaluationSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()