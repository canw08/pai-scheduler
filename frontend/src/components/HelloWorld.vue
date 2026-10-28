<template>
  <div class="main-container">
    <!-- 标语 -->
    <h1 class="headline">
      <span class="fade-in first">拖拽之间</span><span class="fade-in second">，完美课表诞生。</span>
    </h1>
    <h2 class="subheadline">
      <span class="fade-in first">Drag & Drop</span><span class="fade-in second">, A Perfect Schedule is Born.</span>
    </h2>

    <!-- 立即开始按钮 -->
    <el-button type="primary" class="start-button" color='#626aef' @click="startScheduling">
      立即开始排课
    </el-button>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

// 跳转到排课页面
const startScheduling = () => {
  router.push("/nav/projects"); // 跳转到排课页面
};
</script>

<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 90vh; /* 居中 */
  text-align: center;
  background-color: #f8f9fa; /* 浅灰色背景 */
  transform: translateY(-10px); /* 整体上移一些 */
}

.headline {
  font-size: 2.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 20px;
}

.subheadline {
  font-size: 1.5rem;
  color: #666;
  margin-bottom: 50px;
}

/* 文字淡入动画 */
.fade-in {
  opacity: 0;
  animation: fadeIn 1.5s forwards;
}

/* 第一部分（逗号前）先出现 */
.first {
  animation-delay: 0.3s;
}

/* 第二部分（逗号后）稍后出现 */
.second {
  animation-delay: 1.2s;
}

/* 渐入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px); /* 轻微上移动画 */
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.start-button {
  font-size: 1.2rem;
  padding: 12px 24px;
  margin-top: 20px; /* 与文字拉开一点距离 */
  opacity: 0;
  animation: fadeIn 1.5s forwards 2s; /* 按钮稍后显示 */
}
</style>
