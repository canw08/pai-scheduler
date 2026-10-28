<template>
  <el-steps style="max-width: 600px; margin: 0 auto;" :active="0" finish-status="success" align-center>
    <el-step title="设置课程" />
    <el-step title="设置班级" />
    <el-step title="排课设置" />
  </el-steps>

  <div class="table-container">
    <el-table :data="store.courseData" style="width: 80%" max-height="500" align="center" :row-style="getRowStyle">
      <!-- 课程名称 -->
      <el-table-column prop="course" label="课程名称" width="180" align="center">
        <template #default="{ row }">
          <el-select v-model="row.course" placeholder="选择课程" size="small">
            <el-option
              v-for="course in store.presets_courses"
              :key="course.course_name"
              :label="`${course.course_name} (${course.course_type})`" 
              :value="course.course_name"
            />
          </el-select>

        </template>
      </el-table-column>

      <!-- 老师
      <el-table-column prop="teacher" label="老师" width="200" align="center">
        <template #default="{ row }">
          <el-cascader
            v-model="row.teacher"
            :options="store.presets_teachers"
            :props="{ value: 'name', label: 'name', children: 'children' }"
            placeholder="选择老师"
            size="small"
            clearable
          />
        </template>
      </el-table-column> -->

      <!-- 数量 -->
      <el-table-column prop="quantity" label="数量(每周)" width="150" align="center">
        <template #default="{ row }">
          <el-input-number v-model="row.quantity" :min="1" :max="50" size="small" />
        </template>
      </el-table-column>

      <!-- 期望连堂数 -->
      <el-table-column prop="continue" label="期望连堂数" width="150" align="center">
        <template #default="{ row }">
          <el-input-number v-model="row.continue" :min="1" :max="4" size="small" />
        </template>
      </el-table-column>

      <!-- 班级
      <el-table-column prop="class" label="班级" width="150" align="center">
        <template #default="{ row }">
          <el-select v-model="row.class" placeholder="选择班级" size="small">
            <el-option
              v-for="item in store.classData"
              :key="item.class"
              :label="item.class"
              :value="item.class"
            />
          </el-select>
        </template>
      </el-table-column> -->

      <!-- 关联课程 -->
      <el-table-column prop="associatedCourse" label="关联课程" width="150" align="center">
        <template #default="{ row }">
          <div v-if="row.associationType">
            {{ row.associationType }}
          </div>
          <div v-else>
            <el-checkbox
              v-if="linkingCourseId !== null && row.id !== linkingCourseId && !isBound(row.id)"
              v-model="selectedCourses[row.id]"
              @change="() => handleCourseCheck(row.id)"
            />
          </div>
        </template>
      </el-table-column>


    <!-- 操作列 -->
    <el-table-column fixed="right" label="操作" min-width="200" align="center">
      <template #default="scope">
        <div class="flex gap-1 justify-center">
          <template v-if="isBound(scope.row.id)">
            <el-button link type="danger" size="small" @click="() => unbindCourse(scope.row.id)">
              解绑
            </el-button>
          </template>
          <template v-else>
            <el-button
              link
              type="success"
              size="small"
              @click="() => startLinking(scope.row.id, '对开课程')"
            >
              绑定对开
            </el-button>
            <el-button
              link
              type="warning"
              size="small"
              @click="() => startLinking(scope.row.id, '单双周课程')"
            >
              绑定单双周
            </el-button>
          </template>

          <el-button link type="primary" size="small" @click="deleteRow(scope.$index)">
            移除
          </el-button>
        </div>
      </template>
    </el-table-column>


    </el-table>

    <div class="button-container">
      <el-button class="mt-4 small" type="warning" @click="settingFixClass">设置体育课</el-button>
      <el-button class="mt-4 large" type="primary" @click="onAddItem">添加课程</el-button>
    </div>
  </div>

  <el-button type="info" style="margin-top: 12px" class="continue-button" @click="goToNextPage">下一步</el-button>
</template>

<script lang="ts" setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useWaceSetting } from '~/stores/waceSettings'

const router = useRouter()
const store = useWaceSetting()

const linkingType = ref<string>('')
onMounted(() => {
  const waceId = Number(sessionStorage.getItem('wace_id'))

  if (waceId >= 0) {
    store.fetchDataFromBackend().then(() => {
      initializeCourseColors() // ⭐ 加上这个，等后端数据拉完以后自动恢复颜色
    })
  } else {
    router.push('/nav/projects')
  }
})

const colors = [
  '#E6F4EA', // 柔和的绿色系
  '#F2F5FF', // 淡淡的蓝紫色
  '#FFF3E0', // 奶油橙
  '#FDEFF0', // 柔粉
  '#E8F0FE', // 云雾蓝
  '#F0F9EB', // 浅薄荷绿
  '#FAF3DD', // 柔米白
]

const courseColorMap = ref(new Map<number, string>())
const linkingCourseId = ref<number | null>(null)

const getRowColor = (id: number) => {
  return courseColorMap.value.get(id) || ''
}

const getRowStyle = ({ row }: { row: { id: number } }) => {
  const color = getRowColor(row.id)
  return color ? { backgroundColor: color } : {}
}

