# scheduler/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from projects.models import Project
from .task import start_scheduling_task
from .task import start_fitnessCaculate_task
from .models import SchedulingTask


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_run(request):
    project_id = request.data.get('id')
    if not project_id:
        return Response({'error': '缺少项目 ID'}, status=400)

    try:
        project = Project.objects.get(id=project_id, user=request.user)

        # 检查是否已经有正在运行的任务
        existing_task = SchedulingTask.objects.filter(project=project, status='running').first()
        if existing_task:
            return Response({'error': f"项目 {project_id} 正在运行排课任务，无法启动新的任务"}, status=400)

        # 启动排课任务
        start_scheduling_task(project.id)
        return Response({'success': True, 'message': '排课任务已启动'})
    except Project.DoesNotExist:
        return Response({'error': '项目不存在'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def project_checkFitness(request):
    project_id = request.data.get('id')
    if not project_id:
        return Response({'error': '缺少项目 ID'}, status=400)

    try:
        project = Project.objects.get(id=project_id, user=request.user)

        # 检查是否已经有正在运行的任务
        existing_task = SchedulingTask.objects.filter(project=project, status='running').first()
        if existing_task:
            return Response({'error': f"项目 {project_id} 正在运行任务，无法启动新的任务"}, status=400)

        # 启动排课任务
        start_fitnessCaculate_task(project.id)
        return Response({'success': True, 'message': '适应度计算任务已启动'})
    except Project.DoesNotExist:
        return Response({'error': '项目不存在'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_run_status(request):
    project_id = request.query_params.get('id')
    if not project_id:
        return Response({'error': '缺少项目 ID'}, status=400)

    try:
        # 获取最新的排课任务
        task = SchedulingTask.objects.filter(project_id=project_id).order_by('-start_time').first()

        if task:
            return Response({
                'status': task.status,
                'progress': task.progress,
                'start_time': task.start_time,
                'end_time': task.end_time,
                'error_message': task.error_message,
            })
        else:
            return Response({'error': '未找到相关排课任务'}, status=404)
    except SchedulingTask.DoesNotExist:
        return Response({'error': '排课任务未找到'}, status=404)
