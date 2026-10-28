<template>
  <el-steps style="max-width: 600px; margin: 0 auto;" :active="2" finish-status="success" align-center>
    <el-step title="设置课程" />
    <el-step title="设置班级" />
    <el-step title="排课设置" />
  </el-steps>
  
  <h1>最后一些设置🥱</h1>

  
  <el-button type="warning" @click="settingTeachers">设置老师特殊情况</el-button>

  <el-button type = "info" style="margin-top: 12px" class="continue-button" @click="goToNextPage">下一步</el-button>
  <el-button type = "info" style="margin-top: 12px" class="goback-button" @click="goToPreviousPage">上一步</el-button>

</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
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


const goToNextPage = () => {
  router.push('/wace/step4') // 跳转到下一步
}

const goToPreviousPage = () => {
  router.push('/wace/step2') // 跳转到上一步
}

const settingTeachers = () => {
  router.push('/wace/step3-1')
}



const settingContinueClass = () => {
  router.push('/wace/step3-3')
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

</style>


 