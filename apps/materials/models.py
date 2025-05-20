from django.db import models
from simple_history.models import HistoricalRecords
from apps.users.models import User
from apps.system.models import BaseModel


class Material(BaseModel):
    """
    物料模型
    用于管理物料基本信息
    """
    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '停用'),
    ]
    
    code = models.CharField('物料编码', max_length=50, unique=True)
    name = models.CharField('物料名称', max_length=100)
    category = models.CharField('物料分类', max_length=50)
    unit = models.CharField('计量单位', max_length=20)
    specifications = models.JSONField('规格参数', default=dict)
    min_stock = models.IntegerField('最小库存', default=0)
    max_stock = models.IntegerField('最大库存', default=0)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    remarks = models.TextField('备注', null=True, blank=True)
    suppliers = models.ManyToManyField('Supplier', through='MaterialSupplier', related_name='materials_supplier')
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '物料'
        verbose_name_plural = verbose_name
        ordering = ['code']
        db_table = 'mat_material'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Location(BaseModel):
    """
    库位模型
    用于管理仓库中的库位信息
    """
    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '停用'),
    ]
    
    code = models.CharField('库位编码', max_length=50, unique=True)
    name = models.CharField('库位名称', max_length=100)
    warehouse = models.ForeignKey('warehouse.Warehouse', on_delete=models.CASCADE, verbose_name='所属仓库')
    area = models.CharField('区域', max_length=50, null=True, blank=True)
    capacity = models.IntegerField('容量', default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '库位'
        verbose_name_plural = verbose_name
        ordering = ['code']
        db_table = 'mat_location'
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Inventory(BaseModel):
    """
    库存模型
    用于管理物料的库存信息
    """
    STATUS_CHOICES = [
        ('normal', '正常'),
        ('locked', '锁定'),
        ('expired', '过期'),
    ]
    
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='物料', related_name='inventories')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, verbose_name='库位')
    batch_number = models.CharField('批次号', max_length=50, null=True, blank=True)
    quantity = models.IntegerField('数量', default=0)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='normal')
    production_date = models.DateField('生产日期', null=True, blank=True)
    expiry_date = models.DateField('过期日期', null=True, blank=True)
    last_transaction = models.ForeignKey('InventoryTransaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_inventory', verbose_name='最后一次交易')
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '库存'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']
        db_table = 'mat_inventory'
        unique_together = ['material', 'location', 'batch_number']
    
    def __str__(self):
        return f"{self.material.name} - {self.location.name} - {self.quantity}{self.material.unit}"


class InventoryTransaction(BaseModel):
    """
    库存交易模型
    用于记录物料的入库、出库和调整记录
    """
    TRANSACTION_TYPE_CHOICES = [
        ('inbound', '入库'),
        ('outbound', '出库'),
        ('adjustment', '调整'),
        ('transfer', '调拨'),
        ('scrap', '报废'),
        ('stocktaking', '盘点'),
    ]
    
    ADJUSTMENT_TYPE_CHOICES = [
        ('increase', '盘盈'),
        ('decrease', '盘亏'),
        ('damage', '报损'),
        ('return', '退货'),
        ('other', '其他'),
    ]
    
    transaction_number = models.CharField('交易编号', max_length=50, unique=True)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name='库存')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='物料', related_name='inventory_transactions')
    transaction_type = models.CharField('交易类型', max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    adjustment_type = models.CharField('调整类型', max_length=20, choices=ADJUSTMENT_TYPE_CHOICES, null=True, blank=True)
    quantity = models.IntegerField('数量')
    batch_number = models.CharField('批次号', max_length=50, null=True, blank=True)
    purchase_order = models.ForeignKey('ProcurementOrder', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='采购订单')
    production_order = models.ForeignKey('production.Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='生产订单', related_name='material_transactions')
    from_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='from_transactions', verbose_name='源库位')
    to_location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='to_transactions', verbose_name='目标库位')
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作人', related_name='operated_inventory_transactions')
    transaction_time = models.DateTimeField('交易时间', auto_now_add=True)
    reason = models.CharField('原因', max_length=200, null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人', related_name='inventory_transaction_creator')

    class Meta:
        verbose_name = '库存交易'
        verbose_name_plural = verbose_name
        ordering = ['-transaction_time']
        db_table = 'mat_inventory_transaction'
        default_permissions = ('add', 'change', 'delete', 'view')
    
    def __str__(self):
        return f"{self.transaction_number} - {self.material.name} - {self.quantity}{self.material.unit}"


class Supplier(BaseModel):
    code = models.CharField('供应商编码', max_length=50, unique=True)
    """
    供应商模型
    用于管理供应商基本信息
    """
    STATUS_CHOICES = [
        ('active', '启用'),
        ('inactive', '停用'),
    ]
    
    name = models.CharField('供应商名称', max_length=100)
    contact_person = models.CharField('联系人', max_length=50)
    contact_phone = models.CharField('联系电话', max_length=20)
    email = models.EmailField('电子邮箱', null=True, blank=True)
    address = models.CharField('地址', max_length=200)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='active')
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        ordering = ['code']
        db_table = 'mat_supplier'

    
    def __str__(self):
        return f"{self.code} - {self.name}"


class MaterialSupplier(BaseModel):
    """
    物料供应商关联模型
    用于管理物料和供应商的多对多关系
    """
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='物料', related_name='supplier_links')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商', related_name='material_links')
    is_preferred = models.BooleanField('是否首选', default=False)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2, default=0)
    lead_time = models.IntegerField('交货周期(天)', default=0)
    min_order_quantity = models.IntegerField('最小订购量', default=1)
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '物料供应商'
        verbose_name_plural = verbose_name
        unique_together = ['material', 'supplier']
        db_table = 'mat_material_supplier'
    
    def __str__(self):
        return f"{self.material.name} - {self.supplier.name}"


