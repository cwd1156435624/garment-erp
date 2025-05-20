from django.db import models
from apps.users.models import User
from .models import BaseModel

class SystemAlert(BaseModel):
    """
    系统告警模型
    用于存储系统的各类告警信息
    """
    SEVERITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('critical', '严重'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活动'),
        ('resolved', '已解决'),
        ('ignored', '已忽略'),
    ]
    
    title = models.CharField('告警标题', max_length=200)
    content = models.TextField('告警内容')
    severity = models.CharField('严重程度', max_length=20, choices=SEVERITY_CHOICES, default='medium')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    source = models.CharField('告警来源', max_length=100)
    resolved_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, 
                                   related_name='resolved_alerts', verbose_name='处理人')
    resolved_at = models.DateTimeField('处理时间', null=True, blank=True)
    resolution_comment = models.TextField('处理说明', null=True, blank=True)
    
    class Meta:
        verbose_name = '系统告警'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'sys_alert'
    
    def __str__(self):
        return f'{self.title} - {self.severity} - {self.status}'