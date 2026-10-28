<template>


    <div class="flex h-full">
        <!-- 左侧班级列表 -->
        <div class="w-64 border-r p-4 flex flex-col">
        <el-scrollbar style="flex: 1; min-height: 0;">
            <el-menu :default-active="selectedClassId" @select="handleClassSelect">
            <el-menu-item
                v-for="item in store.classData"
                :key="item.id"
                :index="item.id.toString()"
            >
                {{ item.name }}
            </el-menu-item>
            </el-menu>
        </el-scrollbar>
        <el-button
            type="primary"
            class="mt-4 mb-10 w-full"
            @click="addClass"
        >
            添加班级
        </el-button>
        </div>

  
      <!-- 右侧班级配置 -->
      <div class="flex-1 p-6">
        <div v-if="currentClass">
          <div class="flex items-center mb-4 gap-4">
            <h2 class="text-xl font-bold">{{ currentClass.name }}</h2>
            <!-- 新增：班级属性切换 -->
            <el-radio-group v-model="currentClass.type" size="small" @change="classTypeChange">
              <el-radio-button :label="'理科班'" :value="'理科班'" />
              <el-radio-button :label="'商科班'" :value="'商科班'" />
              <el-radio-button :label="'商理混班'" :value="'商理混班'" />
            </el-radio-group>
          </div>
  
          <!-- 课程-老师表格 -->
            <!-- 课程-老师表格 -->
            <el-table
            :data="currentClass.courses"
            style="width: 100%"
            height="400px"
            header-align="center"
            align="center"
            border
            >
            <el-table-column prop="courseName" label="课程" align="center" />
            <el-table-column label="老师" align="center">
              <template #default="{ row }">
            <el-cascader
              :model-value="getTeacherPath(row.teacher)"
              :options="store.presets_teachers"
              :props="{ value: 'id', label: 'name', children: 'children', emitPath: true }"
              placeholder="选择老师"
              style="width: 150px"
              clearable
              size="small"
              @change="(val: number[] | undefined) => handleTeacherChange(val, row)"
            />

              </template>
            </el-table-column>

            </el-table>


          <!-- 右下角操作 -->
          <div class="flex justify-end mt-6 gap-4">
            
            <el-button type="danger" @click="deleteClass">删除班级</el-button>
            <el-button type="primary" @click="openCourseDialog">配置课程</el-button>
            <el-button type="warning" @click="copyClass">复制班级</el-button>

          </div>
        </div>
        <div v-else class="flex items-center justify-center h-full text-gray-400">
            班级设置:
            请选择一个班级

        </div>
      </div>
  
      <!-- 配置课程弹窗 -->
      <el-dialog v-model="courseDialogVisible" title="配置课程" width="30%">
        <el-checkbox-group v-model="selectedCourses">
          <el-checkbox
            v-for="item in filteredCourses"
            :key="item.label"
            :label="item.value"
          >
            {{ item.label }}
          </el-checkbox>
        </el-checkbox-group>


        <template #footer>
          <el-button @click="courseDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmCourses">确认</el-button>
        </template>
      </el-dialog>
    </div>

    <el-button type="info" style="margin-top: 12px" class="continue-button" @click="goToNextPage">下一步</el-button>
    <el-button type="info" style="margin-top: 12px" class="goback-button" @click="goToPreviousPage">上一步</el-button>
  </template>
  
  <script lang="ts" setup>
  import { ref, computed ,onMounted, ComputedRef} from 'vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { useRouter } from 'vue-router'
  import { useWaceSetting } from '~/stores/waceSettings'
import { classType } from 'element-plus/lib/components/table-v2/src/common.js'
import { log } from 'three/tsl'
import { lo } from 'element-plus/es/locales.mjs'

  const router = useRouter()
  const store = useWaceSetting()

