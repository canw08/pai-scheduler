import pandas as pd
import os
from rest_framework.parsers import MultiPartParser
from django.contrib.auth import get_user_model
from .formatter import *
from django.http import HttpResponse
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Preset

User = get_user_model()


class ImportPresetView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        # 获取上传的文件
        file = request.FILES.get('file')
        preset_type = request.data.get('preset_type')

        # 解析 Excel 文件
        if not file or not preset_type:
            return Response({"error": "File and preset_type are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            xls = pd.ExcelFile(file)
            all_sheets = xls.sheet_names  # 获取所有 sheet 的名称
            df_dict = {sheet: xls.parse(sheet) for sheet in all_sheets}

            formatted_data = FORMATTERS[preset_type](df_dict)

            # 如果是错误响应，它会自动返回
            if isinstance(formatted_data, Response):
                return formatted_data

            # # 数据处理逻辑
            # preset_data = {
            #     'preset_type': preset_type,
            #     'data': {
            #         sheet: df.to_dict(orient='records') for sheet, df in df_dict.items()
            #     }
            # }

            # 获取当前用户
            user = request.user
            preset, created = Preset.objects.update_or_create(
                user=user,
                preset_type=preset_type,
                defaults={'data': formatted_data}
            )

            if created:
                return Response({"message": "Preset imported successfully"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Preset updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ExportPresetView(APIView):

    def get(self, request):
        preset_type = request.query_params.get('preset_type')

        # 确保用户只能获取自己的预设
        preset = Preset.objects.filter(user=request.user, preset_type=preset_type).first()

        if preset:
            return Response({"data": preset.data}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Preset not found"}, status=status.HTTP_404_NOT_FOUND)


class DownloadPresetTemplateView(APIView):
    def get(self, request):
        # 从 query 参数中获取 preset_type，例如 ?preset_type=wace
        preset_type = request.query_params.get('preset_type')

        # 构造模板文件路径，根据不同类型返回不同文件
        if preset_type:
            filename = f'preset_template_{preset_type}.xlsx'
        else:
            filename = 'preset_template.xlsx'  # 默认模板

        template_file_path = os.path.join(settings.BASE_DIR, 'templates', filename)

        if os.path.exists(template_file_path):
            with open(template_file_path, 'rb') as file:
                response = HttpResponse(
                    file.read(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
        else:
            return Response({"error": f"Template for '{preset_type}' not found"}, status=status.HTTP_404_NOT_FOUND)
