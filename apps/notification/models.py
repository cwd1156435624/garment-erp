from django.db import models
from django.utils import timezone
from django.conf import settings

class Notification(models.Model):
    """
    通知模型
    """
    TYPE_CHOICES = (
        ('system', '系统通知'),
        ('order', '订单通知'),
        ('material', '物料通知'),
        ('task', '任务通知'),
        ('alert', '告警通知'),
    )
    
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system', verbose_name='类型')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name='用户')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
