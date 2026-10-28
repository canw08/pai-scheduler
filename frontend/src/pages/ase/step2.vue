<template>
    <div class="progress-title">😵 系统真的在努力计算了!...</div>

<div class="progress-wrapper">
  <span class="progress-label">0%</span>
  
  <div class="progress-container">
    <div
      class="progress-layer"
      v-for="(bar, index) in progressLayers"
      :key="index"
      :style="{ width: bar.percentage + '%', zIndex: index + 1 }"
    >
      <el-progress
        :percentage="100"
        :color="bar.color"
        :stroke-width="24"
        :show-text="false"
        :status="'success'"
      />
    </div>
  </div>
  
  <span class="progress-label">100%</span>
</div>

<div class="progress-description">
  当前满足度{{ progress }}%， 排课进度反映学生的选课满足率，系统正在尽可能安排每位学生想上的课。
</div>


<div class="progress-tips" v-html="currentTip"></div>

</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '~/api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

const progress = ref(0)
const status = ref('running')
const intervalId = ref<number | null>(null)

// const projectId = 34 // 根据需要动态传入

const fetchProgress = async () => {
  try {
    const response = await api.get(`/api/project/run/status?id=${Number(sessionStorage.getItem('ase_id')) || null}`)
    progress.value = response.data.progress
    status.value = response.data.status

  } catch (error) {
    console.error('获取排课进度失败:', error)
  }
}

onMounted(() => {
  fetchProgress()
  intervalId.value = window.setInterval(() => {
    if (status.value !== 'running') {
      if (intervalId.value) clearInterval(intervalId.value)
      router.push('/ase/result')
      ElMessage.success("排课已完成! 正在跳转...")
    } else {
      fetchProgress()
    }
  }, 1000) // 每秒轮询一次
})

onUnmounted(() => {
  if (intervalId.value) clearInterval(intervalId.value)
})


interface ProgressLayer {
  percentage: number
  color: string
}

const progressLayers = ref<ProgressLayer[]>([])

// 高对比颜色序列
const colorPalette = [
  '#A8DADC', // 柔和蓝绿
  '#F4A261', // 柔和橙
  '#E9C46A', // 柔和黄
  '#9D8189', // 温暖灰粉
  '#B5E48C', // 柔和黄绿
  '#89C2D9', // 柔和天蓝
  '#FFB4A2', // 淡珊瑚
  '#CDB4DB', // 柔和紫
]

const tips = [
  '你知道吗, 洪天明是本项目贡献最多的路人!',
  'Tips: 别盯着我看了，去休息一下吧',
  '我觉得这里应该写一点小故事',
  '你知道吗，这其实是我开发的第一个完整的前后端分离网站',
  '如果你觉得这个界面有些单调 不妨试试这个 <a href="#" class="clickable-tip">点击进入</a>',
  '你知道吗, 美高界面的开发仅用了两天(非净含量)',
]

const currentTip = ref(tips[0])
let tipIndex = 0

let colorIndex = 0

const getNextColor = () => {
  const color = colorPalette[colorIndex]
  colorIndex = (colorIndex + 1) % colorPalette.length
  return color
}

const startNewLayer = () => {
  const newLayer: ProgressLayer = {
    percentage: 0,
    color: getNextColor(),
  }

  progressLayers.value.push(newLayer)
  const currentIndex = progressLayers.value.length - 1
  const stopPoint = progress.value

  const interval = setInterval(() => {
    const current = progressLayers.value[currentIndex]
    if (!current) return

    if (current.percentage >= stopPoint) {
      clearInterval(interval)
      // 自动启动下一段
      setTimeout(() => startNewLayer(), 20)
    } else {
      current.percentage += 1
    }
  }, 30)
}


const startTipRotation = () => {
  setInterval(() => {
    tipIndex = (tipIndex + 1) % tips.length
    currentTip.value = tips[tipIndex]
  }, 6000) // 每 3 秒切换一次
}

onMounted(() => {
  startNewLayer()
  startTipRotation()
    document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    if (target.classList.contains('clickable-tip')) {
      e.preventDefault()
      handleTipClick()
    }
  })
})

const handleTipClick = () => {
  router.push('/ase/step2-3d') // 可选跳转
}

</script>

<style scoped>
.progress-title {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
  margin-top: 200px;
}

.progress-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  margin-top: 12px;
}

.progress-label {
  width: 30px;
  text-align: center;
  font-size: 12px;
  color: #888;
}

.progress-container {
  position: relative;
  width: 600px;
  height: 30px;
  background-color: #ebeef5;
  border-radius: 12px;
  overflow: hidden;
}

.progress-layer {
  position: absolute;
  left: 0;
  top: 3px;
  height: 100%;
  transition: width 1s ease;
  border-radius: 5px;
}

.progress-description {
  text-align: center;
  font-size: 14px;
  color: #666;
  margin-top: 16px;
}

.progress-tips {
  text-align: center;
  font-size: 12px;
  color: #aaa;
  margin-top: 250px;
  font-style: italic;
  transition: opacity 0.5s ease;
}

.progress-tips a.clickable-tip {
  color: #409EFF; /* Element Plus 主色蓝 */
  text-decoration: underline;
  cursor: pointer;
}


</style>
