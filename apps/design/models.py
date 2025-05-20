from django.db import models
from django.conf import settings
from apps.system.models import BaseModel

class DesignFile(BaseModel):
    """设计稿文件模型"""
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('reviewing', '审核中'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('published', '已发布'),
    )
    
    name = models.CharField(max_length=200, verbose_name='设计稿名称')
    version = models.CharField(max_length=50, verbose_name='版本号')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                               null=True, related_name='design_files', verbose_name='设计师')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    
    file_url = models.URLField(max_length=500, verbose_name='文件URL')
    file_name = models.CharField(max_length=200, verbose_name='文件名称')
    file_size = models.PositiveIntegerField(default=0, verbose_name='文件大小(字节)')
    file_type = models.CharField(max_length=50, blank=True, null=True, verbose_name='文件类型')
    
    review_comment = models.TextField(blank=True, null=True, verbose_name='审核意见')
    publish_date = models.DateTimeField(blank=True, null=True, verbose_name='发布日期')
    
    class Meta:
        verbose_name = '设计稿文件'
        verbose_name_plural = '设计稿文件'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"

class DesignTemplate(BaseModel):
    """设计模板模型"""
    name = models.CharField(max_length=200, verbose_name='模板名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    file_url = models.URLField(max_length=500, verbose_name='文件URL')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    
    class Meta:
        verbose_name = '设计模板'
        verbose_name_plural = '设计模板'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name

class DesignSample(BaseModel):
    """设计样品模型"""
    name = models.CharField(max_length=200, verbose_name='样品名称')
    description = models.TextField(blank=True, null=True, verbose_name='描述')
    file_url = models.URLField(max_length=500, verbose_name='图片URL')
    reference_number = models.CharField(max_length=100, blank=True, null=True, verbose_name='参考编号')
    
    class Meta:
        verbose_name = '设计样品'
        verbose_name_plural = '设计样品'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name

class DesignVersion(BaseModel):
    """设计稿版本模型"""
    design_file = models.ForeignKey(DesignFile, on_delete=models.CASCADE, 
                                   related_name='versions', verbose_name='设计稿')
    version_number = models.CharField(max_length=50, verbose_name='版本号')
    file_url = models.URLField(max_length=500, verbose_name='文件URL')
    changelog = models.TextField(blank=True, null=True, verbose_name='变更记录')
    
    class Meta:
        verbose_name = '设计稿版本'
        verbose_name_plural = '设计稿版本'
        ordering = ['-created_at']
        unique_together = ('design_file', 'version_number')
    
    def __str__(self):
        return f"{self.design_file.name} v{self.version_number}"

class DesignReview(BaseModel):
    """设计稿审核模型"""
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    )
    
    design_file = models.ForeignKey(DesignFile, on_delete=models.CASCADE, 
                                   related_name='reviews', verbose_name='设计稿')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                               null=True, related_name='design_reviews', verbose_name='审核人')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='审核状态')
    comment = models.TextField(blank=True, null=True, verbose_name='审核意见')
    
    class Meta:
        verbose_name = '设计稿审核'
        verbose_name_plural = '设计稿审核'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.design_file.name} - {self.get_status_display()}"
