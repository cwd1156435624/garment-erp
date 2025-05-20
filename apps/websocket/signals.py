from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

from apps.notification.models import Notification
from apps.system.models_alerts import SystemAlert
from apps.production.models import Order

channel_layer = get_channel_layer()

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    """当创建新通知时，通过WebSocket发送实时更新"""
    if created and instance.user:
        # 准备通知数据
        notification_data = {
            'id': instance.id,
            'title': instance.title,
            'content': instance.content,
            'type': instance.type,
            'is_read': instance.is_read,
            'created_at': instance.created_at.isoformat()
        }
        
        # 发送到用户的通知频道
        async_to_sync(channel_layer.group_send)(
            f"user_{instance.user.id}",
            {
                'type': 'notification_message',
                'data': notification_data
            }
        )

@receiver(post_save, sender=SystemAlert)
def alert_created(sender, instance, created, **kwargs):
    """当创建新系统告警时，通过WebSocket发送实时更新"""
    if created:
        # 准备告警数据
        alert_data = {
            'id': instance.id,
            'title': instance.title,
            'content': instance.content,
            'severity': instance.severity,
            'status': instance.status,
            'created_at': instance.created_at.isoformat()
        }
        
        # 发送到所有用户的告警频道
        # 注意：这里可能需要根据权限过滤，只发送给有权查看告警的用户
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        for user in User.objects.filter(is_active=True):
            async_to_sync(channel_layer.group_send)(
                f"user_{user.id}",
                {
                    'type': 'alert_message',
                    'data': alert_data
                }
            )

@receiver(post_save, sender=Order)
def order_updated(sender, instance, created, **kwargs):
    """当订单状态更新时，通过WebSocket发送实时更新"""
    # 准备订单数据
    order_data = {
        'id': instance.id,
        'order_no': instance.order_no,
        'status': instance.status,
        'updated_at': instance.updated_at.isoformat()
    }
    
    # 发送到相关用户的订单频道
    # 这里需要确定哪些用户应该接收订单更新
    # 例如：订单创建者、负责人、客户等
    related_users = []
    
    # 添加订单创建者
    if instance.created_by:
        related_users.append(instance.created_by)
    
    # 添加订单负责人
    if hasattr(instance, 'assigned_to') and instance.assigned_to:
        related_users.append(instance.assigned_to)
    
    # 添加客户用户（如果适用）
    if hasattr(instance, 'customer') and hasattr(instance.customer, 'user') and instance.customer.user:
        related_users.append(instance.customer.user)
    
    # 发送到所有相关用户
    for user in set(related_users):  # 使用set去重
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                'type': 'order_update',
                'data': order_data
            }
        )
