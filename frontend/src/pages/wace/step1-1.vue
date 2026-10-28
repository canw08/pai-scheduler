<template>
  <div class="container">
    <!-- 课程表 -->
    <el-card class="schedule">
      <h3>选择 体育课 固定的上课时间</h3>
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
    </el-card>

    <el-button type="info" style="margin-top: 12px" class="goback-button" @click="goToPreviousPage">返回</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useWaceSetting } from '~/stores/waceSettings'

const router = useRouter()
const store = useWaceSetting()

onMounted(() => {
  const waceId = Number(sessionStorage.getItem('wace_id'))
  if (waceId >= 0) {
    store.fetchDataFromBackend()
    if (store.peTimeSetting && store.peTimeSetting.length > 0) {
        schedule.value = JSON.parse(JSON.stringify(store.peTimeSetting))
      } else {
        schedule.value = Array.from({ length: 8 }, () => Array(5).fill(false))
      }
  } else {
    router.push('/nav/projects')
  }
})

// 时间段
const timeSlots = ref([
  '08:30 - 09:15', '09:25 - 10:10', '10:20 - 11:05', '11:15 - 12:00',
  '13:50 - 14:35', '14:45 - 15:30', '15:40 - 16:25', '16:35 - 17:20'
])

// 星期
const days = ['周一', '周二', '周三', '周四', '周五']

// 体育课时间表
const schedule = ref(Array.from({ length: 8 }, () => Array(5).fill(false)))

// 保存体育课安排
const saveSchedule = () => {
  store.peTimeSetting = [...schedule.value] // 保存到 store，自己定义的字段
  ElMessage.success('体育课时间保存成功!')
}

// 返回上一步
const goToPreviousPage = () => {
  store.sendDataToBackend()
  console.log(store.peTimeSetting);
  
  router.push('/wace/step1')
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
}

/* 表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

th, td {
  border: 1px solid #ddd;
  text-align: center;
  padding: 8px;
}

th.time-column {
  width: 120px;
}

.time-cell {
  font-weight: bold;
  background-color: #f5f7fa;
}

/* 卡片样式 */
.schedule {
  width: 80%;
}

/* 返回按钮 */
.goback-button {
  position: fixed;
  left: 160px;
  bottom: 20px;
  z-index: 1000;
}
</style>
