from django.db import models
from django.utils import timezone
from apps.system.models import BaseModel
from apps.materials.models import Material
from apps.production.models import Order
from apps.warehouse.models import Warehouse

class Barcode(BaseModel):
    """
    条码模型
    """
    TYPE_CHOICES = (
        ('material', '物料'),
        ('product', '产品'),
        ('location', '库位'),
        ('order', '订单'),
        ('process', '工序'),
        ('operator', '操作员'),
        ('package', '包装'),
        ('other', '其他'),
    )
    
    STATUS_CHOICES = (
        ('active', '激活'),
        ('used', '已使用'),
        ('disabled', '禁用'),
    )
    
    barcode_number = models.CharField(max_length=100, unique=True, verbose_name='条码号')
    barcode_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='条码类型')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    reference_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='关联ID')
    material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联物料')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联仓库')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='关联订单')
    operator_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='关联操作员ID')
    print_count = models.IntegerField(default=0, verbose_name='打印次数')
    last_print_time = models.DateTimeField(null=True, blank=True, verbose_name='最后打印时间')
    
    class Meta:
        verbose_name = '条码'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.barcode_number

class ScanningHistory(BaseModel):
    """
    扫码历史模型
    """
    OPERATION_TYPE_CHOICES = (
        ('material_inbound', '物料入库'),
        ('material_outbound', '物料出库'),
        ('production_process', '生产过程'),
        ('product_packaging', '产品包装'),
        ('inventory_check', '库存盘点'),
        ('other', '其他'),
    )
    
    barcode = models.ForeignKey(Barcode, on_delete=models.CASCADE, related_name='scanning_history', verbose_name='条码')
    operation_type = models.CharField(max_length=30, choices=OPERATION_TYPE_CHOICES, verbose_name='操作类型')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='数量')
    location_barcode = models.ForeignKey(Barcode, on_delete=models.SET_NULL, null=True, blank=True, related_name='location_scanning_history', verbose_name='库位条码')
    order_barcode = models.ForeignKey(Barcode, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_scanning_history', verbose_name='订单条码')
    process_barcode = models.ForeignKey(Barcode, on_delete=models.SET_NULL, null=True, blank=True, related_name='process_scanning_history', verbose_name='工序条码')
    operator_barcode = models.ForeignKey(Barcode, on_delete=models.SET_NULL, null=True, blank=True, related_name='operator_scanning_history', verbose_name='操作员条码')
    package_barcode = models.ForeignKey(Barcode, on_delete=models.SET_NULL, null=True, blank=True, related_name='package_scanning_history', verbose_name='包装条码')
    batch_number = models.CharField(max_length=50, blank=True, null=True, verbose_name='批次号')
    result = models.CharField(max_length=20, default='success', verbose_name='结果')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '扫码历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.barcode.barcode_number}-{self.operation_type}"

class BarcodeGenerationBatch(BaseModel):
    """
    条码生成批次模型
    """
    batch_number = models.CharField(max_length=50, unique=True, verbose_name='批次号')
    barcode_type = models.CharField(max_length=20, choices=Barcode.TYPE_CHOICES, verbose_name='条码类型')
    quantity = models.IntegerField(verbose_name='生成数量')
    prefix = models.CharField(max_length=20, blank=True, null=True, verbose_name='前缀')
    start_number = models.IntegerField(verbose_name='起始编号')
    end_number = models.IntegerField(verbose_name='结束编号')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    
    class Meta:
        verbose_name = '条码生成批次'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.batch_number

class PrintJob(BaseModel):
    """
    打印任务模型
    """
    STATUS_CHOICES = (
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('failed', '失败'),
    )
    
    FORMAT_CHOICES = (
        ('standard', '标准'),
        ('small', '小号'),
        ('large', '大号'),
        ('custom', '自定义'),
    )
    
    job_number = models.CharField(max_length=50, unique=True, verbose_name='任务编号')
    barcodes = models.ManyToManyField(Barcode, related_name='print_jobs', verbose_name='条码')
    printer_name = models.CharField(max_length=100, verbose_name='打印机名称')
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='standard', verbose_name='格式')
    copies = models.IntegerField(default=1, verbose_name='打印份数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    class Meta:
        verbose_name = '打印任务'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
    
    def __str__(self):
        return self.job_number