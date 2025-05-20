from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from .serializers import UserSerializer, UserListSerializer
from .models import User

class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集
    提供用户的增删改查、登录、注册等功能
    """
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """
        根据不同的操作返回不同的序列化器
        """
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_permissions(self):
        """
        根据不同的操作设置不同的权限
        """
        if self.action in ['create', 'login']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def perform_create(self, serializer):
        """
        创建用户时的额外操作
        新注册用户默认为未激活状态，需要管理员审核
        """
        # 如果是管理员创建用户，则直接激活
        is_active = False
        if self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser):
            is_active = True
            
        user = serializer.save(is_active=is_active)
        if hasattr(self.request, 'META') and 'REMOTE_ADDR' in self.request.META:
            user.last_login_ip = self.request.META['REMOTE_ADDR']
            user.save(update_fields=['last_login_ip', 'is_active'])
    
    def perform_destroy(self, instance):
        """
        软删除用户
        """
        instance.is_deleted = True
        instance.save(update_fields=['is_deleted'])
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """
        用户登录
        """
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response(
                {'error': '请提供用户名和密码'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'error': '用户名或密码错误'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if user.is_deleted:
            return Response(
                {'error': '该用户已被删除'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        if not user.is_active:
            return Response(
                {'error': '该用户账号尚未激活，请等待管理员审核'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 更新最后登录时间和IP
        user.last_login = timezone.now()
        if 'REMOTE_ADDR' in request.META:
            user.last_login_ip = request.META['REMOTE_ADDR']
        user.save(update_fields=['last_login', 'last_login_ip'])
        
        # 生成JWT令牌
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            },
            'user': UserSerializer(user).data
        })
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """
        获取当前用户信息
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        修改密码
        """
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([old_password, new_password, confirm_password]):
            return Response(
                {'error': '请提供所有必要的密码字段'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': '两次输入的新密码不匹配'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {'error': '原密码错误'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        return Response({'message': '密码修改成功'})
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        重置用户密码
        请求参数：{
            "new_password": "新密码",
            "confirm_password": "确认密码"
        }
        """
        try:
            user = self.get_object()
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            if not new_password or new_password != confirm_password:
                return Response({'error': '密码不匹配或为空'}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save(update_fields=['password'])
            return Response({'message': '密码重置成功', 'user_id': user.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        审核用户注册
        只有管理员或超级管理员可以审核用户
        """
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({'error': '没有权限执行此操作'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            user = self.get_object()
            user.is_active = True
            user.save(update_fields=['is_active'])
            return Response({'message': '用户已激活', 'user_id': user.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        获取待审核用户列表
        只有管理员或超级管理员可以查看待审核用户
        """
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({'error': '没有权限执行此操作'}, status=status.HTTP_403_FORBIDDEN)
            
        pending_users = User.objects.filter(is_active=False, is_deleted=False)
        page = self.paginate_queryset(pending_users)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(pending_users, many=True)
        return Response(serializer.data)