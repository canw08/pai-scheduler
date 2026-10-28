# scheduler/tasks.py
import threading
import time  # 用来模拟长时间运行的任务
from django.utils import timezone
from .models import SchedulingTask
from django.db import models
from projects.models import Project
from scheduler.formatTranslater import transform_schedule
from presets.models import Preset
from .wace import runAutomaticSchedulingForWace
from .ase import runAutomaticSchedulingForAse
# from .ase import afterDrag
import json


def run_WACE_scheduling(project, task):
    """WACE排课程序"""
    try:

        task.status = 'running'
        task.start_time = timezone.now()
        task.save()

        preset = Preset.objects.filter(user=project.user, preset_type="preset_wace").first()
        config = transform_schedule(project.config, preset.data)
        # print(json.dumps(config, ensure_ascii=False, indent=2))
        # print(config)
        output = runAutomaticSchedulingForWace(config)
        project.table = output
        project.save()
        # print(json.dumps(output, ensure_ascii=False, indent=4))

        # 更新状态
        task.status = 'completed'
        task.end_time = timezone.now()
        task.save()
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        print(e)
        task.save()


def run_ASE_scheduling(project, task):
    """ASE排课程序"""
    try:
        task.status = 'running'
        task.start_time = timezone.now()
        task.save()

        output = runAutomaticSchedulingForAse(project.config, task)
        project.table = output
        project.save()
        print(json.dumps(output, ensure_ascii=False, indent=4))

        # 更新状态
        task.status = 'completed'
        task.end_time = timezone.now()
        task.save()
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        print(e)
        task.save()


def run_ASE_fitnessCalculate(project, task):
    """ASE排课程序"""
    try:
        task.status = 'running'
        task.start_time = timezone.now()
        task.save()

        # output = afterDrag(project.config, project.table[1])
        # project.table[0] = output
        project.save()

        # 更新状态
        task.status = 'completed'
        task.end_time = timezone.now()
        task.save()
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        print(e)
        task.save()


def start_scheduling_task(project_id):
    """根据 project 类型来选择不同的排课程序"""
    project = Project.objects.get(id=project_id)

    task = SchedulingTask.objects.create(project=project)
    # 启动不同的排课程序
    if project.project_type == 'project_wace':
        threading.Thread(target=run_WACE_scheduling, args=(project, task)).start()
    elif project.project_type == 'project_ase':
        threading.Thread(target=run_ASE_scheduling, args=(project, task)).start()
    else:
        task.status = 'failed'
        task.error_message = 'Unknown project type'
        task.save()


def start_fitnessCaculate_task(project_id):
    """根据 project 类型来选择不同的排课程序"""
    project = Project.objects.get(id=project_id)

    task = SchedulingTask.objects.create(project=project)
    # 启动不同的排课程序
    if project.project_type == 'project_ase':
        threading.Thread(target=run_ASE_fitnessCalculate, args=(project, task)).start()
    else:
        task.status = 'failed'
        task.error_message = 'Unknown project type'
        task.save()
