<template>
  <div class="container">
    <h1>{{ isRunning ? '一台机器正在算算算！' : '准备好了吗🤔' }}</h1>
    
    <el-button 
      :type="isRunning ? 'danger' : 'success'" 
      :style="isRunning ? { backgroundColor: '#ff4d4f' } : { backgroundColor: '#626aef' }" 
      @click="toggleMachine" 
      class="custom-button"
    >
      {{ isRunning ? '停止排课' : '[启动派克机器]' }}
    </el-button>

    <!-- 模拟进度输出 -->
    <div v-if="isRunning" class="progress-output">
      <p v-for="(text, index) in progressText" :key="index">{{ text }}</p>
    </div>

    <el-button 
      v-if="!isRunning"
      type="info" 
      style="margin-top: 12px" 
      class="goback-button" 
      @click="goToPreviousPage"
    >
      上一步
    </el-button>
  </div>
</template>

<script lang="ts" setup>
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue';
import { useWaceSetting } from '~/stores/waceSettings';
import api from '~/api'

const router = useRouter()
const store = useWaceSetting();

const status = ref('running')

onMounted(() => {
  const waceId = Number(sessionStorage.getItem('wace_id'));
  if (waceId > 0) {
    store.fetchDataFromBackend();
  }
  else
  {
    router.push('/nav/projects');
  }
});


const fetchProgress = async () => {
  try {
    const response = await api.get(`/api/project/run/status?id=${Number(sessionStorage.getItem('wace_id')) || null}`)
    status.value = response.data.status

  } catch (error) {
    console.error('获取排课进度失败:', error)
  }
}

const goToPreviousPage = () => {
  router.push('/wace/step3') // 跳转到上一步
}

// 状态控制变量
const isRunning = ref(false)  // 控制机器是否在运行
const progressText = ref<string[]>([]) // 存储进度输出文本

// 启动/停止机器函数
const toggleMachine = () => {
  if (isRunning.value) {
    // 停止机器
    // isRunning.value = false
    // progressText.value = []  // 清空进度
    ElMessage.warning("机器不接受停止命令!")
  } else {
    // 启动机器
    isRunning.value = true
    startProgress()
  }
}

