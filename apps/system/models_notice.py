from django.db import models
from apps.users.models import User
from django.utils.translation import gettext_lazy as _

class Notice(models.Model):
    """系统公告模型"""
    PRIORITY_CHOICES = (
        ('low', _('低')),
        ('medium', _('中')),
        ('high', _('高')),
        ('urgent', _('紧急')),
    )
    
    STATUS_CHOICES = (
        ('draft', _('草稿')),
        ('published', _('已发布')),
        ('expired', _('已过期')),
    )
    
    title = models.CharField(_('标题'), max_length=200)
    content = models.TextField(_('内容'))
    priority = models.CharField(_('优先级'), max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_('状态'), max_length=10, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notices', verbose_name=_('创建人'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    published_at = models.DateTimeField(_('发布时间'), null=True, blank=True)
    expired_at = models.DateTimeField(_('过期时间'), null=True, blank=True)
    
    # 通知范围 (全部用户、特定部门、特定角色等)
    is_global = models.BooleanField(_('全局通知'), default=False)
    # 存储部门和角色名称列表，使用JSON字段
    departments = models.JSONField(_('部门范围'), default=list, blank=True, help_text='部门名称列表，如 ["研发部", "市场部"]')
    roles = models.JSONField(_('角色范围'), default=list, blank=True, help_text='角色名称列表，如 ["admin", "manager"]')
    
    # 已读记录
    read_by = models.ManyToManyField(User, through='NoticeReadRecord', related_name='read_notices', verbose_name=_('已读用户'))
    
    class Meta:
        verbose_name = _('系统公告')
        verbose_name_plural = _('系统公告')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class NoticeReadRecord(models.Model):
    """公告阅读记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('用户'))
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, verbose_name=_('公告'))
    read_at = models.DateTimeField(_('阅读时间'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('公告阅读记录')
        verbose_name_plural = _('公告阅读记录')
        unique_together = ('user', 'notice')
