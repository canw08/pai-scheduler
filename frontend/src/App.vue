<template>
  <el-config-provider namespace="ep">
    <!-- 根据路由判断是否显示 BaseHeader 和 BaseSide -->
    <BaseHeader v-if="!isLoginPage" />
    <div class="main-container flex">
      <BaseSide v-if="!isLoginPage" />
      <div w="full" py="4">
        <!-- 路由视图 -->
        <RouterView />
      </div>
    </div>
  </el-config-provider>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue';
import { useRoute } from 'vue-router';

export default defineComponent({
  name: 'App',
  computed: {
    // 判断当前页面是否是登录页面
    isLoginPage(): boolean {
      const route = useRoute();
      return route && route.name === '/nav/login';  // 确保 $route 存在
    },
  },
});
</script>

<style>
#app {
  text-align: center;
  color: var(--ep-text-color-primary);
}

.main-container {
  height: calc(100vh - var(--ep-menu-item-height) - 4px);
}
</style>
