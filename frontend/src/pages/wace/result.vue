<template>
<div class="schedule-container">
<h1>{{ scheduleType === 'class' ? '班级课表' : '教师课表' }} - {{ currentSchedule[currentIndex]?.name }}</h1>

<!-- 切换课表类型的按钮 -->
<div class="toggle-buttons">
<el-button :type="scheduleType === 'class' ? 'primary' : 'default'" @click="switchSchedule('class')">班级</el-button>
<el-button :type="scheduleType === 'teacher' ? 'primary' : 'default'" @click="switchSchedule('teacher')">老师</el-button>
</div>

<div class="table-wrapper">
<!-- 左侧切换按钮 -->
<el-button class="nav-button left" :disabled="currentIndex === 0" @click="prevSchedule">
<el-icon><ArrowLeft /></el-icon>
</el-button>

<!-- 课程表 -->
<el-table v-if="currentSchedule.length > 0" :data="currentSchedule[currentIndex]?.schedule" border>
<el-table-column prop="time" label="时间" width="120" align="center" />
<el-table-column prop="monday" label="星期一" align="center" />
<el-table-column prop="tuesday" label="星期二" align="center" />
<el-table-column prop="wednesday" label="星期三" align="center" />
<el-table-column prop="thursday" label="星期四" align="center" />
<el-table-column prop="friday" label="星期五" align="center" />
</el-table>

<!-- 右侧切换按钮 -->
<el-button class="nav-button right" :disabled="currentIndex === currentSchedule.length - 1" @click="nextSchedule">
<el-icon><ArrowRight /></el-icon>
</el-button>
</div>

<div class="conflict-buttons">
<!-- <el-button type="warning" class="regenerate-button" @click="showConflicts('low')">查看冲突</el-button> -->
<el-button type="danger" class="regenerate-button" @click="regenerateSchedule">重新生成</el-button>
<el-button type="primary"class="regenerate-button" @click="handleExport">导出 Excel</el-button>

</div>

<!-- 侧边栏 - 冲突详情 -->
<!-- <el-drawer v-model="isDrawerOpen" title="冲突详情" direction="rtl">
<p v-if="conflictDetails.length === 0">暂无冲突</p>
<ul v-else>
<li v-for="(conflict, index) in conflictDetails" :key="index">
  {{ conflict }}
</li>
</ul>
</el-drawer> -->
</div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useWaceSetting } from '~/stores/waceSettings'
import api from '~/api'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

const DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
const SLOTS_PER_DAY = 7

const router = useRouter()
const store = useWaceSetting()

const scheduleType = ref<'class' | 'teacher'>('teacher')
const teacherSchedules = ref<{ name: string, schedule: any[] }[]>([])
const classSchedules = ref<{ name: string, schedule: any[] }[]>([])

const currentIndex = ref(0)
const currentSchedule = computed(() =>
  scheduleType.value === 'teacher' ? teacherSchedules.value : classSchedules.value
)

const isDrawerOpen = ref(false)
const conflictDetails = ref<string[]>([])

const switchSchedule = (type: 'class' | 'teacher') => {
  scheduleType.value = type
  currentIndex.value = 0
}

const prevSchedule = () => { if (currentIndex.value > 0) currentIndex.value-- }
const nextSchedule = () => { if (currentIndex.value < currentSchedule.value.length - 1) currentIndex.value++ }

const regenerateSchedule = () => { router.push('/wace/step4') }

const conflicts = { low: ['数学和物理时间冲突', '英语教师时间不匹配'] }
const showConflicts = (level: 'low') => {
  conflictDetails.value = conflicts[level] || []
  isDrawerOpen.value = true
}

function exportSchedulesToExcel(fileName: string, schedules: { name: string; schedule: Record<string, string>[] }[]) {
  const workbook = XLSX.utils.book_new()

  schedules.forEach(schedule => {
    const worksheet = XLSX.utils.json_to_sheet(schedule.schedule)
    XLSX.utils.book_append_sheet(workbook, worksheet, schedule.name)
  }) 

  const wbout = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([wbout], { type: 'application/octet-stream' })
  saveAs(blob, fileName)
}


const getTeacherName = (id: number | string) => {
  for (const group of store.presets_teachers) {
    const match = group.children.find(t => t.id === Number(id))
    if (match) return match.name
  }
  return `教师${id}`
}

const getCourseName = (id: number | string) => {
  const match = store.courseData.find(c => c.id === Number(id))
  if (match && match.course) return match.course

  const presetMatch = store.presets_courses.find((c, index) => index === Number(id))
  if (presetMatch) return presetMatch.course_name

  return `课程${id}`
}


const handleExport = () => {
  exportSchedulesToExcel("班级课表.xlsx",classSchedules.value)
  exportSchedulesToExcel("老师课表.xlsx",teacherSchedules.value)
}


