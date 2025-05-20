from rest_framework import serializers
from .models_notice import Notice, NoticeReadRecord

class NoticeSerializer(serializers.ModelSerializer):
    """系统公告序列化器"""
    created_by_name = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'priority', 'status',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
            'published_at', 'expired_at', 'is_global', 'is_read'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.username if obj.created_by else None
    
    def get_is_read(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return NoticeReadRecord.objects.filter(user=request.user, notice=obj).exists()
        return False


class NoticeReadRecordSerializer(serializers.ModelSerializer):
    """公告阅读记录序列化器"""
    class Meta:
        model = NoticeReadRecord
        fields = ['id', 'user', 'notice', 'read_at']
        read_only_fields = ['read_at']
