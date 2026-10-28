<template>
  <div ref="canvasContainer" class="viewer-container"></div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import * as THREE from 'three'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'

const canvasContainer = ref<HTMLDivElement | null>(null)

onMounted(() => {
  if (!canvasContainer.value) return

  const scene = new THREE.Scene()
  scene.background = new THREE.Color(0xeeeeee)

  const camera = new THREE.PerspectiveCamera(
    75,
    canvasContainer.value.clientWidth / canvasContainer.value.clientHeight,
    0.1,
    1000
  )
  camera.position.set(0, 1, 3)
 
  const renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
  canvasContainer.value.appendChild(renderer.domElement)

  const light = new THREE.HemisphereLight(0xffffff, 0x444444, 1)
  scene.add(light)

  const loader = new GLTFLoader()
  loader.load('/models/htm.glb', (gltf: { scene: THREE.Object3D<THREE.Object3DEventMap> }) => {
    scene.add(gltf.scene)
  })

  const controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true

  const animate = () => {
    requestAnimationFrame(animate)
    controls.update()
    renderer.render(scene, camera)
  }

  animate()

  window.addEventListener('resize', () => {
    if (!canvasContainer.value) return
    camera.aspect = canvasContainer.value.clientWidth / canvasContainer.value.clientHeight
    camera.updateProjectionMatrix()
    renderer.setSize(canvasContainer.value.clientWidth, canvasContainer.value.clientHeight)
  })
})
</script>

<style scoped>
.viewer-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>
