from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.db.models import Sum, Avg, Count, F, Q
from datetime import datetime, timedelta
import json

from .models import ReportTemplate, SavedReport
from .serializers import (
    ReportTemplateSerializer, SavedReportSerializer,
    ProductionStatisticsSerializer, ProductionEfficiencySerializer, ProductionQualitySerializer,
    InventoryStatusSerializer, InventoryTurnoverSerializer, MaterialConsumptionSerializer,
    ProductionCostSerializer, ProcurementCostSerializer, CostVarianceSerializer
)
from apps.system.utils import ResponseWrapper
from apps.production.models import Order, ProductionPlan, Batch, ProductionException
from apps.materials.models import Inventory, InventoryTransaction
# TODO: Finance models import needs to be updated once models are available
# from apps.finance.models import Cost, ProcurementOrder

class ReportTemplateViewSet(viewsets.ModelViewSet):
    """
    报表模板视图集
    提供报表模板的CRUD操作
    """
    queryset = ReportTemplate.objects.filter(is_deleted=False)
    serializer_class = ReportTemplateSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

class SavedReportViewSet(viewsets.ModelViewSet):
    """
    保存的报表视图集
    提供保存的报表的CRUD操作
    """
    queryset = SavedReport.objects.filter(is_deleted=False)
    serializer_class = SavedReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status='generating')
    
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()

