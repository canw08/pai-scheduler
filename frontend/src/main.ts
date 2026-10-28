import type { UserModule } from './types'
import { ViteSSG } from 'vite-ssg'

// import "~/styles/element/index.scss";

// import ElementPlus from "element-plus";
// import all element css, uncommented next line
// import "element-plus/dist/index.css";

// or use cdn, uncomment cdn link in `index.html`

import { routes } from 'vue-router/auto-routes'
import App from './App.vue'

import '~/styles/index.scss'
import { refreshAccessToken } from './api';  // 引入刷新 token 的方法
import 'uno.css'
// If you want to use ElMessage, import it.
import 'element-plus/theme-chalk/src/message.scss'
import 'element-plus/theme-chalk/src/message-box.scss'
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

// if you do not need ssg:
// import { createApp } from "vue";

// const app = createApp(App);
// app.use(createRouter({
//   history: createWebHistory(),
//   routes,
// }))
// // app.use(ElementPlus);
// app.mount("#app");

// https://github.com/antfu/vite-ssg

// 创建应用
export const createApp = ViteSSG(
  App,
  {
    routes,
    base: import.meta.env.BASE_URL, // 设置应用的基础路径
  },
  (ctx) => {
    const pinia = createPinia()
    pinia.use(piniaPluginPersistedstate)
    ctx.app.use(pinia)

    // 安装模块，确保 Pinia 和其他模块都能正确工作
    Object.values(import.meta.glob<{ install: UserModule }>('./modules/*.ts', { eager: true }))
      .forEach(i => i.install?.(ctx))

    // 这里是设置路由守卫
    const router = ctx.router

    // 路由守卫 - 检查用户是否登录
    router.beforeEach(async (to, from, next) => {
      let token = sessionStorage.getItem('access_token') // 从 localStorage 中获取 token

      // 如果没有 token，尝试通过刷新 token 来获取新的 access_token
      if (!token) {
        try {
          const refreshResponse = await refreshAccessToken();  // 尝试使用 refresh_token 获取新的 access_token
          sessionStorage.setItem('access_token', refreshResponse.access);  // 将新的 access_token 保存到 sessionStorage
          token = refreshResponse.access;  // 更新 token
          console.log("已更新Access Token")
        } catch (error) {
          if(to.path !== '/nav/login')
          {
            console.error('刷新 Token 失败，跳转到登录页面');
            return next({ path: '/nav/login' });  // 刷新失败，跳转到登录页面
          }
        }
      }
      
      if (token && to.path === '/nav/login') {
        // 如果用户已经登录，且尝试访问登录页面，重定向到首页或其他页面
        next({ path: '/' });  // 可以改成你想重定向的页面
      } else {
        // 其他情况，继续正常路由
        next();
      }
    })
  },
)