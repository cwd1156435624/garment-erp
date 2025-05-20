from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import CuttingTask, ProductionPlan
from .serializers import CuttingTaskSerializer
from apps.system.utils import ResponseWrapper
from apps.materials.models import Material, Inventory


class CuttingTaskCreateView(views.APIView):
    """
    裁剪任务创建视图
    用于创建裁剪任务，分配面料，生成裁剪图纸
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 获取请求参数
            plan_id = request.data.get('planId')
            fabric_id = request.data.get('fabricId')
            quantity = request.data.get('quantity')
            markers = request.data.get('markers', [])
            
            # 参数验证
            if not all([plan_id, fabric_id, quantity]):
                return ResponseWrapper.error('生产计划ID、面料ID和数量不能为空')
            
            # 验证生产计划是否存在
            try:
                production_plan = ProductionPlan.objects.get(id=plan_id, is_deleted=False)
            except ProductionPlan.DoesNotExist:
                return ResponseWrapper.error('生产计划不存在')
            
            # 验证面料是否存在
            try:
                fabric = Material.objects.get(id=fabric_id, is_deleted=False)
            except Material.DoesNotExist:
                return ResponseWrapper.error('面料不存在')
            
            # 检查面料库存是否充足
            total_inventory = Inventory.objects.filter(
                material=fabric, 
                status='normal'
            ).values_list('quantity', flat=True)
            
            if sum(total_inventory) < quantity:
                return ResponseWrapper.error('面料库存不足')
            
            # 生成任务编号
            task_number = f"CT{timezone.now().strftime('%Y%m%d%H%M%S')}"
            
            # 创建裁剪任务
            cutting_task = CuttingTask.objects.create(
                production_plan=production_plan,
                task_number=task_number,
                material=fabric.name,
                quantity=quantity,
                assigned_to=request.user,
                status='pending',
                remarks=f"裁剪图纸数量: {len(markers)}"
            )
            
            # 返回成功响应
            return ResponseWrapper.success({
                'taskId': cutting_task.id,
                'taskNumber': cutting_task.task_number,
                'message': '裁剪任务创建成功'
            })
            
        except Exception as e:
            return ResponseWrapper.error(f'创建裁剪任务失败: {str(e)}')


class CuttingResultView(views.APIView):
    """
    裁剪结果记录视图
    用于记录裁剪结果，计算实际面料利用率，记录裁剪问题
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 获取请求参数
            task_id = request.data.get('taskId')
            actual_quantity = request.data.get('actualQuantity')
            waste_quantity = request.data.get('wasteQuantity')
            issues = request.data.get('issues', [])
            images = request.data.get('images', [])
            
            # 参数验证
            if not all([task_id, actual_quantity]):
                return ResponseWrapper.error('任务ID和实际数量不能为空')
            
            # 验证裁剪任务是否存在
            try:
                cutting_task = CuttingTask.objects.get(id=task_id, is_deleted=False)
            except CuttingTask.DoesNotExist:
                return ResponseWrapper.error('裁剪任务不存在')
            
            # 验证任务状态
            if cutting_task.status == 'completed':
                return ResponseWrapper.error('该任务已完成，无法再次记录结果')
            
            # 计算面料利用率
            total_quantity = int(actual_quantity) + int(waste_quantity) if waste_quantity else int(actual_quantity)
            utilization_rate = round((int(actual_quantity) / total_quantity) * 100, 2) if total_quantity > 0 else 0
            
            # 更新裁剪任务
            cutting_task.status = 'completed'
            cutting_task.end_time = timezone.now()
            
            # 将裁剪问题和图片信息添加到备注中
            remarks = cutting_task.remarks or ""
            if issues:
                remarks += f"\n裁剪问题: {', '.join(issues)}"
            if images:
                remarks += f"\n裁剪图片: {len(images)}张"
            remarks += f"\n面料利用率: {utilization_rate}%"
            
            cutting_task.remarks = remarks
            cutting_task.save()
            
            # 返回成功响应
            return ResponseWrapper.success({
                'taskId': cutting_task.id,
                'utilizationRate': utilization_rate,
                'message': '裁剪结果记录成功'
            })
            
        except Exception as e:
            return ResponseWrapper.error(f'记录裁剪结果失败: {str(e)}')