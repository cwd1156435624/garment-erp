import os
import uuid
import logging
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import DesignFile, DesignTemplate, DesignSample, DesignVersion, DesignReview
from .serializers import (
    DesignFileSerializer, DesignTemplateSerializer, DesignSampleSerializer,
    DesignVersionSerializer, DesignReviewSerializer, DesignFileUploadResponseSerializer
)

# 创建一个内部帮助函数来获取有效的User实例
def _get_valid_user_instance(user_data):
    """确保获取有效的User实例对象"""
    from apps.users.models import User
    logger = logging.getLogger('django')
    
    if isinstance(user_data, User):
        return user_data
        
    try:
        if hasattr(user_data, 'id'):
            return User.objects.get(id=user_data.id)
        elif hasattr(user_data, 'pk'):
            return User.objects.get(id=user_data.pk)
        elif isinstance(user_data, (int, str)):
            return User.objects.get(id=int(user_data))
        else:
            logger.error(f"Unknown user data type: {type(user_data)}")
    except (User.DoesNotExist, ValueError, TypeError) as e:
        logger.error(f"Failed to get User instance for {user_data}: {e}")
    
    # 如果不能获取用户实例，使用默认管理员
    return User.objects.filter(is_superuser=True).first()

class DesignFileViewSet(viewsets.ModelViewSet):
    """设计稿文件视图集"""
    queryset = DesignFile.objects.all()
    serializer_class = DesignFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        
        serializer.save(
            created_by=current_user,
            updated_by=current_user,
            designer=current_user
        )
    
    def perform_update(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(updated_by=current_user)
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload_file(self, request):
        """上传设计稿文件"""
        import logging
        logger = logging.getLogger('django')
        
        logger.info(f"Received file upload request. POST data: {request.POST}, FILES: {list(request.FILES.keys())}")
        
        # 同时支持'file'和'design_file'字段
        if 'file' in request.FILES:
            file = request.FILES['file']
            logger.info(f"Using 'file' field. Filename: {file.name}, Size: {file.size}")
        elif 'design_file' in request.FILES:
            file = request.FILES['design_file']
            logger.info(f"Using 'design_file' field. Filename: {file.name}, Size: {file.size}")
        else:
            logger.error("No file provided in the request")
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 处理文件类型和名称元数据
        file_type = request.POST.get('file_type', file.content_type)
        file_name = request.POST.get('file_name', file.name)
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file_name)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        # 构建存储路径
        relative_path = f"design_files/{timezone.now().strftime('%Y/%m/%d')}/{unique_filename}"
        
        try:
            file_path = default_storage.save(relative_path, ContentFile(file.read()))
            logger.info(f"File saved successfully at {file_path}")
            
            # 生成URL - 处理相对路径和绝对路径
            media_url = settings.MEDIA_URL if settings.MEDIA_URL else '/media/'
            if not media_url.endswith('/'):
                media_url += '/'
            
            # 确保我们不会在相对路径前添加域名
            if file_path.startswith('/'):
                file_url = f"{media_url}{file_path[1:]}"
            else:
                file_url = f"{media_url}{file_path}"
                
            logger.info(f"Generated file URL: {file_url}")
            
            # 返回文件信息
            response_data = {
                'id': uuid.uuid4().int >> 64,  # 生成一个临时ID
                'url': file_url,
                'filename': file_name,
                'file_type': file_type
            }
            
            # 采用推荐的标准响应格式，包含success、message和data字段
            from django.http import JsonResponse
            
            # 构建标准响应格式
            standard_response = {
                "success": True,
                "message": "文件上传成功",
                "data": {
                    "fileUrl": file_url,
                    "filename": unique_filename,  # 服务器重命名后的文件名
                    "originalFilename": file_name,  # 原始文件名
                    "id": response_data['id'],  # 文件唯一ID
                    "fileType": file_type,  # 文件类型
                    "size": file.size  # 文件大小
                }
            }
            
            logger.info(f"Returning standardized response: {standard_response}")
            return JsonResponse(standard_response, status=200)
                
        except Exception as e:
            logger.exception(f"Error saving file: {str(e)}")
            return Response({"error": f"Error saving file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """审批设计稿"""
        design_file = self.get_object()
        design_file.status = 'approved'
        design_file.review_comment = request.data.get('comment', '')
        design_file.save(update_fields=['status', 'review_comment', 'updated_at'])
        
        # 获取有效的User实例并创建审核记录
        current_user = _get_valid_user_instance(request.user)
        DesignReview.objects.create(
            design_file=design_file,
            reviewer=current_user,
            status='approved',
            comment=request.data.get('comment', ''),
            created_by=current_user,
            updated_by=current_user
        )
        
        return Response({'status': 'approved'})
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """拒绝设计稿"""
        design_file = self.get_object()
        design_file.status = 'rejected'
        design_file.review_comment = request.data.get('comment', '')
        design_file.save(update_fields=['status', 'review_comment', 'updated_at'])
        
        # 获取有效的User实例并创建审核记录
        current_user = _get_valid_user_instance(request.user)
        DesignReview.objects.create(
            design_file=design_file,
            reviewer=current_user,
            status='rejected',
            comment=request.data.get('comment', ''),
            created_by=current_user,
            updated_by=current_user
        )
        
        return Response({'status': 'rejected'})
    
    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        """发布设计稿"""
        design_file = self.get_object()
        
        if design_file.status != 'approved':
            return Response(
                {"error": "Only approved design files can be published"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        design_file.status = 'published'
        design_file.publish_date = timezone.now()
        design_file.save(update_fields=['status', 'publish_date', 'updated_at'])
        
        return Response({'status': 'published'})

class DesignTemplateViewSet(viewsets.ModelViewSet):
    """设计模板视图集"""
    queryset = DesignTemplate.objects.all()
    serializer_class = DesignTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(created_by=current_user, updated_by=current_user)
    
    def perform_update(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(updated_by=current_user)

class DesignSampleViewSet(viewsets.ModelViewSet):
    """设计样品视图集"""
    queryset = DesignSample.objects.all()
    serializer_class = DesignSampleSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(created_by=current_user, updated_by=current_user)
    
    def perform_update(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(updated_by=current_user)

class DesignVersionViewSet(viewsets.ModelViewSet):
    """设计稿版本视图集"""
    queryset = DesignVersion.objects.all()
    serializer_class = DesignVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(created_by=current_user, updated_by=current_user)
    
    def perform_update(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(updated_by=current_user)

class DesignReviewViewSet(viewsets.ModelViewSet):
    """设计稿审核视图集"""
    queryset = DesignReview.objects.all()
    serializer_class = DesignReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(created_by=current_user, updated_by=current_user, reviewer=current_user)
    
    def perform_update(self, serializer):
        # 使用帮助函数获取有效的User实例
        current_user = _get_valid_user_instance(self.request.user)
        serializer.save(updated_by=current_user)
