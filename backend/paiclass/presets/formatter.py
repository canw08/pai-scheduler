# presets/utils/formatter.py
# formatter.py
from rest_framework.response import Response

# Sheet 名 + 列名映射表
SHEET_FORMAT_CONFIG_WACE = {
    '老师': {
        'sheet_key': 'teachers',
        'columns': {
            '老师名称': 'teacher_name',
            '所属部门（ASE/WACE/BSE）': 'department'
        }
    },
    '课程': {
        'sheet_key': 'courses',
        'columns': {
            '课程名称': 'course_name',
            '课程类型（SCI/BUS/common）': 'course_type'
        }
    }
}


def format_preset_wace(sheet_dict):
    formatted_data = {}

    for original_sheet_name, config in SHEET_FORMAT_CONFIG_WACE.items():
        # 校验 Sheet 是否存在
        if original_sheet_name not in sheet_dict:
            return Response({"error": f"缺少必要的 Sheet: {original_sheet_name}"}, status=400)

        df = sheet_dict[original_sheet_name]
        columns_mapping = config['columns']
        new_sheet_key = config['sheet_key']

        # 校验列
        missing = [col for col in columns_mapping if col not in df.columns]
        if missing:
            return Response({"error": f"{original_sheet_name} 缺少列: {', '.join(missing)}"}, status=400)

        # 重命名列
        df = df.rename(columns=columns_mapping)

        # 如果是老师表，插入 ID 列
        if new_sheet_key == 'teachers':
            df.insert(0, 'teacher_id', range(1, len(df) + 1))  # 从 1 开始编号，插入到最前面

        # 存入以新 sheet_key 命名的键值对
        formatted_data[new_sheet_key] = df.to_dict(orient='records')

    return formatted_data


FORMATTERS = {
    'preset_wace': format_preset_wace
}
