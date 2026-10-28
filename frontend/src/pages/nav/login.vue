<template>
  <div class="wrapper">
    <div class="card-switch">
      <input type="checkbox" class="toggle" />
      <span class="slider"></span>
      <span class="card-side"></span>
      <div class="flip-card__inner">
        <div class="flip-card__front">
          <div class="title">登录派克</div>
          <form class="flip-card__form" @submit.prevent="handleLogin">
            <input
              v-model="username"
              class="flip-card__input"
              placeholder="用户名"
              type="text"
            />
            <input
              v-model="password"
              class="flip-card__input"
              placeholder="密码"
              type="password"
            />
            <button :disabled="isLoading" class="flip-card__btn">
              <span v-if="isLoading">正在登录...</span>
              <span v-else>GoGo出发喽</span>
            </button>
          </form>
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { ref } from 'vue';
import api from '~/api';
import { useRouter } from 'vue-router'


export default {
  setup() {
    const username = ref('');
    const password = ref('');
    const isLoading = ref(false);
    const errorMessage = ref('');
    const router = useRouter()

    const handleLogin = async () => {
      isLoading.value = true;
      errorMessage.value = ''; // 清除之前的错误消息

      try {
        const response = await api.post('/api/users/login/', {
          username: username.value,
          password: password.value,
        });

        // 处理成功的响应，保存 access_token 和 refresh_token
        const { access_token, refresh_token } = response.data;

        // 保存 access_token 和 refresh_token
        sessionStorage.setItem('access_token', access_token);  // 用 sessionStorage 存储 Access Token
        localStorage.setItem('refresh_token', refresh_token);  // 用 localStorage 存储 Refresh Token

        // 跳转到主页面
        router.push('projects/').then(() => {
          window.location.reload();  // 跳转后刷新页面
        });
        // router.push('projects/');
      } catch (error: any) {
        // console.error(error);
        // 登录失败时显示错误消息
        errorMessage.value = '用户名或密码错误，请重新输入！';
      } finally {
        isLoading.value = false;
      }
    };

    return {
      username,
      password,
      isLoading,
      errorMessage,
      handleLogin,
    };
  },
};
</script>

<style>
/* From Uiverse.io by andrew-demchenk0 */
.wrapper {
  --input-focus: #2d8cf0;
  --font-color: #323232;
  --font-color-sub: #666;
  --bg-color: #fff;
  --bg-color-alt: #666;
  --main-color: #323232;

  /* 设置 flex 布局并使内容居中 */
  display: flex;
  justify-content: center;  /* 水平居中 */
  align-items: center;      /* 垂直居中 */
  height: 80vh;            /* 使父容器占满整个视口高度 */
}

.toggle {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  box-sizing: border-box;
  border-radius: 5px;
  border: 2px solid var(--main-color);
  box-shadow: 4px 4px var(--main-color);
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--bg-colorcolor);
  transition: 0.3s;
}

.slider:before {
  box-sizing: border-box;
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  border: 2px solid var(--main-color);
  border-radius: 5px;
  left: -2px;
  bottom: 2px;
  background-color: var(--bg-color);
  box-shadow: 0 3px 0 var(--main-color);
  transition: 0.3s;
}

.toggle:checked + .slider {
  background-color: var(--input-focus);
}

.toggle:checked + .slider:before {
  transform: translateX(30px);
}

.toggle:checked ~ .card-side:before {
  text-decoration: none;
}

.toggle:checked ~ .card-side:after {
  text-decoration: underline;
}

/* card */
.flip-card__inner {
  width: 300px;
  height: 350px;
  position: relative;
  background-color: transparent;
  perspective: 1000px;
  text-align: center;
  transition: transform 0.8s;
  transform-style: preserve-3d;
}

.toggle:checked ~ .flip-card__inner {
  transform: rotateY(180deg);
}

.toggle:checked ~ .flip-card__front {
  box-shadow: none;
}

.flip-card__front {
  padding: 20px;
  position: absolute;
  display: flex;
  flex-direction: column;
  justify-content: center;
  -webkit-backface-visibility: hidden;
  backface-visibility: hidden;
  background: lightgrey;
  gap: 20px;
  border-radius: 5px;
  border: 2px solid var(--main-color);
  box-shadow: 4px 4px var(--main-color);
}

.flip-card__form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.title {
  margin: 20px 0 20px 0;
  font-size: 25px;
  font-weight: 900;
  text-align: center;
  color: var(--main-color);
}

.flip-card__input {
  width: 250px;
  height: 40px;
  border-radius: 5px;
  border: 2px solid var(--main-color);
  background-color: var(--bg-color);
  box-shadow: 4px 4px var(--main-color);
  font-size: 15px;
  font-weight: 600;
  color: var(--font-color);
  padding: 5px 10px;
  outline: none;
}

.flip-card__input::placeholder {
  color: var(--font-color-sub);
  opacity: 0.8;
}

.flip-card__input:focus {
  border: 2px solid var(--input-focus);
}

.flip-card__btn:active, .button-confirm:active {
  box-shadow: 0px 0px var(--main-color);
  transform: translate(3px, 3px);
}

.flip-card__btn {
  margin: 20px 0 20px 0;
  width: 120px;
  height: 40px;
  border-radius: 5px;
  border: 2px solid var(--main-color);
  background-color: var(--bg-color);
  box-shadow: 4px 4px var(--main-color);
  font-size: 17px;
  font-weight: 600;
  color: var(--font-color);
  cursor: pointer;
}
</style>
