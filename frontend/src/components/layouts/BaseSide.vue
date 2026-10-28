<script lang="ts" setup>
import {
  Document,
  Menu as IconMenu,
  UserFilled,
  Location,
  Setting,
} from '@element-plus/icons-vue'

// const isCollapse = ref(true)
function handleOpen(key: string, keyPath: string[]) {

}
function handleClose(key: string, keyPath: string[]) {

}
</script>

<template>
  <el-menu
    router
    default-active="1"
    class="el-menu-vertical-demo"
    @open="handleOpen"
    @close="handleClose"
  >
    <el-menu-item index="/nav/projects">
      <el-icon>
        <IconMenu />
      </el-icon>
      <template #title class>
        课程表工作台
      </template>
    </el-menu-item>
    <el-sub-menu index="1">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>排课预设</span>
          </template>
          <el-menu-item index="/wace/preset">WACE 预设</el-menu-item>
          <!-- <el-menu-item index="1-2">ASE 预设</el-menu-item> -->
          <el-menu-item index="1-1">BSE 预设</el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/nav/4">
      <el-icon>
        <UserFilled />
      </el-icon>
      <template #title>
        账号管理
      </template>
    </el-menu-item>

    <el-menu-item index="/nav/settings">
      <el-icon>
        <Setting />
      </el-icon>
      <template #title>
        设置
      </template>
    </el-menu-item>

  </el-menu>
</template>
