<template>
  <el-steps style="max-width: 600px; margin: 0 auto;" :active="0" finish-status="success" align-center>
    <el-step title="上传文件" />
    <el-step title="开始排课!!!" />
  </el-steps>
<p class="upload-hint">请上传 Excel 文件，系统将根据您提供的数据进行自动排课。</p>

  <!-- 上传区域容器，设置最大宽度 -->
  <div class="upload-section">
      <el-upload
        class="upload-demo"
        drag
        :before-upload="handleExcelUpload"
        action=""
        multiple
      >

      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到这里<em> 点击上传也可以</em>
      </div>
      <template #tip>
      </template>
    </el-upload>

    <!-- 下载模板按钮 -->
    <el-button type="primary" @click="downloadTemplate" class="download-button">下载模板文件</el-button>
  </div>
<!-- <pre v-if="parsedData" style="text-align: left; white-space: pre-wrap; max-width: 400px; margin: auto;">
  {{ parsedData }}
</pre> -->
</template>


<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { UploadFilled } from '@element-plus/icons-vue'
import * as XLSX from 'xlsx' // 👈 引入 xlsx
import axios from 'axios'
import { ElMessage } from 'element-plus'
import api from '~/api';

const router = useRouter()
const parsedData = ref<Record<string, any[]> | null>(null) // 存储解析后的 JSON

const goToNextPage = () => {
  // 你可以把 parsedData.value 存储进全局 store 后跳转
  router.push('/wace/step2')
}

// 👇 下载模板函数
const downloadTemplate = () => {
  const link = document.createElement('a')
  link.href = '/template.xlsx'
  link.download = '排课模板.xlsx'
  link.click()
}

// 👇 文件上传前读取并解析为 JSON（不上传）
const handleExcelUpload = (file: File) => {
  const reader = new FileReader()

  reader.onload = async (e: ProgressEvent<FileReader>) => {
    const data = new Uint8Array(e.target!.result as ArrayBuffer)
    const workbook = XLSX.read(data, { type: 'array' })

    const result: Record<string, any[]> = {}

    workbook.SheetNames.forEach(sheetName => {
      const worksheet = workbook.Sheets[sheetName]
      const json = XLSX.utils.sheet_to_json(worksheet, { defval: '' }) // 保留空单元格
      result[sheetName] = json
    })

    parsedData.value = result
    console.log('解析结果:', result)

    const validResult = validateScheduleConfig(result)

    if (!validResult.valid) {
      console.error("配置验证失败：")
      validResult.errors.forEach(err => ElMessage.error(err))
      
    } else {
      console.log("配置合法 ✅")
    // ✅ 自动发送到后端
    await sendParsedDataToBackend(result)
    }


  }

  reader.readAsArrayBuffer(file)
  return false // 阻止 el-upload 默认上传
}

const sendParsedDataToBackend = async (data: Record<string, any[]>) => {
  const requestData = {
    id: Number(sessionStorage.getItem('ase_id')) || null,
    config: data,
  }
  
  const requestDataRun = {
    id: Number(sessionStorage.getItem('ase_id')) || null
  }

  try {
    const response = await api.post('/api/project/edit/', requestData)
    console.log(requestData);
    
    console.log('上传成功:', response.data)
    ElMessage.success('文件解析并上传成功！')

    const responseDataRun = await api.post('/api/project/run/', requestDataRun)
    router.push('/ase/step2')
  } catch (error) {
    console.error('上传失败:', error)
    ElMessage.error('上传失败，请检查网络或接口。')
  }
}

function validateScheduleConfig(json: any): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  // // 顶层结构检查
  // if (!json || typeof json !== 'object' || !json.config) {
  //   return { valid: false, errors: ['缺少 "config" 字段或格式错误'] }
  // }

  const config = json

  // 校验非数学课设置
  if (!Array.isArray(config["非数学课设置"])) {
    errors.push('未找到 "非数学课设置" 表')
  } else {
    config["非数学课设置"].forEach((item: any, index: number) => {
      if (!item["课程名称"]) errors.push(`非数学课设置[${index}] 缺少 "课程名称"`)
      if (!item["老师名称"]) errors.push(`非数学课设置[${index}] 缺少 "老师名称"`)
      if (typeof item["班级数"] !== 'number') errors.push(`非数学课设置[${index}] 的 "班级数" 应为数字`)
    })
  }

  // 校验数学课设置
  if (!Array.isArray(config["数学课设置"])) {
    errors.push('未找到 "数学课设置" 表')
  } else {
    config["数学课设置"].forEach((item: any, index: number) => {
      if (!item["课程名称"]) errors.push(`数学课设置[${index}] 缺少 "课程名称"`)
      if (!item["老师名称"]) errors.push(`数学课设置[${index}] 缺少 "老师名称"`)
      if (typeof item["班级数"] !== 'number') errors.push(`数学课设置[${index}] 的 "班级数" 应为数字`)
    })
  }

// 校验学生信息
if (!Array.isArray(config["学生信息"])) {
  errors.push('未找到 "学生信息" 表')
    return {
    valid: errors.length === 0,
    errors
  }
}

for (let index = 0; index < config["学生信息"].length; index++) {
  const student = config["学生信息"][index]
  const requiredFields = ["学生姓名", "英文中教课", "英文外教课", "数学课"]

  // 固定字段检查
  for (const field of requiredFields) {
    if (!student[field]) {
      errors.push(`学生信息[${index}] 缺少 "${field}"`)
      return {
    valid: errors.length === 0,
    errors
  }
    }
  }

  // 动态检查所有“选修课”字段
  const electiveKeys = Object.keys(student).filter(key => key.startsWith("选修课"))
  if (electiveKeys.length === 0) {
    errors.push(`学生信息[${index}] 至少需要一个 "选修课" 字段`)
    return {
    valid: errors.length === 0,
    errors
  }
  }
}


  return {
    valid: errors.length === 0,
    errors
  }
}

</script>



<style scoped>
.upload-section {
  max-width: 400px;
  margin: 20px auto;
  text-align: center;
}

.upload-demo {
  width: 100%;
  margin-bottom: 12px;
}

.download-button {
  margin-top: 10px;
}

.continue-button {
  position: fixed;
  right: 20px;
  bottom: 20px;
  z-index: 1000;
}

/* 保留你的其他样式 */
.table-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.button-container {
  display: flex;
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