class Contact(BaseModel):
    """
    联系人模型
    用于管理供应商的联系人信息
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='contacts', verbose_name='供应商')
    name = models.CharField('姓名', max_length=50)
    position = models.CharField('职位', max_length=50, null=True, blank=True)
    phone = models.CharField('电话', max_length=20)
    email = models.EmailField('邮箱', null=True, blank=True)
    is_primary = models.BooleanField('是否主要联系人', default=False)
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '联系人'
        verbose_name_plural = verbose_name
        db_table = 'mat_contact'
    
    def __str__(self):
        return f"{self.supplier.name} - {self.name}"


class SupplierEvaluation(BaseModel):
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='创建人', related_name='supplier_evaluation_creators')
    evaluator = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='评估人', related_name='supplier_evaluation_evaluators')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    period = models.CharField('评估周期', max_length=50)
    quality_score = models.DecimalField('质量评分', max_digits=5, decimal_places=2)
    delivery_score = models.DecimalField('交付评分', max_digits=5, decimal_places=2)
    price_score = models.DecimalField('价格评分', max_digits=5, decimal_places=2)
    service_score = models.DecimalField('服务评分', max_digits=5, decimal_places=2)
    total_score = models.DecimalField('总评分', max_digits=5, decimal_places=2)

    evaluation_date = models.DateField('评估日期', auto_now_add=True)
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '供应商评估'
        verbose_name_plural = verbose_name
        ordering = ['-evaluation_date']
        db_table = 'mat_supplier_evaluation'
    
    def __str__(self):
        return f"{self.supplier.name} - {self.period} - {self.total_score}"


class ProcurementRequirement(BaseModel):
    """
    采购需求模型
    用于记录采购需求信息
    """
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
        ('urgent', '紧急'),
    ]
    
    requirement_number = models.CharField('需求编号', max_length=50, unique=True)
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='物料')
    quantity = models.IntegerField('数量')
    required_date = models.DateField('需求日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField('优先级', max_length=20, choices=PRIORITY_CHOICES, default='medium')
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='procurement_requirements', verbose_name='申请人')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requirements', verbose_name='审批人')
    approval_date = models.DateTimeField('审批日期', null=True, blank=True)
    production_order = models.ForeignKey('production.Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='生产订单', related_name='procurement_requirements')
    reason = models.CharField('原因', max_length=200)
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '采购需求'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'mat_procurement_requirement'
    
    def __str__(self):
        return f"{self.requirement_number} - {self.material.name} - {self.quantity}{self.material.unit}"


class ProcurementOrder(BaseModel):
    """
    采购订单模型
    用于记录采购订单信息
    """
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('confirmed', '已确认'),
        ('shipping', '发货中'),
        ('received', '已收货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    ]
    
    order_number = models.CharField('订单编号', max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='供应商')
    order_date = models.DateField('订单日期')
    expected_delivery_date = models.DateField('预计交付日期')
    actual_delivery_date = models.DateField('实际交付日期', null=True, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField('总金额', max_digits=12, decimal_places=2, default=0)
    payment_terms = models.CharField('付款条件', max_length=100, null=True, blank=True)
    shipping_method = models.CharField('运输方式', max_length=50, null=True, blank=True)
    contact_person = models.CharField('联系人', max_length=50, null=True, blank=True)
    contact_phone = models.CharField('联系电话', max_length=20, null=True, blank=True)
    delivery_address = models.CharField('交货地址', max_length=200, null=True, blank=True)
    purchaser = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='procurement_orders', verbose_name='采购员')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_orders', verbose_name='审批人')
    approval_date = models.DateTimeField('审批日期', null=True, blank=True)
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '采购订单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        db_table = 'mat_procurement_order'
    
    def __str__(self):
        return f"{self.order_number} - {self.supplier.name} - {self.total_amount}"


class ProcurementItem(BaseModel):
    """
    采购项目模型
    用于记录采购订单中的物料项目
    """
    order = models.ForeignKey(ProcurementOrder, on_delete=models.CASCADE, related_name='items', verbose_name='采购订单')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='物料')
    quantity = models.IntegerField('数量')
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    total_price = models.DecimalField('总价', max_digits=12, decimal_places=2)
    requirement = models.ForeignKey(ProcurementRequirement, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='采购需求')
    received_quantity = models.IntegerField('已收货数量', default=0)
    remarks = models.TextField('备注', null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = '采购项目'
        verbose_name_plural = verbose_name
        db_table = 'mat_procurement_item'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.material.name} - {self.quantity}{self.material.unit}"


class StatusHistory(BaseModel):
    """
    状态历史模型
    用于记录采购订单状态变更历史
    """
    order = models.ForeignKey(ProcurementOrder, on_delete=models.CASCADE, related_name='status_history', verbose_name='采购订单')
    from_status = models.CharField('原状态', max_length=20)
    to_status = models.CharField('新状态', max_length=20)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='创建人', related_name='statushistory_creator')
    change_time = models.DateTimeField('变更时间', auto_now_add=True)
    remarks = models.TextField('备注', null=True, blank=True)
    
    class Meta:
        verbose_name = '状态历史'
        verbose_name_plural = verbose_name
        ordering = ['-change_time']
        db_table = 'mat_status_history'
    
    def __str__(self):
        return f"{self.order.order_number} - {self.from_status} -> {self.to_status}"