# 生产报表视图
class ProductionReportViewSet(viewsets.ViewSet):
    """
    生产报表视图集
    提供生产相关的报表数据
    """
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取生产统计报表
        支持按日、周、月分组，可按车间筛选
        """
        serializer = ProductionStatisticsSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        group_by = serializer.validated_data.get('group_by')
        workshop_id = serializer.validated_data.get('workshop_id')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        query_filter = Q(created_at__gte=start_date, created_at__lte=end_date, is_deleted=False)
        if workshop_id:
            query_filter &= Q(workshop_id=workshop_id)
        
        # 获取生产计划数据
        plans = ProductionPlan.objects.filter(query_filter)
        
        # 计算汇总数据
        summary = {
            'total_plans': plans.count(),
            'completed_plans': plans.filter(status='completed').count(),
            'in_progress_plans': plans.filter(status='in_progress').count(),
            'pending_plans': plans.filter(status='pending').count(),
            'avg_completion_rate': plans.aggregate(avg=Avg('progress'))['avg'] or 0,
        }
        
        # 按分组获取详细数据
        details = self._group_production_data(plans, group_by)
        
        # 构建图表数据
        chart_data = {
            'labels': [item['period'] for item in details],
            'datasets': [
                {
                    'label': '计划数',
                    'data': [item['plan_count'] for item in details]
                },
                {
                    'label': '完成率',
                    'data': [item['completion_rate'] for item in details]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    @action(detail=False, methods=['get'])
    def efficiency(self, request):
        """
        获取生产效率报表
        计算设备利用率、人员效率等指标
        """
        serializer = ProductionEfficiencySerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        group_by = serializer.validated_data.get('group_by')
        workshop_id = serializer.validated_data.get('workshop_id')
        line_id = serializer.validated_data.get('line_id')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        query_filter = Q(created_at__gte=start_date, created_at__lte=end_date, is_deleted=False)
        if workshop_id:
            query_filter &= Q(workshop_id=workshop_id)
        if line_id:
            query_filter &= Q(production_line_id=line_id)
        
        # 获取批次数据
        batches = Batch.objects.filter(query_filter)
        
        # 计算汇总数据
        total_planned_hours = batches.aggregate(sum=Sum(F('planned_end_time') - F('planned_start_time')))['sum'] or 0
        total_actual_hours = batches.aggregate(sum=Sum(F('actual_end_time') - F('actual_start_time')))['sum'] or 0
        
        if isinstance(total_planned_hours, timedelta):
            total_planned_hours = total_planned_hours.total_seconds() / 3600
        if isinstance(total_actual_hours, timedelta):
            total_actual_hours = total_actual_hours.total_seconds() / 3600
        
        efficiency_rate = (total_planned_hours / total_actual_hours * 100) if total_actual_hours > 0 else 0
        
        summary = {
            'total_batches': batches.count(),
            'total_planned_hours': round(total_planned_hours, 2),
            'total_actual_hours': round(total_actual_hours, 2),
            'efficiency_rate': round(efficiency_rate, 2),
            'on_time_completion_rate': round(batches.filter(status='completed', actual_end_time__lte=F('planned_end_time')).count() / batches.filter(status='completed').count() * 100 if batches.filter(status='completed').count() > 0 else 0, 2)
        }
        
        # 按分组获取详细数据
        details = self._group_efficiency_data(batches, group_by)
        
        # 构建图表数据
        chart_data = {
            'labels': [item['period'] for item in details],
            'datasets': [
                {
                    'label': '效率率',
                    'data': [item['efficiency_rate'] for item in details]
                },
                {
                    'label': '准时完成率',
                    'data': [item['on_time_rate'] for item in details]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    @action(detail=False, methods=['get'])
    def quality(self, request):
        """
        获取生产质量报表
        计算不良率、返工率等指标
        """
        serializer = ProductionQualitySerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        product_id = serializer.validated_data.get('product_id')
        process_id = serializer.validated_data.get('process_id')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        query_filter = Q(created_at__gte=start_date, created_at__lte=end_date, is_deleted=False)
        if product_id:
            query_filter &= Q(product_id=product_id)
        if process_id:
            query_filter &= Q(process_id=process_id)
        
        # 获取异常数据
        exceptions = ProductionException.objects.filter(query_filter)
        
        # 获取批次数据
        batches = Batch.objects.filter(created_at__gte=start_date, created_at__lte=end_date, is_deleted=False)
        if product_id:
            batches = batches.filter(product_id=product_id)
        
        # 计算汇总数据
        total_batches = batches.count()
        total_exceptions = exceptions.count()
        quality_issues = exceptions.filter(exception_type='quality').count()
        rework_count = exceptions.filter(exception_type='rework').count()
        
        defect_rate = (quality_issues / total_batches * 100) if total_batches > 0 else 0
        rework_rate = (rework_count / total_batches * 100) if total_batches > 0 else 0
        
        summary = {
            'total_batches': total_batches,
            'total_exceptions': total_exceptions,
            'quality_issues': quality_issues,
            'rework_count': rework_count,
            'defect_rate': round(defect_rate, 2),
            'rework_rate': round(rework_rate, 2)
        }
        
        # 获取详细数据
        details = []
        products = {}
        
        for exception in exceptions:
            product_id = exception.product_id
            if product_id not in products:
                products[product_id] = {
                    'product_id': product_id,
                    'product_name': exception.product.name if hasattr(exception, 'product') else f'产品 {product_id}',
                    'total_exceptions': 0,
                    'quality_issues': 0,
                    'rework_count': 0
                }
            
            products[product_id]['total_exceptions'] += 1
            if exception.exception_type == 'quality':
                products[product_id]['quality_issues'] += 1
            elif exception.exception_type == 'rework':
                products[product_id]['rework_count'] += 1
        
        for product_id, data in products.items():
            product_batches = batches.filter(product_id=product_id).count()
            if product_batches > 0:
                data['defect_rate'] = round(data['quality_issues'] / product_batches * 100, 2)
                data['rework_rate'] = round(data['rework_count'] / product_batches * 100, 2)
            else:
                data['defect_rate'] = 0
                data['rework_rate'] = 0
            details.append(data)
        
        # 构建图表数据
        chart_data = {
            'labels': [item['product_name'] for item in details],
            'datasets': [
                {
                    'label': '不良率',
                    'data': [item['defect_rate'] for item in details]
                },
                {
                    'label': '返工率',
                    'data': [item['rework_rate'] for item in details]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    def _parse_time_range(self, time_range):
        """
        解析时间范围字符串
        格式：'2023-01-01,2023-01-31' 或 'last7days', 'last30days', 'thismonth', 'lastmonth'
        """
        today = timezone.now().date()
        
        if ',' in time_range:
            start_str, end_str = time_range.split(',')
            try:
                start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d').date()
                return datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())
            except ValueError:
                raise ValueError('日期格式错误，正确格式为：YYYY-MM-DD,YYYY-MM-DD')
        
        if time_range == 'last7days':
            start_date = today - timedelta(days=7)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'last30days':
            start_date = today - timedelta(days=30)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'thismonth':
            start_date = today.replace(day=1)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'lastmonth':
            last_month = today.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())
        
        raise ValueError('无效的时间范围格式')
    
    def _group_production_data(self, plans, group_by):
        """
        按指定的分组方式对生产计划数据进行分组
        """
        details = []
        
        if group_by == 'day':
            # 按天分组
            current_date = plans.order_by('created_at').first().created_at.date() if plans.exists() else timezone.now().date()
            end_date = plans.order_by('-created_at').first().created_at.date() if plans.exists() else current_date
            
            while current_date <= end_date:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                day_plans = plans.filter(created_at__gte=day_start, created_at__lte=day_end)
                
                if day_plans.exists():
                    details.append({
                        'period': current_date.strftime('%Y-%m-%d'),
                        'plan_count': day_plans.count(),
                        'completed_count': day_plans.filter(status='completed').count(),
                        'completion_rate': round(day_plans.aggregate(avg=Avg('progress'))['avg'] or 0, 2)
                    })
                
                current_date += timedelta(days=1)
        
        elif group_by == 'week':
            # 按周分组
            weeks = {}
            for plan in plans:
                year, week, _ = plan.created_at.isocalendar()
                week_key = f'{year}-W{week:02d}'
                
                if week_key not in weeks:
                    weeks[week_key] = {
                        'period': week_key,
                        'plans': [],
                    }
                
                weeks[week_key]['plans'].append(plan)
            
            for week_key, data in sorted(weeks.items()):
                week_plans = data['plans']
                details.append({
                    'period': data['period'],
                    'plan_count': len(week_plans),
                    'completed_count': sum(1 for p in week_plans if p.status == 'completed'),
                    'completion_rate': round(sum(p.progress for p in week_plans) / len(week_plans) if week_plans else 0, 2)
                })
        
        elif group_by == 'month':
            # 按月分组
            months = {}
            for plan in plans:
                month_key = plan.created_at.strftime('%Y-%m')
                
                if month_key not in months:
                    months[month_key] = {
                        'period': month_key,
                        'plans': [],
                    }
                
                months[month_key]['plans'].append(plan)
            
            for month_key, data in sorted(months.items()):
                month_plans = data['plans']
                details.append({
                    'period': data['period'],
                    'plan_count': len(month_plans),
                    'completed_count': sum(1 for p in month_plans if p.status == 'completed'),
                    'completion_rate': round(sum(p.progress for p in month_plans) / len(month_plans) if month_plans else 0, 2)
                })
        
        return details
    
    def _group_efficiency_data(self, batches, group_by):
        """
        按指定的分组方式对生产效率数据进行分组
        """
        details = []
        
        if group_by == 'day':
            # 按天分组
            current_date = batches.order_by('created_at').first().created_at.date() if batches.exists() else timezone.now().date()
            end_date = batches.order_by('-created_at').first().created_at.date() if batches.exists() else current_date
            
            while current_date <= end_date:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                day_batches = batches.filter(created_at__gte=day_start, created_at__lte=day_end)
                
                if day_batches.exists():
                    details.append(self._calculate_efficiency_metrics(day_batches, current_date.strftime('%Y-%m-%d')))
                
                current_date += timedelta(days=1)
        
        elif group_by == 'week':
            # 按周分组
            weeks = {}
            for batch in batches:
                year, week, _ = batch.created_at.isocalendar()
                week_key = f'{year}-W{week:02d}'
                
                if week_key not in weeks:
                    weeks[week_key] = {
                        'period': week_key,
                        'batches': [],
                    }
                
                weeks[week_key]['batches'].append(batch)
            
            for week_key, data in sorted(weeks.items()):
                details.append(self._calculate_efficiency_metrics(data['batches'], data['period']))
        
        elif group_by == 'month':
            # 按月分组
            months = {}
            for batch in batches:
                month_key = batch.created_at.strftime('%Y-%m')
                
                if month_key not in months:
                    months[month_key] = {
                        'period': month_key,
                        'batches': [],
                    }
                
                months[month_key]['batches'].append(batch)
            
            for month_key, data in sorted(months.items()):
                details.append(self._calculate_efficiency_metrics(data['batches'], data['period']))
        
        return details
    
    def _calculate_efficiency_metrics(self, batches, period):
        """
        计算效率指标
        """
        total_planned_hours = sum((batch.planned_end_time - batch.planned_start_time).total_seconds() / 3600 for batch in batches if batch.planned_end_time and batch.planned_start_time)
        total_actual_hours = sum((batch.actual_end_time - batch.actual_start_time).total_seconds() / 3600 for batch in batches if batch.actual_end_time and batch.actual_start_time)
        
        completed_batches = [batch for batch in batches if batch.status == 'completed']
        on_time_batches = [batch for batch in completed_batches if batch.actual_end_time and batch.planned_end_time and batch.actual_end_time <= batch.planned_end_time]
        
        efficiency_rate = (total_planned_hours / total_actual_hours * 100) if total_actual_hours > 0 else 0
        on_time_rate = (len(on_time_batches) / len(completed_batches) * 100) if completed_batches else 0
        
        return {
            'period': period,
            'batch_count': len(batches),
            'planned_hours': round(total_planned_hours, 2),
            'actual_hours': round(total_actual_hours, 2),
            'efficiency_rate': round(efficiency_rate, 2),
            'on_time_rate': round(on_time_rate, 2)
        }

# 库存报表视图
class InventoryReportViewSet(viewsets.ViewSet):
    """
    库存报表视图集
    提供库存相关的报表数据
    """
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        获取库存状态报表
        按类别统计库存价值
        """
        serializer = InventoryStatusSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        date = serializer.validated_data.get('date')
        category = serializer.validated_data.get('category')
        
        # 构建查询条件
        query_filter = Q(is_deleted=False)
        if category:
            query_filter &= Q(material__category=category)
        
        # 获取库存数据
        inventories = Inventory.objects.filter(query_filter)
        
        # 计算汇总数据
        total_items = inventories.count()
        total_quantity = inventories.aggregate(sum=Sum('current_quantity'))['sum'] or 0
        total_value = inventories.aggregate(sum=Sum(F('current_quantity') * F('material__unit_price')))['sum'] or 0
        
        summary = {
            'date': date.strftime('%Y-%m-%d'),
            'total_items': total_items,
            'total_quantity': total_quantity,
            'total_value': round(total_value, 2),
            'category_count': inventories.values('material__category').distinct().count()
        }
        
        # 按类别获取详细数据
        details = []
        categories = inventories.values('material__category').distinct()
        
        for category_data in categories:
            category_name = category_data['material__category']
            category_inventories = inventories.filter(material__category=category_name)
            
            category_quantity = category_inventories.aggregate(sum=Sum('current_quantity'))['sum'] or 0
            category_value = category_inventories.aggregate(sum=Sum(F('current_quantity') * F('material__unit_price')))['sum'] or 0
            
            details.append({
                'category': category_name,
                'item_count': category_inventories.count(),
                'quantity': category_quantity,
                'value': round(category_value, 2),
                'percentage': round(category_value / total_value * 100 if total_value > 0 else 0, 2)
            })
        
        # 按价值排序
        details.sort(key=lambda x: x['value'], reverse=True)
        
        # 构建图表数据
        chart_data = {
            'labels': [item['category'] for item in details],
            'datasets': [
                {
                    'label': '库存价值',
                    'data': [item['value'] for item in details]
                },
                {
                    'label': '库存数量',
                    'data': [item['quantity'] for item in details]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    @action(detail=False, methods=['get'])
    def turnover(self, request):
        """
        获取库存周转报表
        计算库存周转率，识别呆滞物料
        """
        serializer = InventoryTurnoverSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        category = serializer.validated_data.get('category')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        inventory_filter = Q(is_deleted=False)
        transaction_filter = Q(transaction_time__gte=start_date, transaction_time__lte=end_date, is_deleted=False)
        
        if category:
            inventory_filter &= Q(material__category=category)
            transaction_filter &= Q(inventory__material__category=category)
        
        # 获取库存数据
        inventories = Inventory.objects.filter(inventory_filter)
        transactions = InventoryTransaction.objects.filter(transaction_filter)
        
        # 计算周转率
        period_days = (end_date.date() - start_date.date()).days
        
        # 计算汇总数据
        avg_inventory_value = inventories.aggregate(avg=Avg(F('current_quantity') * F('material__unit_price')))['avg'] or 0
        total_outbound_value = transactions.filter(transaction_type='outbound').aggregate(
            sum=Sum(F('quantity') * F('inventory__material__unit_price')))['sum'] or 0
        
        turnover_rate = (total_outbound_value / avg_inventory_value * 365 / period_days) if avg_inventory_value > 0 and period_days > 0 else 0
        
        summary = {
            'period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            'avg_inventory_value': round(avg_inventory_value, 2),
            'total_outbound_value': round(total_outbound_value, 2),
            'turnover_rate': round(turnover_rate, 2),
            'turnover_days': round(365 / turnover_rate if turnover_rate > 0 else 0, 2)
        }
        
        # 计算每个物料的周转率
        details = []
        for inventory in inventories:
            material_id = inventory.material_id
            material_name = inventory.material.name if hasattr(inventory, 'material') else f'物料 {material_id}'
            
            material_transactions = transactions.filter(inventory__material_id=material_id)
            material_outbound_value = material_transactions.filter(transaction_type='outbound').aggregate(
                sum=Sum(F('quantity') * F('inventory__material__unit_price')))['sum'] or 0
            
            avg_material_value = inventory.current_quantity * inventory.material.unit_price if hasattr(inventory, 'material') else 0
            material_turnover_rate = (material_outbound_value / avg_material_value * 365 / period_days) if avg_material_value > 0 and period_days > 0 else 0
            material_turnover_days = 365 / material_turnover_rate if material_turnover_rate > 0 else 0
            
            # 判断是否为呆滞物料（周转天数超过90天）
            is_stagnant = material_turnover_days >= 90 if material_turnover_days > 0 else True
            
            details.append({
                'material_id': material_id,
                'material_name': material_name,
                'current_quantity': inventory.current_quantity,
                'current_value': round(avg_material_value, 2),
                'outbound_value': round(material_outbound_value, 2),
                'turnover_rate': round(material_turnover_rate, 2),
                'turnover_days': round(material_turnover_days, 2),
                'is_stagnant': is_stagnant
            })
        
        # 按周转率排序
        details.sort(key=lambda x: x['turnover_rate'])
        
        # 构建图表数据
        chart_data = {
            'labels': [item['material_name'] for item in details[:20]],  # 只显示前20个物料
            'datasets': [
                {
                    'label': '周转天数',
                    'data': [item['turnover_days'] for item in details[:20]]
                },
                {
                    'label': '周转率',
                    'data': [item['turnover_rate'] for item in details[:20]]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        获取库存统计信息
        支持按不同报表类型获取库存统计数据
        参数：
            - report_type: 报表类型 (summary, aging, category, location)
            - warehouse_id: 仓库ID (可选)
            - category_id: 物料类别ID (可选)
        """
        # 获取请求参数
        report_type = request.query_params.get('report_type', 'summary')
        warehouse_id = request.query_params.get('warehouse_id')
        category_id = request.query_params.get('category_id')
        
        # 构建查询条件
        query_filter = Q(is_deleted=False)
        if warehouse_id:
            query_filter &= Q(warehouse_id=warehouse_id)
        if category_id:
            query_filter &= Q(material__category_id=category_id)
        
        # 获取库存数据
        inventories = Inventory.objects.filter(query_filter)
        
        # 根据报表类型返回不同的统计数据
        if report_type == 'summary':
            # 库存总览
            total_items = inventories.count()
            total_value = inventories.aggregate(total=Sum(F('quantity') * F('unit_price')))['total'] or 0
            
            # 库存状态分布
            low_stock = inventories.filter(quantity__lt=F('min_quantity')).count()
            normal_stock = inventories.filter(quantity__gte=F('min_quantity'), quantity__lte=F('max_quantity')).count()
            over_stock = inventories.filter(quantity__gt=F('max_quantity')).count()
            
            # 最近30天的库存变化
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_transactions = InventoryTransaction.objects.filter(
                material__in=inventories.values_list('material', flat=True),
                created_at__gte=thirty_days_ago
            )
            
            # 按日期分组的库存变化
            daily_changes = {}
            for transaction in recent_transactions:
                date_key = transaction.created_at.date().isoformat()
                if date_key not in daily_changes:
                    daily_changes[date_key] = {'in': 0, 'out': 0}
                
                if transaction.transaction_type in ['purchase_in', 'production_in', 'return_in', 'adjustment_in']:
                    daily_changes[date_key]['in'] += transaction.quantity
                elif transaction.transaction_type in ['sales_out', 'production_out', 'return_out', 'adjustment_out']:
                    daily_changes[date_key]['out'] += transaction.quantity
            
            # 转换为列表并排序
            daily_changes_list = [{'date': k, 'in': v['in'], 'out': v['out']} for k, v in daily_changes.items()]
            daily_changes_list.sort(key=lambda x: x['date'])
            
            return Response({
                'total_items': total_items,
                'total_value': round(total_value, 2),
                'stock_status': {
                    'low_stock': low_stock,
                    'normal_stock': normal_stock,
                    'over_stock': over_stock,
                },
                'daily_changes': daily_changes_list,
            })
            
        elif report_type == 'aging':
            # 库存时效分析
            now = timezone.now()
            aging_ranges = {
                '0-30': {'count': 0, 'value': 0},
                '31-60': {'count': 0, 'value': 0},
                '61-90': {'count': 0, 'value': 0},
                '91-180': {'count': 0, 'value': 0},
                '180+': {'count': 0, 'value': 0},
            }
            
            for inventory in inventories:
                # 计算库存时间（天）
                if inventory.last_in_date:
                    days = (now.date() - inventory.last_in_date).days
                    value = inventory.quantity * inventory.unit_price
                    
                    if days <= 30:
                        aging_ranges['0-30']['count'] += 1
                        aging_ranges['0-30']['value'] += value
                    elif days <= 60:
                        aging_ranges['31-60']['count'] += 1
                        aging_ranges['31-60']['value'] += value
                    elif days <= 90:
                        aging_ranges['61-90']['count'] += 1
                        aging_ranges['61-90']['value'] += value
                    elif days <= 180:
                        aging_ranges['91-180']['count'] += 1
                        aging_ranges['91-180']['value'] += value
                    else:
                        aging_ranges['180+']['count'] += 1
                        aging_ranges['180+']['value'] += value
            
            # 格式化结果
            aging_data = [{
                'range': k,
                'count': v['count'],
                'value': round(v['value'], 2),
                'percentage': round(v['count'] / inventories.count() * 100, 2) if inventories.count() > 0 else 0
            } for k, v in aging_ranges.items()]
            
            return Response(aging_data)
            
        elif report_type == 'category':
            # 按物料类别统计
            categories = {}
            for inventory in inventories:
                category_name = inventory.material.category.name if inventory.material.category else '未分类'
                category_id = inventory.material.category_id if inventory.material.category else 0
                
                if category_id not in categories:
                    categories[category_id] = {
                        'id': category_id,
                        'name': category_name,
                        'count': 0,
                        'value': 0,
                        'quantity': 0,
                    }
                
                categories[category_id]['count'] += 1
                categories[category_id]['value'] += inventory.quantity * inventory.unit_price
                categories[category_id]['quantity'] += inventory.quantity
            
            # 转换为列表并排序
            category_data = list(categories.values())
            for item in category_data:
                item['value'] = round(item['value'], 2)
            
            category_data.sort(key=lambda x: x['value'], reverse=True)
            
            return Response(category_data)
            
        elif report_type == 'location':
            # 按库位统计
            locations = {}
            for inventory in inventories:
                location_name = inventory.location or '未指定'
                location_key = inventory.location or 'unspecified'
                
                if location_key not in locations:
                    locations[location_key] = {
                        'name': location_name,
                        'count': 0,
                        'value': 0,
                        'quantity': 0,
                    }
                
                locations[location_key]['count'] += 1
                locations[location_key]['value'] += inventory.quantity * inventory.unit_price
                locations[location_key]['quantity'] += inventory.quantity
            
            # 转换为列表并排序
            location_data = list(locations.values())
            for item in location_data:
                item['value'] = round(item['value'], 2)
            
            location_data.sort(key=lambda x: x['value'], reverse=True)
            
            return Response(location_data)
        
        else:
            return Response({'error': f'不支持的报表类型: {report_type}'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def consumption(self, request):
        """
        获取物料消耗报表
        统计物料消耗情况，支持按日、周、月分组
        """
        serializer = MaterialConsumptionSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        material_id = serializer.validated_data.get('material_id')
        group_by = serializer.validated_data.get('group_by')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        query_filter = Q(transaction_time__gte=start_date, transaction_time__lte=end_date, 
                         transaction_type='outbound', is_deleted=False)
        if material_id:
            query_filter &= Q(inventory__material_id=material_id)
        
        # 获取出库事务数据
        transactions = InventoryTransaction.objects.filter(query_filter)
        
        # 计算汇总数据
        total_quantity = transactions.aggregate(sum=Sum('quantity'))['sum'] or 0
        total_value = transactions.aggregate(sum=Sum(F('quantity') * F('inventory__material__unit_price')))['sum'] or 0
        
        summary = {
            'period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            'total_transactions': transactions.count(),
            'total_quantity': total_quantity,
            'total_value': round(total_value, 2),
            'material_count': transactions.values('inventory__material_id').distinct().count()
        }
        
        # 按分组获取详细数据
        details = self._group_consumption_data(transactions, group_by)
        
        # 构建图表数据
        chart_data = {
            'labels': [item['period'] for item in details],
            'datasets': [
                {
                    'label': '消耗数量',
                    'data': [item['quantity'] for item in details]
                },
                {
                    'label': '消耗金额',
                    'data': [item['value'] for item in details]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    def _parse_time_range(self, time_range):
        """
        解析时间范围字符串
        格式：'2023-01-01,2023-01-31' 或 'last7days', 'last30days', 'thismonth', 'lastmonth'
        """
        today = timezone.now().date()
        
        if ',' in time_range:
            start_str, end_str = time_range.split(',')
            try:
                start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d').date()
                return datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())
            except ValueError:
                raise ValueError('日期格式错误，正确格式为：YYYY-MM-DD,YYYY-MM-DD')
        
        if time_range == 'last7days':
            start_date = today - timedelta(days=7)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'last30days':
            start_date = today - timedelta(days=30)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'thismonth':
            start_date = today.replace(day=1)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'lastmonth':
            last_month = today.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())
        
        raise ValueError('无效的时间范围格式')
    
    def _group_consumption_data(self, transactions, group_by):
        """
        按指定的分组方式对物料消耗数据进行分组
        """
        details = []
        
        if group_by == 'day':
            # 按天分组
            current_date = transactions.order_by('transaction_time').first().transaction_time.date() if transactions.exists() else timezone.now().date()
            end_date = transactions.order_by('-transaction_time').first().transaction_time.date() if transactions.exists() else current_date
            
            while current_date <= end_date:
                day_start = datetime.combine(current_date, datetime.min.time())
                day_end = datetime.combine(current_date, datetime.max.time())
                day_transactions = transactions.filter(transaction_time__gte=day_start, transaction_time__lte=day_end)
                
                if day_transactions.exists():
                    quantity = day_transactions.aggregate(sum=Sum('quantity'))['sum'] or 0
                    value = day_transactions.aggregate(sum=Sum(F('quantity') * F('inventory__material__unit_price')))['sum'] or 0
                    
                    details.append({
                        'period': current_date.strftime('%Y-%m-%d'),
                        'transaction_count': day_transactions.count(),
                        'quantity': quantity,
                        'value': round(value, 2)
                    })
                
                current_date += timedelta(days=1)
        
        elif group_by == 'week':
            # 按周分组
            weeks = {}
            for transaction in transactions:
                year, week, _ = transaction.transaction_time.isocalendar()
                week_key = f'{year}-W{week:02d}'
                
                if week_key not in weeks:
                    weeks[week_key] = {
                        'period': week_key,
                        'transactions': [],
                    }
                
                weeks[week_key]['transactions'].append(transaction)
            
            for week_key, data in sorted(weeks.items()):
                week_transactions = data['transactions']
                quantity = sum(t.quantity for t in week_transactions)
                value = sum(t.quantity * t.inventory.material.unit_price for t in week_transactions if hasattr(t.inventory, 'material'))
                
                details.append({
                    'period': data['period'],
                    'transaction_count': len(week_transactions),
                    'quantity': quantity,
                    'value': round(value, 2)
                })
        
        elif group_by == 'month':
            # 按月分组
            months = {}
            for transaction in transactions:
                month_key = transaction.transaction_time.strftime('%Y-%m')
                
                if month_key not in months:
                    months[month_key] = {
                        'period': month_key,
                        'transactions': [],
                    }
                
                months[month_key]['transactions'].append(transaction)
            
            for month_key, data in sorted(months.items()):
                month_transactions = data['transactions']
                quantity = sum(t.quantity for t in month_transactions)
                value = sum(t.quantity * t.inventory.material.unit_price for t in month_transactions if hasattr(t.inventory, 'material'))
                
                details.append({
                    'period': data['period'],
                    'transaction_count': len(month_transactions),
                    'quantity': quantity,
                    'value': round(value, 2)
                })
        
        return details

# 成本报表视图
class CostReportViewSet(viewsets.ViewSet):
    """
    成本报表视图集
    提供成本相关的报表数据
    """
    
    @action(detail=False, methods=['get'])
    def production(self, request):
        """
        获取生产成本报表
        统计生产成本，分析物料成本、人工成本和制造费用
        """
        serializer = ProductionCostSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        product_id = serializer.validated_data.get('product_id')
        group_by = serializer.validated_data.get('group_by')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        query_filter = Q(cost_date__gte=start_date.date(), cost_date__lte=end_date.date(), 
                         cost_type='production', is_deleted=False)
        if product_id:
            query_filter &= Q(product_id=product_id)
        
        # 获取成本数据
        costs = Cost.objects.filter(query_filter)
        
        # 计算汇总数据
        total_cost = costs.aggregate(sum=Sum('amount'))['sum'] or 0
        material_cost = costs.filter(cost_category='material').aggregate(sum=Sum('amount'))['sum'] or 0
        labor_cost = costs.filter(cost_category='labor').aggregate(sum=Sum('amount'))['sum'] or 0
        overhead_cost = costs.filter(cost_category='overhead').aggregate(sum=Sum('amount'))['sum'] or 0
        
        summary = {
            'period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            'total_cost': round(total_cost, 2),
            'material_cost': round(material_cost, 2),
            'material_percentage': round(material_cost / total_cost * 100 if total_cost > 0 else 0, 2),
            'labor_cost': round(labor_cost, 2),
            'labor_percentage': round(labor_cost / total_cost * 100 if total_cost > 0 else 0, 2),
            'overhead_cost': round(overhead_cost, 2),
            'overhead_percentage': round(overhead_cost / total_cost * 100 if total_cost > 0 else 0, 2),
            'product_count': costs.values('product_id').distinct().count()
        }
        
        # 按分组获取详细数据
        details = self._group_cost_data(costs, group_by)
        
        # 构建图表数据
        chart_data = {
            'labels': [item['period'] for item in details],
            'datasets': [
                {
                    'label': '物料成本',
                    'data': [item['material_cost'] for item in details]
                },
                {
                    'label': '人工成本',
                    'data': [item['labor_cost'] for item in details]
                },
                {
                    'label': '制造费用',
                    'data': [item['overhead_cost'] for item in details]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    @action(detail=False, methods=['get'])
    def procurement(self, request):
        """
        获取采购成本报表
        统计采购成本，分析不同类别和供应商的采购金额
        """
        serializer = ProcurementCostSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        category = serializer.validated_data.get('category')
        supplier_id = serializer.validated_data.get('supplier_id')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        query_filter = Q(order_date__gte=start_date.date(), order_date__lte=end_date.date(), is_deleted=False)
        if category:
            query_filter &= Q(material__category=category)
        if supplier_id:
            query_filter &= Q(supplier_id=supplier_id)
        
        # 获取采购订单数据
        orders = ProcurementOrder.objects.filter(query_filter)
        
        # 计算汇总数据
        total_amount = orders.aggregate(sum=Sum('total_amount'))['sum'] or 0
        
        summary = {
            'period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            'total_orders': orders.count(),
            'total_amount': round(total_amount, 2),
            'supplier_count': orders.values('supplier_id').distinct().count(),
            'category_count': orders.values('material__category').distinct().count()
        }
        
        # 按供应商获取详细数据
        supplier_details = []
        suppliers = orders.values('supplier_id', 'supplier__name').distinct()
        
        for supplier_data in suppliers:
            supplier_id = supplier_data['supplier_id']
            supplier_name = supplier_data['supplier__name'] if supplier_data['supplier__name'] else f'供应商 {supplier_id}'
            
            supplier_orders = orders.filter(supplier_id=supplier_id)
            supplier_amount = supplier_orders.aggregate(sum=Sum('total_amount'))['sum'] or 0
            
            supplier_details.append({
                'supplier_id': supplier_id,
                'supplier_name': supplier_name,
                'order_count': supplier_orders.count(),
                'amount': round(supplier_amount, 2),
                'percentage': round(supplier_amount / total_amount * 100 if total_amount > 0 else 0, 2)
            })
        
        # 按类别获取详细数据
        category_details = []
        categories = orders.values('material__category').distinct()
        
        for category_data in categories:
            category_name = category_data['material__category']
            
            category_orders = orders.filter(material__category=category_name)
            category_amount = category_orders.aggregate(sum=Sum('total_amount'))['sum'] or 0
            
            category_details.append({
                'category': category_name,
                'order_count': category_orders.count(),
                'amount': round(category_amount, 2),
                'percentage': round(category_amount / total_amount * 100 if total_amount > 0 else 0, 2)
            })
        
        # 按金额排序
        supplier_details.sort(key=lambda x: x['amount'], reverse=True)
        category_details.sort(key=lambda x: x['amount'], reverse=True)
        
        # 构建图表数据
        chart_data = {
            'supplier': {
                'labels': [item['supplier_name'] for item in supplier_details[:10]],  # 只显示前10个供应商
                'data': [item['amount'] for item in supplier_details[:10]]
            },
            'category': {
                'labels': [item['category'] for item in category_details],
                'data': [item['amount'] for item in category_details]
            }
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'supplier_details': supplier_details,
            'category_details': category_details,
            'chart': chart_data
        })
    
    @action(detail=False, methods=['get'])
    def variance(self, request):
        """
        获取成本差异分析报表
        分析计划成本与实际成本的差异，识别成本超支原因
        """
        serializer = CostVarianceSerializer(data=request.query_params)
        if not serializer.is_valid():
            return ResponseWrapper.error(serializer.errors)
        
        time_range = serializer.validated_data.get('time_range')
        product_id = serializer.validated_data.get('product_id')
        
        # 解析时间范围
        try:
            start_date, end_date = self._parse_time_range(time_range)
        except ValueError as e:
            return ResponseWrapper.error(str(e))
        
        # 构建查询条件
        query_filter = Q(cost_date__gte=start_date.date(), cost_date__lte=end_date.date(), 
                         cost_type='production', is_deleted=False)
        if product_id:
            query_filter &= Q(product_id=product_id)
        
        # 获取成本数据
        costs = Cost.objects.filter(query_filter)
        
        # 计算汇总数据
        total_planned_cost = costs.aggregate(sum=Sum('planned_amount'))['sum'] or 0
        total_actual_cost = costs.aggregate(sum=Sum('amount'))['sum'] or 0
        total_variance = total_actual_cost - total_planned_cost
        variance_percentage = (total_variance / total_planned_cost * 100) if total_planned_cost > 0 else 0
        
        summary = {
            'period': f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}",
            'total_planned_cost': round(total_planned_cost, 2),
            'total_actual_cost': round(total_actual_cost, 2),
            'total_variance': round(total_variance, 2),
            'variance_percentage': round(variance_percentage, 2),
            'product_count': costs.values('product_id').distinct().count()
        }
        
        # 按产品获取详细数据
        details = []
        products = costs.values('product_id', 'product__name').distinct()
        
        for product_data in products:
            product_id = product_data['product_id']
            product_name = product_data['product__name'] if product_data['product__name'] else f'产品 {product_id}'
            
            product_costs = costs.filter(product_id=product_id)
            
            # 计算各类成本
            planned_material = product_costs.filter(cost_category='material').aggregate(sum=Sum('planned_amount'))['sum'] or 0
            actual_material = product_costs.filter(cost_category='material').aggregate(sum=Sum('amount'))['sum'] or 0
            material_variance = actual_material - planned_material
            
            planned_labor = product_costs.filter(cost_category='labor').aggregate(sum=Sum('planned_amount'))['sum'] or 0
            actual_labor = product_costs.filter(cost_category='labor').aggregate(sum=Sum('amount'))['sum'] or 0
            labor_variance = actual_labor - planned_labor
            
            planned_overhead = product_costs.filter(cost_category='overhead').aggregate(sum=Sum('planned_amount'))['sum'] or 0
            actual_overhead = product_costs.filter(cost_category='overhead').aggregate(sum=Sum('amount'))['sum'] or 0
            overhead_variance = actual_overhead - planned_overhead
            
            total_planned = planned_material + planned_labor + planned_overhead
            total_actual = actual_material + actual_labor + actual_overhead
            total_variance = total_actual - total_planned
            
            details.append({
                'product_id': product_id,
                'product_name': product_name,
                'planned_material': round(planned_material, 2),
                'actual_material': round(actual_material, 2),
                'material_variance': round(material_variance, 2),
                'material_variance_percentage': round(material_variance / planned_material * 100 if planned_material > 0 else 0, 2),
                'planned_labor': round(planned_labor, 2),
                'actual_labor': round(actual_labor, 2),
                'labor_variance': round(labor_variance, 2),
                'labor_variance_percentage': round(labor_variance / planned_labor * 100 if planned_labor > 0 else 0, 2),
                'planned_overhead': round(planned_overhead, 2),
                'actual_overhead': round(actual_overhead, 2),
                'overhead_variance': round(overhead_variance, 2),
                'overhead_variance_percentage': round(overhead_variance / planned_overhead * 100 if planned_overhead > 0 else 0, 2),
                'total_planned': round(total_planned, 2),
                'total_actual': round(total_actual, 2),
                'total_variance': round(total_variance, 2),
                'total_variance_percentage': round(total_variance / total_planned * 100 if total_planned > 0 else 0, 2)
            })
        
        # 按差异金额排序
        details.sort(key=lambda x: abs(x['total_variance']), reverse=True)
        
        # 构建图表数据
        chart_data = {
            'labels': [item['product_name'] for item in details[:10]],  # 只显示前10个产品
            'datasets': [
                {
                    'label': '计划成本',
                    'data': [item['total_planned'] for item in details[:10]]
                },
                {
                    'label': '实际成本',
                    'data': [item['total_actual'] for item in details[:10]]
                },
                {
                    'label': '差异',
                    'data': [item['total_variance'] for item in details[:10]]
                }
            ]
        }
        
        return ResponseWrapper.success({
            'summary': summary,
            'details': details,
            'chart': chart_data
        })
    
    def _parse_time_range(self, time_range):
        """
        解析时间范围字符串
        格式：'2023-01-01,2023-01-31' 或 'last7days', 'last30days', 'thismonth', 'lastmonth'
        """
        today = timezone.now().date()
        
        if ',' in time_range:
            start_str, end_str = time_range.split(',')
            try:
                start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d').date()
                end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d').date()
                return datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())
            except ValueError:
                raise ValueError('日期格式错误，正确格式为：YYYY-MM-DD,YYYY-MM-DD')
        
        if time_range == 'last7days':
            start_date = today - timedelta(days=7)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'last30days':
            start_date = today - timedelta(days=30)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'thismonth':
            start_date = today.replace(day=1)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(today, datetime.max.time())
        
        if time_range == 'lastmonth':
            last_month = today.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1)
            end_date = today.replace(day=1) - timedelta(days=1)
            return datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())
        
        raise ValueError('无效的时间范围格式')
    
    def _group_cost_data(self, costs, group_by):
        """
        按指定的分组方式对成本数据进行分组
        """
        details = []
        
        if group_by == 'day':
            # 按天分组
            current_date = costs.order_by('cost_date').first().cost_date if costs.exists() else timezone.now().date()
            end_date = costs.order_by('-cost_date').first().cost_date if costs.exists() else current_date
            
            while current_date <= end_date:
                day_costs = costs.filter(cost_date=current_date)
                
                if day_costs.exists():
                    material_cost = day_costs.filter(cost_category='material').aggregate(sum=Sum('amount'))['sum'] or 0
                    labor_cost = day_costs.filter(cost_category='labor').aggregate(sum=Sum('amount'))['sum'] or 0
                    overhead_cost = day_costs.filter(cost_category='overhead').aggregate(sum=Sum('amount'))['sum'] or 0
                    
                    details.append({
                        'period': current_date.strftime('%Y-%m-%d'),
                        'material_cost': round(material_cost, 2),
                        'labor_cost': round(labor_cost, 2),
                        'overhead_cost': round(overhead_cost, 2),
                        'total_cost': round(material_cost + labor_cost + overhead_cost, 2)
                    })
                
                current_date += timedelta(days=1)
        
        elif group_by == 'week':
            # 按周分组
            weeks = {}
            for cost in costs:
                year, week, _ = cost.cost_date.isocalendar()
                week_key = f'{year}-W{week:02d}'
                
                if week_key not in weeks:
                    weeks[week_key] = {
                        'period': week_key,
                        'costs': [],
                    }
                
                weeks[week_key]['costs'].append(cost)
            
            for week_key, data in sorted(weeks.items()):
                week_costs = data['costs']
                material_cost = sum(c.amount for c in week_costs if c.cost_category == 'material')
                labor_cost = sum(c.amount for c in week_costs if c.cost_category == 'labor')
                overhead_cost = sum(c.amount for c in week_costs if c.cost_category == 'overhead')
                
                details.append({
                    'period': data['period'],
                    'material_cost': round(material_cost, 2),
                    'labor_cost': round(labor_cost, 2),
                    'overhead_cost': round(overhead_cost, 2),
                    'total_cost': round(material_cost + labor_cost + overhead_cost, 2)
                })
        
        elif group_by == 'month':
            # 按月分组
            months = {}
            for cost in costs:
                month_key = cost.cost_date.strftime('%Y-%m')
                
                if month_key not in months:
                    months[month_key] = {
                        'period': month_key,
                        'costs': [],
                    }
                
                months[month_key]['costs'].append(cost)
            
            for month_key, data in sorted(months.items()):
                month_costs = data['costs']
                material_cost = sum(c.amount for c in month_costs if c.cost_category == 'material')
                labor_cost = sum(c.amount for c in month_costs if c.cost_category == 'labor')
                overhead_cost = sum(c.amount for c in month_costs if c.cost_category == 'overhead')
                
                details.append({
                    'period': data['period'],
                    'material_cost': round(material_cost, 2),
                    'labor_cost': round(labor_cost, 2),
                    'overhead_cost': round(overhead_cost, 2),
                    'total_cost': round(material_cost + labor_cost + overhead_cost, 2)
                })
        
        return details