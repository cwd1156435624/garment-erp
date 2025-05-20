from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    """
    class Meta:
        model = Notification
        fields = ['id', 'title', 'content', 'type', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']