// 处理教师课表
const transformTeacherSchedule = (data: Record<string, number[][]>) => {
  const result = []

  for (const [teacherId, entries] of Object.entries(data)) {
    const table: Record<string, string>[] = []

    for (let i = 0; i < SLOTS_PER_DAY; i++) {
      const row: Record<string, string> = {
        time: `第${i + 1}节`
      }
      DAYS.forEach(day => row[day] = '')
      table.push(row)
    }

    for (const entry of entries) {
      const [slot, courseId, classId, weekType] = entry
      const dayIndex = Math.floor(slot / SLOTS_PER_DAY)
      const timeIndex = slot % SLOTS_PER_DAY
      const dayKey = DAYS[dayIndex]
      const courseName = getCourseName(courseId)
      const className = `班级${classId + 1}`
      const weekNote = weekType === 1 ? '（单双周）' : ''

      if (table[timeIndex] && dayKey) {
        table[timeIndex][dayKey] = `${courseName}(${className})${weekNote}`
      }
    }

    result.push({
      name: getTeacherName(teacherId),
      schedule: table
    })
  }

  return result
}

const transformClassSchedule = (data: Record<string, any[][][]>) => {
  const result = []

  for (const [classId, weeklySchedule] of Object.entries(data)) {
    const table: Record<string, string>[] = []

    for (let i = 0; i < SLOTS_PER_DAY; i++) {
      const row: Record<string, string> = { time: `第${i + 1}节` }
      DAYS.forEach(day => row[day] = '')
      table.push(row)
    }

    for (let dayIndex = 0; dayIndex < weeklySchedule.length; dayIndex++) {
      const dailySchedule = weeklySchedule[dayIndex]

      for (let timeIndex = 0; timeIndex < dailySchedule.length; timeIndex++) {
        const cell = dailySchedule[timeIndex]
        const contents: string[] = []

        if (!cell) continue

        const cellArray = Array.isArray(cell[0]) ? cell : [cell]

        for (const pair of cellArray) {
          if (!Array.isArray(pair)) continue

          const marker = pair[4] // 'OddEven', 'Related' 或 undefined

          const isDualCourse = pair.length >= 4 && typeof pair[2] !== 'undefined' && typeof pair[3] !== 'undefined'

          if (isDualCourse) {
            const [courseId1, teacherId1, courseId2, teacherId2] = pair

            const getCourseDisplay = (courseId: string, teacherId: string) => {
              if (teacherId === 'PHE Teacher') return 'PE'
              const courseName = getCourseName(courseId)
              const teacherName = getTeacherName(teacherId)
              return `${courseName}(${teacherName})`
            }

            const note = marker === 'OddEven' ? '（单双周）' : marker === 'Related' ? '（对开）' : ''
            contents.push(`${getCourseDisplay(courseId1, teacherId1)} / ${getCourseDisplay(courseId2, teacherId2)}${note}`)

          } else {
            const [courseId, teacherId] = pair
            let courseDisplay = ''

            if (teacherId === 'PHE Teacher') {
              courseDisplay = 'PE'
            } else {
              const courseName = getCourseName(courseId)
              const teacherName = getTeacherName(teacherId)
              courseDisplay = `${courseName}(${teacherName})`
            }

            const note = marker === 'OddEven' ? '（单双周）' : marker === 'Related' ? '（对开）' : ''
            contents.push(`${courseDisplay}${note}`)
          }
        }

        const dayKey = DAYS[dayIndex]
        table[timeIndex][dayKey] = contents.join(' / ')
      }
    }

    result.push({
      name: `班级${Number(classId)}`,
      schedule: table
    })
  }

  return result
}





// 加载后端数据
onMounted(async () => {
  const waceId = Number(sessionStorage.getItem('wace_id'))
  if (waceId >= 0) {
    await store.fetchDataFromBackend()

    const res = await api.get(`/api/project/get?id=${waceId}`)
    const table = res.data.table
    

    if (table.teacher_time_table) {
      teacherSchedules.value = transformTeacherSchedule(table.teacher_time_table)
    }

    if (table.time_table) {
      classSchedules.value = transformClassSchedule(table.time_table)
    }

    console.log(classSchedules.value);
    

  } else {
    router.push('/nav/projects')
  }
})
</script>



<style scoped>
.schedule-container {
display: flex;
flex-direction: column;
align-items: center;
text-align: center;
padding: 20px;
}

.toggle-buttons {
display: flex;
gap: 10px;
margin-bottom: 20px;
}

.table-wrapper {
display: flex;
align-items: center;
gap: 10px;
width: 100%;
max-width: 1500px;
}

.nav-button {
border: none;
font-size: 24px;
cursor: pointer;
}

.conflict-buttons {
display: flex;
gap: 10px;
margin-top: 20px;
}

.regenerate-button {
margin-top: 20px;
}
</style>
