from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User
from apps.production.models import Order, Batch

class Warehouse(models.Model):
    """
    仓库模型
    用于管理多个仓库信息
    """
    name = models.CharField('仓库名称', max_length=100)
    address = models.CharField('仓库地址', max_length=200)
    contact_person = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    area = models.FloatField('面积(平方米)')
    is_active = models.BooleanField('是否启用', default=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'wh_warehouse'
    
    def __str__(self):
        return self.name

class DeliveryTask(models.Model):
    """
    送货任务模型
    用于管理送货任务的分配和跟踪
    """
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('in_transit', '运输中'),
        ('delivered', '已送达'),
        ('cancelled', '已取消'),
    ]
    
    task_number = models.CharField('任务编号', max_length=50, unique=True)
    order = models.ForeignKey(Order, on_delete=models.PROTECT, verbose_name='关联订单')
    from_warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='delivery_from', verbose_name='发货仓库')
    to_address = models.CharField('送货地址', max_length=200)
    contact_person = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    delivery_date = models.DateField('送货日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    driver = models.CharField('司机', max_length=50, null=True, blank=True)
    vehicle_number = models.CharField('车牌号', max_length=20, null=True, blank=True)
    actual_delivery_time = models.DateTimeField('实际送达时间', null=True, blank=True)
    signature_image = models.ImageField('签收图片', upload_to='signatures/', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '送货任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'wh_delivery_task'
    
    def __str__(self):
        return self.task_number

class FinishedGoods(models.Model):
    """
    成品库存模型
    用于管理成品的入库、出库和库存
    """
    OPERATION_CHOICES = [
        ('in', '入库'),
        ('out', '出库'),
    ]
    
    batch = models.ForeignKey(Batch, on_delete=models.PROTECT, verbose_name='生产批次')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='仓库')
    operation_type = models.CharField('操作类型', max_length=10, choices=OPERATION_CHOICES)
    quantity = models.IntegerField('数量')
    operation_time = models.DateTimeField('操作时间', auto_now_add=True)
    operator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='操作人')
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '成品库存'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'wh_finished_goods'
    
    def __str__(self):
        return f'{self.batch} - {self.get_operation_type_display()}'