const bindTwoCourses = (course1: number, course2: number) => {
  const assignedColors = new Set(courseColorMap.value.values())
  const availableColor = colors.find(color => !assignedColors.has(color)) || '#D3D3D3'

  courseColorMap.value.set(course1, availableColor)
  courseColorMap.value.set(course2, availableColor)

  store.courseData.forEach((item) => {
    if (item.id === course1) {
      item.associatedCourse = course2
      item.associationType = linkingType.value // ⭐ 绑定类型
    }
    if (item.id === course2) {
      item.associatedCourse = course1
      item.associationType = linkingType.value // ⭐ 绑定类型
    }
  })

  ElMessage({
    message: `课程 ${course1} 和 ${course2} 已成功绑定为 ${linkingType.value}！`,
    type: 'success',
  })

  linkingCourseId.value = null
  linkingType.value = ''
  selectedCourses.value = {}
}

const handleCourseCheck = (targetId: number) => {
  if (linkingCourseId.value !== null && linkingCourseId.value !== targetId ) {
    bindTwoCourses(linkingCourseId.value, targetId)
  }
}

const initializeCourseColors = () => {
  const assignedColors = new Set<string>()

  store.courseData.forEach(item => {
    if (item.associatedCourse !== undefined && !courseColorMap.value.has(item.id)) {
      // 找一对
      const pairedItem = store.courseData.find(i => i.id === item.associatedCourse)
      if (pairedItem) {
        // 如果两边都还没上色，就上新颜色
        if (!courseColorMap.value.has(item.id) && !courseColorMap.value.has(pairedItem.id)) {
          const availableColor = [...colors].find(color => !assignedColors.has(color)) || '#D3D3D3'
          assignedColors.add(availableColor)

          courseColorMap.value.set(item.id, availableColor)
          courseColorMap.value.set(pairedItem.id, availableColor)
        }
      }
    }
  })
}


const startLinking = (id: number, type: string) => {
  bindCourses()
  linkingCourseId.value = id
  linkingType.value = type
  selectedCourses.value = {}
}

const bindCourses = () => {
  ElMessage({
    message: '请勾选一个其他课程来完成绑定',
    type: 'info'
  })
}

//const courseList = ref(['数学', '英语', '物理', '化学', '生物'])


const selectedCourses = ref<{ [key: number]: boolean }>({})

const deleteRow = (index: number) => {
  unbindCourse(index)
  store.courseData.splice(index, 1)
  store.courseData.forEach((item, index) => item.id = index)
}

const onAddItem = () => {
  store.courseData.push({ id: store.courseData.length,continue:1, course: '', quantity: 1})
}

const isBound = (id: number): boolean => { 
  return  store.courseData.some(item => 
    item.id === id && item.associatedCourse !== undefined ||
    item.associatedCourse === id
  )
}



const unbindCourse = (id: number) => {
  const associatedId =  store.courseData.find(item => item.id === id)?.associatedCourse
  if (associatedId !== undefined) {
    // 清除颜色
    courseColorMap.value.delete(id)
    courseColorMap.value.delete(associatedId)

    // 清除关联字段
    store.courseData.forEach((item) => {
      if (item.id === id || item.id === associatedId) {
        item.associatedCourse = undefined
        item.associationType = undefined
      }
    })

    ElMessage({
      message: `课程 ${id} 和 ${associatedId} 已解除绑定！`,
      type: 'info',
    })
  }
}

const checkValidity = (): boolean => {
  for (let i = 0; i < store.courseData.length; i++) {
    const row = store.courseData[i]
    const rowNum = i + 1

    if (!row.course) {
      ElMessage.error(`第 ${rowNum} 行：课程名称不能为空`)
      return false
    }
    // if (!row.teacher || row.teacher.length === 0) {
    //   ElMessage.error(`第 ${rowNum} 行：老师不能为空`)
    //   return false
    // }
    if (!row.quantity || row.quantity <= 0) {
      ElMessage.error(`第 ${rowNum} 行：数量必须为正整数`)
      return false
    }
    // if (!row.class) {
    //   ElMessage.error(`第 ${rowNum} 行：班级不能为空`)
    //   return false
    // }
  const checkedPairs = new Set<string>()
  for (let row of store.courseData) {
    if (row.associatedCourse !== undefined) {
      const key = [row.id, row.associatedCourse].sort().join('-')
      if (!checkedPairs.has(key)) {
        const target = store.courseData.find(item => item.id === row.associatedCourse)
        if (target && row.quantity !== target.quantity) {
          ElMessage.error(`绑定课程 "${row.course}" 和 "${target.course}" 的课时数不一致，请调整`)
          return false
        }
        checkedPairs.add(key)
      }
    }
  }

  }

  return true
}


const goToNextPage = () => {
  if (checkValidity()) {
    store.sendDataToBackend()
    router.push('/wace/step2')
  }
}


const settingFixClass = () => {
  router.push('/wace/step1-1')
}

function getDivisors(n: number) {
  const divisors: number[] = []
  for (let i = 1; i <= n; i++) {
    if (n % i === 0) {
      divisors.push(i)
    }
  }
  return divisors
}

</script>

<style scoped>
.table-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.button-container {
  display: flex; /* 这里改成flex，原来错了 */
  justify-content: space-between;
  width: 100%;
  max-width: 500px;
  gap: 10px;
}


.large {
  flex: 2;

}

.small {
  flex: 1;

}

.continue-button {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 1000;
}

.goback-button {
  position: fixed;
  left: 160px;
  bottom: 20px;
  z-index: 1000;
}

:deep(.el-table th),
:deep(.el-table td) {
  text-align: center !important;
}
</style>
