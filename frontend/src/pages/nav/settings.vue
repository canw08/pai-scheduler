<template>
  <div class="settings-page">
    <el-card class="settings-card">
      <div class="settings-header">
        <h2>这里是设置但是不知道有啥可设置的</h2>
      </div>

      <el-divider />

      <div class="settings-item">
        <el-button type="danger" @click="handleLogout" plain>
          退出登录
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script lang="ts" setup>
import { ElMessageBox, ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 模拟清除登录状态（根据你的实际逻辑调整）
    sessionStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')

    ElMessage.success('已退出登录')

    // 跳转到登录页
    router.push('nav/login')
    window.location.reload()
  }).catch(() => {
    ElMessage.info('已取消退出')
  })
}
</script>

<style scoped>
.settings-page {
  display: flex;
  justify-content: center;
  padding: 80px 16px;
}

.settings-card {
  width: 400px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.settings-item {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
