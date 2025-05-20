from django.db import models
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords

class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='权限组',
        blank=True,
        related_name='custom_user_groups',
        help_text='用户所属的权限组'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='用户权限',
        blank=True,
        related_name='custom_user_permissions',
        help_text='用户的特定权限'
    )
    """
    用户模型
    继承Django默认用户模型，添加额外字段
    """
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('manager', '经理'),
        ('staff', '员工'),
    ]
    
    phone = models.CharField('手机号', max_length=11, unique=True, null=True, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='staff')
    department = models.CharField('部门', max_length=50, null=True, blank=True)
    position = models.CharField('职位', max_length=50, null=True, blank=True)
    avatar = models.ImageField('头像', upload_to='avatars/', null=True, blank=True)
    last_login_ip = models.GenericIPAddressField('最后登录IP', null=True, blank=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'sys_user'
    
    def __str__(self):
        return self.username