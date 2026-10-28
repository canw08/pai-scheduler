<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from '~/api';

interface Teacher {
  name: string;
  department: string;
}

interface Course {
  name: string;
  category: string;
}

const teachers = ref<Teacher[]>([]);
const courses = ref<Course[]>([]);

// 上传文件引用
const fileInput = ref<HTMLInputElement | null>(null);

// 上传用的预设类型（你可以根据需要改为固定值或由用户选择）
const presetType = ref("preset_wace");  // 这里用 default，按需改动

// 页面加载时从 API 获取数据
const importPresetData = async () => {
  try {
    const response = await api.get('/api/presets/export/', {
      params: {
        preset_type: presetType.value,
      },
    });
    const data = response.data.data;

    teachers.value = data.teachers.map((t: any) => ({
      name: t.teacher_name,
      department: t.department
    }));

    courses.value = data.courses.map((c: any) => ({
      name: c.course_name,
      category: c.course_type
    }));
  } catch (error) {
    console.error("导入预设数据失败:", error);
  }
};

onMounted(() => {
  importPresetData();
});

// 触发文件选择
const triggerFileInput = () => {
  fileInput.value?.click();
};

// 处理上传逻辑
const handleFileUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("preset_type", presetType.value);  // 可动态传递不同预设类型

  try {
    await api.post("/api/presets/import/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    // 上传成功后重新获取数据
    importPresetData();
  } catch (error) {
    console.error("上传文件失败:", error);
  } finally {
    // 清空 input 防止连续上传相同文件不触发 change 事件
    target.value = "";
  }
};
</script>

<template>
  <div style="padding: 20px">
    <el-button type="warning">下载模板</el-button>
    <el-button type="primary" @click="triggerFileInput">导入预设</el-button>
    <input
      ref="fileInput"
      type="file"
      accept=".xlsx, .xls"
      style="display: none"
      @change="handleFileUpload"
    />

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div style="text-align: center; font-weight: bold">教师信息</div>
          </template>
          <el-table :data="teachers" border style="width: 100%">
            <el-table-column prop="name" label="教师名称" header-align="center" align="center" min-width="120" />
            <el-table-column prop="department" label="所属部门" header-align="center" align="center" min-width="120" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div style="text-align: center; font-weight: bold">课程信息</div>
          </template>
          <el-table :data="courses" border style="width: 100%">
            <el-table-column prop="name" label="课程名称" header-align="center" align="center" min-width="120" />
            <el-table-column prop="category" label="课程类别" header-align="center" align="center" min-width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.el-card {
  min-height: 250px;
}
</style>
