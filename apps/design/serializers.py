from rest_framework import serializers
from .models import DesignFile, DesignTemplate, DesignSample, DesignVersion, DesignReview
from django.db import IntegrityError
from django.conf import settings
import re

class DesignFileSerializer(serializers.ModelSerializer):
    """设计稿文件序列化器"""
    designer_name = serializers.SerializerMethodField()
    file_url = serializers.CharField(max_length=500)
    
    # 添加前端可能提交但模型中不存在的字段
    style_no = serializers.CharField(required=False, write_only=True, allow_blank=True)
    quantity = serializers.IntegerField(required=False, write_only=True)
    color = serializers.CharField(required=False, write_only=True, allow_blank=True)
    size = serializers.CharField(required=False, write_only=True, allow_blank=True)
    other_info = serializers.CharField(required=False, write_only=True, allow_blank=True)
    materials_json = serializers.CharField(required=False, write_only=True, allow_blank=True)
    
    class Meta:
        model = DesignFile
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
    
    def get_designer_name(self, obj):
        return obj.designer.username if obj.designer else None
        
    def validate_file_url(self, value):
        """验证并转换file_url字段"""
        if not value:
            raise serializers.ValidationError("文件URL不能为空")
            
        # 如果已经是完整URL（以http://或https://开头），则直接返回
        if re.match(r'^https?://', value):
            return value
            
        # 如果是相对路径，转换为完整URL
        base_url = getattr(settings, 'BASE_URL', None)
        if not base_url:
            # 如果没有配置BASE_URL，使用一个默认值
            base_url = 'https://yagtpotihswf.sealosbja.site'
            
        # 确保路径格式正确
        if value.startswith('/'):
            value = value[1:]
            
        return f"{base_url}/{value}"
    
    def create(self, validated_data):
        """完全重写create方法来正确处理所有字段"""
        # 从上下文中获取请求对象
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not request.user.is_authenticated:
            # 如果没有有效的用户，则不能创建，或者可以设置一个默认用户（如果业务逻辑允许）
            # 这里我们选择抛出异常，因为创建者是必需的
            raise serializers.ValidationError("User must be authenticated to create a design file.")

        user = request.user

        # 首先提取并保存所有额外字段信息，包括前端特定字段和保留字段
        extra_fields = {}
        model_fields = {f.name for f in DesignFile._meta.get_fields()}

        # 移除不在模型中的字段
        for field in list(validated_data.keys()):
            if field not in model_fields:
                extra_fields[field] = validated_data.pop(field, None)
        
        # 确保 created_by 和 updated_by 被设置
        validated_data['created_by'] = user
        validated_data['updated_by'] = user

        # 如果 designer 字段也在 validated_data 中，确保它是 User 实例
        # （根据你的逻辑，designer 可能由前端提供，也可能需要从 user 推断）
        # 这里假设如果前端提供了 designer_id，它已被正确处理成 User 实例
        # 如果没有提供，可以考虑默认设置为 user
        if 'designer' not in validated_data or validated_data['designer'] is None:
             # 如果需要，取消下面一行的注释以将 designer 默认设置为创建者
             # validated_data['designer'] = user
             pass # 或者保持为空，如果允许的话

        # 调用模型的创建方法
        try:
            instance = DesignFile.objects.create(**validated_data)
        except IntegrityError as e:
            # 捕获可能的数据库完整性错误，提供更清晰的反馈
            raise serializers.ValidationError(f"Database integrity error: {e}")
        except Exception as e:
            # 捕获其他可能的创建错误
            raise serializers.ValidationError(f"Error creating design file: {e}")

        # extra_fields 可以在这里处理，例如保存到 JSON 字段或单独的模型
        # 目前我们不处理 extra_fields

        return instance

class DesignTemplateSerializer(serializers.ModelSerializer):
    """设计模板序列化器"""
    class Meta:
        model = DesignTemplate
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

class DesignSampleSerializer(serializers.ModelSerializer):
    """设计样品序列化器"""
    class Meta:
        model = DesignSample
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

class DesignVersionSerializer(serializers.ModelSerializer):
    """设计稿版本序列化器"""
    class Meta:
        model = DesignVersion
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

class DesignReviewSerializer(serializers.ModelSerializer):
    """设计稿审核序列化器"""
    reviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignReview
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    
    def get_reviewer_name(self, obj):
        return obj.reviewer.username if obj.reviewer else None

class DesignFileUploadResponseSerializer(serializers.Serializer):
    """设计稿文件上传响应序列化器"""
    id = serializers.IntegerField()
    # 使用CharField而不是URLField，以允许相对路径和非严格的URL格式
    url = serializers.CharField(max_length=500)
    filename = serializers.CharField()
    file_type = serializers.CharField(required=False)
