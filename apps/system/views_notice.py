from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models_notice import Notice, NoticeReadRecord
from .serializers_notice import NoticeSerializer, NoticeReadRecordSerializer

class NoticeViewSet(viewsets.ModelViewSet):
    """系统公告视图集"""
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """重写list方法，返回前端期望的数据格式"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # 处理前端传递的参数
        notice_type = request.query_params.get('type')
        ordering = request.query_params.get('ordering')
        
        # 应用过滤条件
        if notice_type == 'announcement':
            # 这里可以根据实际情况添加类型过滤
            pass
        
        # 应用排序
        if ordering:
            if ordering.startswith('-'):
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by(ordering)
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        # 返回前端期望的格式，包含 results 字段
        return Response({
            'results': serializer.data,
            'count': len(serializer.data)
        })
    
    def get_queryset(self):
        """根据用户权限和角色过滤公告"""
        # 如果是 Swagger 生成 schema，则返回全部查询集
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset
            
        user = self.request.user
        now = timezone.now()
        
        # 匿名用户只能看到全局公告
        if not user.is_authenticated:
            return self.queryset.filter(
                status='published',
                published_at__lte=now,
                is_global=True
            ).filter(
                Q(expired_at__isnull=True) | Q(expired_at__gt=now)
            )
        
        # 管理员可以看到所有公告
        if user.is_staff or user.is_superuser:
            return self.queryset
        
        # 获取用户的部门和角色
        user_department = getattr(user, 'department', None)
        user_role = getattr(user, 'role', None)
        
        # 普通用户只能看到已发布且未过期的公告，且需要符合用户的部门或角色
        queryset = self.queryset.filter(
            status='published',
            published_at__lte=now
        ).filter(
            Q(expired_at__isnull=True) | Q(expired_at__gt=now)
        )
        
        # 过滤条件：全局公告或针对用户部门/角色的公告
        department_role_filter = Q(is_global=True)
        
        # 如果用户有部门，添加部门过滤条件
        if user_department:
            # 使用 JSON 包含查询
            department_role_filter |= Q(departments__contains=[user_department])
        
        # 如果用户有角色，添加角色过滤条件
        if user_role:
            # 使用 JSON 包含查询
            department_role_filter |= Q(roles__contains=[user_role])
        
        queryset = queryset.filter(department_role_filter).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """创建公告时自动设置创建人"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """标记公告为已读"""
        notice = self.get_object()
        user = request.user
        
        # 检查是否已经标记为已读
        if NoticeReadRecord.objects.filter(user=user, notice=notice).exists():
            return Response({'detail': '公告已经标记为已读'}, status=status.HTTP_200_OK)
        
        # 创建已读记录
        NoticeReadRecord.objects.create(user=user, notice=notice)
        return Response({'detail': '公告已标记为已读'}, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """获取用户未读公告"""
        user = request.user
        queryset = self.get_queryset()
        
        # 过滤出用户未读的公告
        unread_notices = queryset.exclude(
            read_by=user
        )
        
        page = self.paginate_queryset(unread_notices)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unread_notices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """获取当前有效的公告（已发布且未过期）"""
        now = timezone.now()
        queryset = self.get_queryset().filter(
            status='published',
            published_at__lte=now
        ).filter(
            Q(expired_at__isnull=True) | Q(expired_at__gt=now)
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