onMounted(async () => {
  const waceId = Number(sessionStorage.getItem('wace_id'))

  if (waceId >= 0) {
    await store.fetchDataFromBackend()

    // console.log('📦 班级数据 classData:', JSON.parse(JSON.stringify(store.classData)))
    // console.log('📦 教师数据 presets_teachers:', JSON.parse(JSON.stringify(store.presets_teachers)))

    // 可选：补全 teacherName
    assignTeacherNames()
  } else {
    router.push('/nav/projects')
  }
})
function assignTeacherNames() {
  for (const cls of store.classData) {
    for (const course of cls.courses) {
      const teacherId = course.teacher
      if (teacherId && teacherId !== -1) {
        const name = findTeacherName(store.presets_teachers, teacherId)
        course.teacherName = name || ''
      } else {
        course.teacherName = ''
      }
    }
  }

  console.log('✅ 补全 teacherName 后的 classData:', JSON.parse(JSON.stringify(store.classData)))
}
function findTeacherName(options: any[], id: number): string | null {
  for (const option of options) {
    if (option.id === id) {
      return option.name
    }
    if (option.children) {
      const found = findTeacherName(option.children, id)
      if (found) return found
    }
  }
  return null
}

  function getTeacherPath(teacherId: number): number[] | undefined {
  let path: number[] = []

  function dfs(options: any[], currentPath: number[]) {
    for (const option of options) {
      const newPath = [...currentPath, option.id]
      if (option.id === teacherId) {
        path = newPath
        return true
      }
      if (option.children && dfs(option.children, newPath)) {
        return true
      }
    }
    return false
  }

  dfs(store.presets_teachers, [])
  return path.length > 0 ? path : undefined
}



  

  
  const selectedClassId = ref<string>('')
  const selectedCourses = ref<string[]>([])
  
  const courseDialogVisible = ref(false)
  
  const currentClass = computed(() => {
    return store.classData.find(c => c.id.toString() === selectedClassId.value)
  })
  
  function handleClassSelect(id: string) {
    selectedClassId.value = id
  }
  
  function reassignClassNames() {
    store.classData.forEach((cls, index) => {
      cls.id = index + 1
      cls.name = `班级${index + 1}` + " - " + cls.type
    })
    // 重新选择一个存在的班级
    selectedClassId.value = store.classData.length > 0 ? store.classData[store.classData.length-1].id.toString() : ''
  }
  
  function classTypeChange() {
    if (currentClass.value) {
      currentClass.value.courses = [] // 清空已选课程
    }
    store.classData.forEach((cls, index) => {
      cls.id = index + 1
      cls.name = `班级${index + 1}` + " - " + cls.type
    })
  }

  function addClass() {
    store.classData.push({
      id: 0, // 临时
      name: '',
      type: '理科班', // 默认
      courses: [],
    })
    reassignClassNames()
  }
  
  function deleteClass() {
    ElMessageBox.confirm(
      '确定要删除这个班级吗？',
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(() => {
      const index = store.classData.findIndex(c => c.id.toString() === selectedClassId.value)
      if (index !== -1) {
        store.classData.splice(index, 1)
        reassignClassNames()
      }
    }).catch(() => {})
  }
  
  function copyClass() {
  if (currentClass.value) {
    const newClass = {
      id: 0, // 临时ID
      name: '',
      type: currentClass.value.type,
      courses: currentClass.value.courses.map(course => ({
        courseName: course.courseName,
        courseId: course.courseId,   // 复制courseId
        teacher: course.teacher,
        teacherName: course.teacherName
      })),
    }
    store.classData.push(newClass)
    reassignClassNames()
  }
}


function openCourseDialog() {
  if (!currentClass.value) return

  const selected: string[] = []
  const handled = new Set<string>()
  const classType = currentClass.value.type

  const typeMap: Record<string, string> = {
    "商理混班": "COMMON",
    "理科班": "SCI",
    "商科班": "BUS",
  }

  const allowedCourseType = typeMap[classType]

  const isCourseAllowed = (courseName: string): boolean => {
    const preset = store.presets_courses.find(c => c.course_name === courseName)
    return preset ? preset.course_type === allowedCourseType : false // 若找不到则默认允许
  }

  for (const courseItem of currentClass.value.courses) {
    const courseName = courseItem.courseName
    if (handled.has(courseName)) continue
    if (!isCourseAllowed(courseName)) continue

    const courseData = store.courseData.find(c => c.course === courseName)
    console.log(courseName);
    if (courseData && courseData.associatedCourse && classType === "商理混班") {
      const associatedCourseData = store.courseData.find(c => c.id === courseData.associatedCourse)
      
      if (
        associatedCourseData &&
        isCourseAllowed(associatedCourseData.course)
      ) {
        selected.push(`${courseName}/${associatedCourseData.course}`)
        handled.add(courseName)
        handled.add(associatedCourseData.course)
      } else {
        selected.push(courseName)
        handled.add(courseName)
      }
    } else {
      selected.push(courseName)
      handled.add(courseName)
    }
  }

  console.log(handled);
  

  selectedCourses.value = selected
  courseDialogVisible.value = true
}



  
function confirmCourses() {
  if (currentClass.value) {
    const newCourses: { courseName: string; courseId: number; teacher: number , teacherName: string}[] = []

    for (const course of selectedCourses.value) {
      if (course.includes('/')) {
        const [first, second] = course.split('/')

        const firstCourse = store.courseData.find(c => c.course === first)
        const secondCourse = store.courseData.find(c => c.course === second)

        if (firstCourse) {
          newCourses.push({ courseName: firstCourse.course, courseId: firstCourse.id, teacher: -1 , teacherName: ''})
        }
        if (secondCourse) {
          newCourses.push({ courseName: secondCourse.course, courseId: secondCourse.id, teacher: -1 , teacherName: ''})
        }

      } else {
        const courseData = store.courseData.find(c => c.course === course)
        if (courseData) {
          newCourses.push({ courseName: courseData.course, courseId: courseData.id, teacher: -1 , teacherName: ''})
        }
      }
    }

    currentClass.value.courses = newCourses
    courseDialogVisible.value = false
  }
}


function validateClassHours() {
  const errors: string[] = []
  let requiredSlots = 35

  if (store.daySlots == 8) {
    requiredSlots = 39
  }

  for (let classIndex = 0; classIndex < store.classData.length; classIndex++) {
    const cls = store.classData[classIndex]
    let totalHours = 0
    const handledCourses = new Set<number>()
    const relatedCourseMessages: string[] = []

    for (const course of cls.courses) {
      if (handledCourses.has(course.courseId)) {
        continue // 已经统计过了
      }

      const courseInfo = store.courseData.find(c => c.id === course.courseId)

      if (!courseInfo) {
        errors.push(`${cls.name} 中找不到课程 ${course.courseName} 的信息`)
        continue
      }

      if (courseInfo.associatedCourse) {
        // 单双周课程，只加一次
        const associatedInfo = store.courseData.find(c => c.id === courseInfo.associatedCourse)

        if (associatedInfo) {
          totalHours += (courseInfo.quantity || 0)
          handledCourses.add(courseInfo.id)
          handledCourses.add(associatedInfo.id)

          relatedCourseMessages.push(`${cls.name} 中课程 ${course.courseName} / ${associatedInfo.course} 是关联课程，只计一次课时`)
        } else {
          totalHours += (courseInfo.quantity || 0)
          handledCourses.add(courseInfo.id)
        }
      } else {
        totalHours += (courseInfo.quantity || 0)
        handledCourses.add(courseInfo.id)
      }
    }

      // peTimeSetting 是 boolean[][]
      const peTime = store.peTimeSetting || [];

      let peCount = 0;

      // 遍历每一天
      for (const day of peTime) {
        if (Array.isArray(day)) {
          peCount += day.filter(v => v).length; // 统计这一行有多少 true
        }
      }

      // 后面加上总课时
      totalHours += peCount;
    
    if (totalHours !== requiredSlots) {
      errors.push(...relatedCourseMessages)
      errors.push(`${cls.name} 的总课时是 ${totalHours} 节（应为${requiredSlots}节）`)
      
    }
  }

  if (errors.length > 0) {
    ElMessageBox.alert(errors.join('<br/>'), '课时检查错误', {
      confirmButtonText: '确定',
      type: 'warning',
      dangerouslyUseHTMLString: true,
    })
    return false
  } else {
    ElMessage.success('所有班级课时检查通过！')
    return true
  }
}


function validateTeachers() {
  const errorLines: string[] = []

  for (const cls of store.classData) {
    for (const course of cls.courses) {
      if (course.teacher === -1 || course.teacher === undefined || course.teacher === null) {
        errorLines.push(`${cls.name} 中课程 ${course.courseName} 未选择老师`)
      }
    }
  }

  if (errorLines.length > 0) {
    ElMessageBox.alert(errorLines.join('<br/>'), '老师选择检查错误', {
      confirmButtonText: '确定',
      type: 'warning',
      dangerouslyUseHTMLString: true,
    })
    return false
  } else {
    ElMessage.success('所有课程老师选择通过！')
    return true
  }
}


const goToNextPage = () => {
  if(!validateTeachers()) return
  if (!validateClassHours()) return
  store.sendDataToBackend()
  router.push('/wace/step3')
}


const goToPreviousPage = () => router.push('/wace/step1')

const filteredCourses = computed(() => {
  if (!currentClass.value) return []

  const classType = currentClass.value.type
  const allowedTypes = classType === '理科班'
    ? ['COMMON', 'SCI']
    : classType === '商科班'
      ? ['COMMON', 'BUS']
      : ['COMMON', 'SCI', 'BUS']

  const result: { label: string; value: string }[] = []
  const usedCourses = new Set<string>()

  for (const cd of store.courseData) {
    if (!cd.course) continue
    if (usedCourses.has(cd.course)) continue

    const preset = store.presets_courses.find(pc => pc.course_name === cd.course)
    if (!preset) continue
    if (!allowedTypes.includes(preset.course_type)) continue

    if (cd.associatedCourse && (cd.associationType !== "对开课程") || (currentClass.value.type === "商理混班")) {
      const associated = store.courseData.find(c => c.id === cd.associatedCourse)
      if (associated) {
        result.push({
          label: `${cd.course} / ${associated.course}`,
          value: `${cd.course}/${associated.course}`, // 合并成一个字符串
        })
        usedCourses.add(cd.course)
        usedCourses.add(associated.course)
      } else {
        result.push({
          label: cd.course,
          value: cd.course,
        })
        usedCourses.add(cd.course)
      }
    } else {
      result.push({
        label: cd.course,
        value: cd.course,
      })
      usedCourses.add(cd.course)
    }
  }

  return result
})

function handleTeacherChange(value: number[] | undefined, row: any) {
  if (!value || value.length === 0) {
    row.teacher = -1
    row.teacherName = ''
    return
  }

  const teacherId = value[value.length - 1]  // 取最后一项
  row.teacher = teacherId

  function findTeacherName(options: any[], id: number): string | null {
    for (const option of options) {
      if (option.id === id) {
        return option.name
      }
      if (option.children) {
        const found = findTeacherName(option.children, id)
        if (found) return found
      }
    }
    return null
  }

  const name = findTeacherName(store.presets_teachers, teacherId)
  if (name) {
    row.teacherName = name
  } else {
    row.teacherName = ''
  }
}



  </script>
  

  
  <style scoped>

  
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

  /* 额外的居中已在 element-plus 自带表格属性里设置 align="center"，这里不用写额外CSS */
  </style>
  