<template>
  <div class="container">
    <div ref="threeCanvas" class="three-canvas"></div>
    <div class="progress-text">当前课表满足率 {{ progress }}%</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref } from 'vue'
import * as THREE from 'three'
import api from '~/api'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

const threeCanvas = ref<HTMLDivElement | null>(null)
const progress = ref(0) // 从后端获取的适应度上限 (0 ~ 100)

const status = ref('running')

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let particles: THREE.Points
let animationId: number
let intervalId: number

const particleCount = 5000
const radius = 300

const fitnessList: number[] = []
const growthRates: number[] = []

function initThree() {
  scene = new THREE.Scene()

  camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 2000)
  camera.position.z = 800
  scene.rotation.y = 1
  scene.rotation.x = 1

  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(window.innerWidth, window.innerHeight)

  if (threeCanvas.value) {
    threeCanvas.value.appendChild(renderer.domElement)
  }

  const positions = new Float32Array(particleCount * 3)
  const colors = new Float32Array(particleCount * 3)

  for (let i = 0; i < particleCount; i++) {
    const angle = Math.random() * Math.PI * 2
    const r = radius + (Math.random() - 0.5) * 1000
    const x = Math.cos(angle) * r
    const z = Math.sin(angle) * r
    const y = (Math.random() - 0.5) * 400

    positions[i * 3] = x
    positions[i * 3 + 1] = y
    positions[i * 3 + 2] = z

    colors[i * 3] = 1.0
    colors[i * 3 + 1] = 0.0
    colors[i * 3 + 2] = 0.0

    // 初始化适应度和增长率
    fitnessList.push(0)
    growthRates.push(0.00001 + Math.random() * 0.00004)
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  const material = new THREE.PointsMaterial({
    size: 10,
    vertexColors: true,
  })

  particles = new THREE.Points(geometry, material)
  scene.add(particles)
}

function updateFitnessAndColor() {
  const colorAttr = particles.geometry.getAttribute('color') as THREE.BufferAttribute
  const maxFitness = progress.value / 100

  for (let i = 0; i < particleCount; i++) {
    if (fitnessList[i] < maxFitness) {
      fitnessList[i] += growthRates[i]
      if (fitnessList[i] > maxFitness) {
        fitnessList[i] = maxFitness
      }
    }

    const f = fitnessList[i]
    const r = 1.0 - f
    const g = f
    const b = 0.0

    colorAttr.setXYZ(i, r, g, b)
  }

  colorAttr.needsUpdate = true
}

function animate() {
  animationId = requestAnimationFrame(animate)
  updateFitnessAndColor()
  scene.rotation.y += 0.002
  scene.rotation.x += 0.002
  renderer.render(scene, camera)
}

async function fetchProgress() {
  try {
    const response = await api.get(`/api/project/run/status?id=${Number(sessionStorage.getItem('ase_id')) || null}`)
    progress.value = response.data.progress
    status.value = response.data.status
  } catch (error) {
    console.error('获取排课进度失败:', error)
  }
}

onMounted(() => {
  initThree()
  animate()
  fetchProgress()
  intervalId = window.setInterval(() => {
    if (status.value !== 'running') {
      if (intervalId) clearInterval(intervalId)
      router.push('/ase/result')
      ElMessage.success("排课已完成! 正在跳转...")
    } else {
      fetchProgress()
    }
  }, 1000)
})

onBeforeUnmount(() => {
  cancelAnimationFrame(animationId)
  clearInterval(intervalId)
  if (threeCanvas.value && renderer) {
    threeCanvas.value.removeChild(renderer.domElement)
  }
})
</script>

<style scoped>
.container {
  position: relative;
}

.three-canvas {
  width: 100%;
  height: 100vh;
  background: #000;
  overflow: hidden;
}

.progress-text {
  position: absolute;
  bottom: 100px;
  left: 20px;
  color: white;
  font-size: 18px;
  background-color: rgba(0, 0, 0, 0.6);
  padding: 6px 12px;
  border-radius: 8px;
}
</style>
