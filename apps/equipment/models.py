from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User

class Equipment(models.Model):
    """
    设备模型
    用于存储设备基本信息
    """
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('maintenance', '维护中'),
        ('malfunction', '故障'),
        ('scrapped', '已报废'),
    ]
    
    TYPE_CHOICES = [
        ('production', '生产设备'),
        ('testing', '测试设备'),
        ('packaging', '包装设备'),
        ('other', '其他'),
    ]
    
    name = models.CharField('设备名称', max_length=100)
    equipment_type = models.CharField('设备类型', max_length=20, choices=TYPE_CHOICES)
    model_number = models.CharField('型号', max_length=50)
    serial_number = models.CharField('序列号', max_length=50, unique=True)
    manufacturer = models.CharField('制造商', max_length=100)
    purchase_date = models.DateField('购买日期')
    warranty_period = models.IntegerField('保修期(月)')
    location = models.CharField('存放位置', max_length=100)
    responsible_person = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='负责人')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    specifications = models.TextField('技术规格', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '设备'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'eqp_equipment'
    
    def __str__(self):
        return self.name

class MaintenanceRecord(models.Model):
    """
    设备维护记录模型
    用于记录设备的维护保养信息
    """
    TYPE_CHOICES = [
        ('routine', '例行保养'),
        ('repair', '维修'),
        ('inspection', '检查'),
        ('upgrade', '升级改造'),
    ]
    
    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='设备')
    maintenance_type = models.CharField('维护类型', max_length=20, choices=TYPE_CHOICES)
    start_time = models.DateTimeField('开始时间')
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    maintenance_cost = models.DecimalField('维护成本', max_digits=10, decimal_places=2, default=0)
    parts_replaced = models.TextField('更换配件', null=True, blank=True)
    maintenance_details = models.TextField('维护详情')
    performed_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='performed_maintenance', verbose_name='执行人')
    verified_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='verified_maintenance', null=True, blank=True, verbose_name='验证人')
    remarks = models.TextField('备注', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '维护记录'
        verbose_name_plural = verbose_name
        ordering = ['-start_time']
        db_table = 'eqp_maintenance_record'
    
    def __str__(self):
        return f'{self.equipment} - {self.get_maintenance_type_display()}'

class FaultRecord(models.Model):
    """
    设备故障记录模型
    用于记录设备故障信息
    """
    STATUS_CHOICES = [
        ('reported', '已报修'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('closed', '已结案'),
    ]

    equipment = models.ForeignKey(Equipment, on_delete=models.PROTECT, verbose_name='设备')
    fault_time = models.DateTimeField('故障时间')
    description = models.TextField('故障描述')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='reported')
    repair_person = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='维修人员')
    solution = models.TextField('解决方案', null=True, blank=True)
    resolved_time = models.DateTimeField('解决时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    is_deleted = models.BooleanField('是否删除', default=False)
    history = HistoricalRecords()

    class Meta:
        verbose_name = '故障记录'
        verbose_name_plural = verbose_name
        ordering = ['-fault_time']
        db_table = 'eqp_fault_record'

    def __str__(self):
        return f'{self.equipment} - {self.get_status_display()}'