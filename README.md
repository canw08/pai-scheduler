# PAI 排课系统

一个基于 Vue 3 + Django 的智能排课系统。

## 技术栈

### 前端
- Vue 3
- Vite
- TypeScript
- Element Plus
- UnoCSS
- Pinia (状态管理)
- Vue Router

### 后端
- Python 3.11+
- Django 5.1
- Django REST Framework
- SimpleJWT (认证)
- Pandas / NumPy (数据处理)
- OpenPyXL (Excel 导出)

## 快速开始

### 一键启动（推荐）

双击根目录下的 `start.bat` 文件，即可同时启动前端和后端服务。

### 手动启动

#### 后端

```bash
cd backend/paiclass
# 激活虚拟环境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

后端默认运行在 `http://localhost:8000`

#### 前端

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

前端默认运行在 `http://localhost:5173`

## 项目结构

```
pai/
├── frontend/          # 前端 Vue 项目
│   ├── src/
│   │   ├── assets/    # 静态资源
│   │   ├── components/# 组件
│   │   ├── composables/# 组合式函数
│   │   ├── pages/     # 页面
│   │   ├── styles/    # 样式
│   │   └── types.ts   # 类型定义
│   └── package.json
│
├── backend/           # 后端 Django 项目
│   ├── paiclass/
│   │   ├── manage.py
│   │   ├── paiclass/  # Django 配置
│   │   ├── users/     # 用户模块
│   │   ├── presets/   # 预设模块
│   │   ├── projects/  # 项目模块
│   │   └── scheduler/ # 排课模块
│   └── venv/          # Python 虚拟环境
│
├── start.bat          # 一键启动脚本
└── README.md
