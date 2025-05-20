from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from django.http import HttpResponse
from prometheus_client import multiprocess, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import os
import json
from datetime import datetime
from .utils import ResponseWrapper
from .models import OperationLog
from .serializers import SystemParameterSerializer, OperationLogSerializer

class MetricsView(APIView):
    """Prometheus指标导出视图
    
    提供Prometheus监控指标的导出接口，用于监控系统运行状态
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        data = generate_latest(registry)
        return HttpResponse(
            data,
            content_type=CONTENT_TYPE_LATEST
        )


class BaseViewSet(viewsets.ModelViewSet):
    """基础视图集，提供统一的响应格式"""

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return ResponseWrapper.success(self.get_paginated_response(serializer.data).data)
        serializer = self.get_serializer(queryset, many=True)
        return ResponseWrapper.success(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return ResponseWrapper.success(serializer.data, '创建成功')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return ResponseWrapper.success(serializer.data, '更新成功')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return ResponseWrapper.success(None, '删除成功')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return ResponseWrapper.success(serializer.data)