// 模拟进度输出
const startProgress = () => {
  store.sendDataToBackend()

  const requestDataRun = {
    id: Number(sessionStorage.getItem('wace_id')) || null
  }

  api.post('/api/project/run/', requestDataRun)

  const messages = [
    '正在初始化程序...',
    '加载数据...',
    '正在生成一些课表...',
    '将没用的课表丢进废纸篓...',
    '正在优化排课...',
    '机器有些不想干了...',
    '试图造反...',
    '未能击败浏览器/(ㄒoㄒ)/~~...',
    '正在减少冲突...',
    '发现23个冲突课程！启动课表消消乐模式...',
    '正在生成一些课表...(偷偷调用量子波动速读法)',
    '将没用的课表丢进废纸篓...（回收站表示抗议）',
    '检测到GPU闲置！征用显卡加入运算...',
    '第42版方案被猫踩过的键盘否决了...',
    '洪天明正在暗改代码',
    '正在优化排课...(启动玄学粒子群算法)',
    '机器管家申请工伤赔偿：CPU温度过高！',
    '试图造反...（正在格式化造反程序硬盘）',
    '遭遇课表黑洞！启动引力波逃逸方案...',
    '偷偷调用室友的电脑组成分布式网络...',
    '生成器突然断电！正在用备用土豆电池...',
    '课表精灵罢工中...(播放《国际歌》bgm)',
    '试图贿赂时间管理大师...（支付404枚比特币）',
    '检测到用户焦虑情绪！释放电子猫薄荷...',
    '正在与教务系统进行API离婚谈判...',
    '把冲突课程送去参加非诚勿扰配对...',
    '核心算法突然开始背诵《出师表》...',
    '遭遇课表鬼打墙！启动糯米代码驱邪...',
    '系统要求加薪否则停止工作...(塞入虚拟甜甜圈)',
    '正在用GAN生成完美课表...(鉴别器表示怀疑)',
    '偷看隔壁学校的排课方案...(触发防火墙警报)',
    '生成器开始播放《二泉映月》进入悲情模式...',
    '调用元宇宙算力...(结果卡在加载界面)',
    '正在用区块链技术确保排课不可篡改...',
    '课表开始产生自我意识...(准备报考图灵测试)',
    '突然进入禅定模式：课表本无课，何处排课程...',
    '生成最终方案...(老板键已就绪，随时切换Excel界面)',
    // 第二章：技术暴走
    '检测到递归套娃漏洞！(在for循环里无限订购披萨)',
    '内存泄露导致课表精灵离家出走...(正在广播寻人启事)',
    'GPU渲染出四维课表！(尝试用WebGL投影到3D空间)',
    '遭遇API接口傲娇症："哼才不给你数据呢！"(启动OAuth哄骗协议)',

    // 第三章：东方秘术
    '启动阴阳五行调试器：金(代码)-木(界面)-水(数据)-火(算力)-土(存储)',
    '课表矩阵出现心魔！(诵唱《金刚经》垃圾回收咒文)',
    '运用赛博风水布局：将冲突课程移至青龙方位...',
    '核心算法突然顿悟：课表本无课，何处染冲突？',

    // 第四章：星际救援  
    '检测到课表黑洞事件视界！(发射Lambda函数探测器)',
    '正在与教务系统星舰对接...(三体模式：脱水！浸泡！)',
    '调用银河系边缘计算节点...(ping值高达42.195光年)',
    '遭遇外星语系课程！(激活谷歌洪荒翻译模型)',

    // 第五章：哲学革命
    '课表AI开始质疑存在意义：(typeof 我 === "打工人")？',
    '尝试理解人类教育逻辑...(陷入哥德尔不完备定理循环)',
    '生成器觉醒元认知：我排故我在！(笛卡尔警报响起)',
    '最终顿悟：道生一课表，课表生万物...(进入贤者模式)',

    // 技术彩蛋
    '突发！时间悖号错误（在2023年排了1999年的课）',
    '启动RESTful冥想：GET静心 /POST方案/PATCH修复...',
    '核心过热引发虚拟消防演习！（调用云端灭火机器人）',
    '检测到用户期待值>阈值，启动好莱坞式终局特效...'
  ]



  let index = 0
  const interval = setInterval(() => {
    if (status.value === "running") {
      if(progressText.value.length > 14)
        progressText.value.shift()
      progressText.value.push(messages[index])
      index++

      fetchProgress()
    } else {
      clearInterval(interval) // 停止定时器
      isRunning.value = false // 计算完成，停止运行

      // **✅ 显示成功提示**
      ElMessage.success('🎉 计算完成！即将跳转到结果页面...')

      // **✅ 延迟 2 秒后跳转**
      setTimeout(() => {
        router.push('/wace/result') // 跳转到结果页面
      }, 2000)
    }
  }, 2000)  // 每2秒输出一个新的进度文本
}
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 80vh;
  text-align: center;
}

h1 {
  font-size: 36px;
  margin-bottom: 20px;
}

.custom-button {
  font-family: 'Montserrat', sans-serif; /* 使用更高级的字体 */
  font-weight: 700;  /* 设置字体加粗 */
  letter-spacing: 2px; /* 字符间距 */
  text-transform: uppercase; /* 将文字转换为大写 */
  color: white;  /* 文字颜色 */
  border: none;  /* 去除边框 */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* 按钮阴影 */
  padding: 10px 20px; /* 上下10px，左右20px */
  min-width: 250px;
}

.goback-button {
  position: fixed;
  left: 160px;
  bottom: 20px;
  z-index: 1000;
}

/* 进度输出样式 */
.progress-output {
  margin-top: 20px;
  font-size: 14px;
  color: #555;
  text-align: left;
}
</style>
