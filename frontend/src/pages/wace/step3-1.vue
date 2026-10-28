<template>
  <div class="container">
    <!-- 老师列表 -->
    <el-card class="teacher-list">
      <el-scrollbar height="400px">
        <el-menu>
          <el-menu-item 
            v-for="teacher in teachers" 
            :key="teacher.id" 
            @click="selectTeacher(teacher)"
            :class="{ 'selected': teacher.id === selectedTeacher?.id }">
            {{ teacher.name }}
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-card>

    <!-- 课程表 -->
    <el-card class="schedule">
      <div v-if="selectedTeacher">
        <h3>选择 {{ selectedTeacher.name }} 无法上课的时间段</h3>
        <table>
          <thead>
            <tr>
              <th class="time-column">时间段</th>
              <th v-for="day in days" :key="day">{{ day }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(time, rowIndex) in timeSlots" :key="rowIndex">
              <td class="time-cell">{{ time }}</td>
              <td v-for="(day, colIndex) in days" :key="colIndex">
                <el-checkbox v-model="schedule[rowIndex][colIndex]" size="small" />
              </td>
            </tr>
          </tbody>
        </table>
        <el-button type="primary" class="save-button" @click="saveSchedule">保存</el-button>
      </div>
      <p v-else>请选择一位老师</p>
    </el-card>
  </div>
  <el-button type = "info" style="margin-top: 12px" class="goback-button" @click="goToPreviousPage">返回</el-button>

</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { onMounted } from 'vue';
import { useWaceSetting } from '~/stores/waceSettings';

const router = useRouter()
const store = useWaceSetting();


onMounted(() => {
  const waceId = Number(sessionStorage.getItem('wace_id'));
  if (waceId >= 0) {
    store.fetchDataFromBackend();
  }
  else
  {
    router.push('/nav/projects');
  }
});


// 提取所有班级中的老师，并去重
const teachers = computed(() => {
  const teacherIds = new Set<number>();

  for (const cls of store.classData) {
    for (const course of cls.courses) {
      const teacherField = course.teacher;
      
      if (Array.isArray(teacherField)) {
        // 如果是数组，提取所有有效id
        for (const id of teacherField) {
          if (typeof id === 'number' && !isNaN(id)) {
            teacherIds.add(id);
          }
        }
      } else if (typeof teacherField === 'number') {
        // 如果是单个数字，直接添加
        teacherIds.add(teacherField);
      }
    }
  }
  //console.log(teacherIds);
  
  // 2. 根据 presets_teachers 查找名字
  const allTeachers: { id: number; name: string }[] = [];
  for (const group of store.presets_teachers) {
    for (const teacher of group.children) {
      if (teacherIds.has(teacher.id)) {
        allTeachers.push({ id: teacher.id, name: teacher.name });
      }
    }
  }

  return allTeachers;
});


const selectedTeacher = ref<{ id: number; name: string } | null>(null);

// 课程表时间段
const timeSlots = ref([
  '08:30 - 09:15', '09:25 - 10:10', '10:20 - 11:05', '11:15 - 12:00',
  '13:50 - 14:35', '14:45 - 15:30', '15:40 - 16:25', '16:35 - 17:20'
]);

// 星期几
const days = ['周一', '周二', '周三', '周四', '周五'];

// 初始化课程表
const schedule = ref(Array.from({ length: 8 }, () => Array(5).fill(false)));

// 选择老师
const selectTeacher = (teacher: { id: number; name: string }) => {
  selectedTeacher.value = teacher;
  // 加载已保存的时间表，如果存在
  if (store.teacherTimeSetting[teacher.id]) {
    schedule.value = [...store.teacherTimeSetting[teacher.id]];
  } else {
    // 如果没有保存过，则清空数据
    schedule.value = Array.from({ length: 8 }, () => Array(5).fill(false));
  }
};

// 保存课程表
const saveSchedule = () => {
  if (selectedTeacher.value) {
    // 将当前课程表保存到 teacherSchedules 中
    store.teacherTimeSetting[selectedTeacher.value.id] = [...schedule.value];
    ElMessage({
      message: '保存成功!',
      type: 'success',
    })
  }
};

// 返回上一页
const goToPreviousPage = () => {
  store.sendDataToBackend()
  router.push('/wace/step3') // 跳转到上一步
}
</script>

<style scoped>
.container {
  display: flex;
  width: 90%;
  gap: 20px;
  padding: 20px;
}

/* 老师列表样式 */
.teacher-list {
  width: 200px;
}

.teacher-list .el-menu-item {
  text-align: center;
}

.teacher-list .selected {
  background-color: #409eff !important;
  color: white;
}

/* 课程表样式 */
.schedule {
  flex: 1;
}

/* 表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

/* 控制时间段列的宽度 */
th.time-column {
  width: 120px;
}

th, td {
  border: 1px solid #ddd;
  text-align: center;
  padding: 8px;
}

/* 时间段列样式 */
.time-cell {
  font-weight: bold;
  background-color: #f5f7fa;
}

.goback-button {
  position: fixed;
  left: 160px;
  bottom: 20px;
  z-index: 1000;
}
</style>
