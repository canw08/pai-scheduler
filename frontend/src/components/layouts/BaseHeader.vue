<script lang="ts" setup>
import { repository } from '~/../package.json'
import { UserFilled } from '@element-plus/icons-vue'
import { toggleDark } from '~/composables'
import { useRoute } from 'vue-router';
const route = useRoute();
</script>

<template>
  <el-menu class="el-menu-demo" mode="horizontal" :ellipsis="false" router>
    <el-menu-item index="/">
      <div class="flex items-center justify-center gap-2">
  <img src="/favicon.svg" alt="Logo" class="w-6 h-6" />
        <span>π Editor</span>
  
      </div>
      
    </el-menu-item>
    
    <el-menu-item index="3" disabled>
      没啥用按钮
    </el-menu-item>
    <el-menu-item index="4">
      但我感觉未来应该有用
    </el-menu-item>

    <el-menu-item h="full" @click="toggleDark()">
      <button
        class="w-full cursor-pointer border-none bg-transparent"
        style="height: var(--ep-menu-item-height)"
      >
        <i inline-flex i="dark:ep-moon ep-sunny" />
      </button>
    </el-menu-item>

  </el-menu>
</template>

<style lang="scss">
.el-menu-demo {
  &.ep-menu--horizontal > .ep-menu-item:nth-child(1) {
    margin-right: auto;
  }
}
</style>
