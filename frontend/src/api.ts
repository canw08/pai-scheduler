// src/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000', // 替换为你的后端 API 地址
  timeout: 5000, // 可根据需求设置请求超时时间
  headers: {
    'Content-Type': 'application/json',
  }
});

// 刷新 access_token 的接口
export const refreshAccessToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh_token');

    const response = await api.post('/api/token/refresh/', {
      refresh: refreshToken
    });
    
    return response.data; // 返回新的 access_token
  } catch (error) {
    console.error('Refresh token failed:', error);
    throw error; // 如果刷新失败，则抛出异常
  }
};

// 设置请求拦截器
api.interceptors.request.use(
  async (config) => {
    const token = sessionStorage.getItem('access_token');
    const isLoginRequest = config.url === '/api/users/login/';  // 判断是否为登录请求
    const isRefreshRequest = config.url === '/api/token/refresh/';  // 判断是否为刷新请求
    const isTokenExpired = token && isExpired(token);  // 判断 token 是否过期

    // 如果是登录请求，直接放行
    if (isLoginRequest || isRefreshRequest) {
      return config;
    }


    if (isTokenExpired) {
      try {
        const data = await refreshAccessToken();
        sessionStorage.setItem('access_token', data.access);  // 更新 access_token
        config.headers['Authorization'] = `Bearer ${data.access}`;  // 更新请求头的 Authorization
      } catch (error) {
        // 刷新失败时跳转到登录页面
        window.location.href = '/nav/login';  // 或者使用 router.push('/nav/login') 进行跳转
        throw error;  // 抛出异常，停止请求
      }
    } else {
      config.headers['Authorization'] = `Bearer ${token}`;  // 如果 access_token 存在且有效，直接加到请求头
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 判断 access_token 是否过期的辅助函数
function isExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));  // 解码 token 获取 payload
    const exp = payload.exp * 1000;  // exp 是秒级时间戳，需要转换为毫秒
    return Date.now() > exp;  // 如果当前时间大于过期时间，则表示 token 已过期
  } catch (e) {
    console.error('Error decoding token', e);
    return true;  // 如果无法解码 token，默认为过期
  }
}
export default api;
