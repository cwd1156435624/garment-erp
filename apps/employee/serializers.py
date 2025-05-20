from rest_framework import serializers
from .models import Employee, Attendance, PerformanceEvaluation

class EmployeeSerializer(serializers.ModelSerializer):
    """员工序列化器"""
    class Meta:
        model = Employee
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class AttendanceSerializer(serializers.ModelSerializer):
    """考勤记录序列化器"""
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

class PerformanceEvaluationSerializer(serializers.ModelSerializer):
    """绩效评估序列化器"""
    class Meta:
        model = PerformanceEvaluation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']