# PAI 排课系统

基于 Vue 3 + Django REST Framework 的排课项目，包含 WACE、ASE 两套排课流程，以及用户、项目和预设管理。

## 功能与技术

- 用户认证：自定义 Django 用户模型和 SimpleJWT。
- 项目与预设管理：创建排课项目、配置与导入预设。
- 自动排课：Python 线程执行 WACE / ASE 任务，支持查询任务状态。
- 课表展示：WACE 提供班级和教师视图；ASE 提供拖动调整；两者均提供 Excel 导出。
- 前端：Vue 3、TypeScript、Vite 6、Element Plus、UnoCSS、Pinia、Vue Router、Axios、SheetJS，部分页面使用 Three.js。
- 后端：Django 5.1.7、DRF、SimpleJWT、django-cors-headers、NumPy、Pandas、OpenPyXL。
- 数据库：SQLite，路径为 `backend/paiclass/db.sqlite3`。

部分页面仍包含占位按钮，具体能力以当前实现为准。

## 目录结构

```text
pai/
├── backend/paiclass/
│   ├── manage.py
│   ├── requirements.txt
│   ├── paiclass/       # Django 配置与总路由
│   ├── users/          # 用户认证
│   ├── projects/       # 排课项目
│   ├── presets/        # 预设与格式转换
│   └── scheduler/      # WACE / ASE 算法及任务接口
├── frontend/
│   ├── src/api.ts      # 后端请求地址
│   ├── src/pages/nav/  # 登录、项目和设置
│   ├── src/pages/wace/ # WACE 排课流程
│   ├── src/pages/ase/  # ASE 排课流程
│   ├── src/components/# 组件与布局
│   ├── src/stores/    # 状态管理
│   └── package.json
└── start.bat           # Windows 开发启动脚本
```

## 本地启动

建议环境：Python 3.11+、Node.js 20+、pnpm 9.15.0（前端声明的包管理器版本）。以下命令在 Windows PowerShell 中执行。

### 后端

从项目根目录执行：

```powershell
cd backend/paiclass
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe manage.py migrate
# 可选：创建管理后台用户
.\venv\Scripts\python.exe manage.py createsuperuser
.\venv\Scripts\python.exe manage.py runserver
```

后端：`http://127.0.0.1:8000`；管理后台：`http://127.0.0.1:8000/admin/`。

### 前端

另开终端，从项目根目录执行：

```powershell
cd frontend
pnpm install
pnpm dev
```

浏览器访问 `http://localhost:5173`。`frontend/src/api.ts` 中的 API 地址为 `http://127.0.0.1:8000`。后端 CORS 配置允许 `http://localhost:5173`，更换前端端口或地址时需要同步修改 Django 设置。

### 一键启动

完成后端依赖安装和数据库迁移后，双击根目录 `start.bat`。它要求虚拟环境位于 `backend/paiclass/venv`；目录中已有的 `backend/venv` 不属于脚本使用的路径。前端依赖不存在时脚本会执行 `pnpm install`。关闭对应服务终端即可停止服务。

## 检查与构建

在 `frontend` 目录执行：

```powershell
pnpm typecheck
pnpm lint
pnpm build
pnpm preview
```

在 `backend/paiclass` 目录执行：

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py test
```

这些是项目提供的检查入口，不代表当前版本已全部通过。

## API 入口

| 路径 | 用途 |
| --- | --- |
| `/api/users/` | 用户接口 |
| `/api/presets/` | 预设接口 |
| `/api/token/refresh/` | 刷新 JWT |
| `/api/project/` | 项目接口 |
| `/api/project/run/` | 启动排课任务 |
| `/api/project/run/status/` | 查询任务状态 |
| `/api/project/fitness/` | 课表适应度检查 |

请求方法、参数和认证要求以应用的 `urls.py` 和 `views.py` 为准。当前 Django 设置用于本地开发，部署前需配置独立密钥、主机白名单和生产环境设置。

## Git 使用说明

当前目录包含三个独立仓库：根目录、`backend`、`frontend`，并未配置为 Git 子模块。需要分别查看状态、暂存和提交；仅提交根目录不会自动提交前后端源码。

```powershell
 git status
 git -C backend status
 git -C frontend status
```

根仓库和后端仓库尚未配置远程；前端已有 `origin` 和模板来源 `upstream`。推送前用 `git remote -v` 或 `git -C frontend remote -v` 核对目标。

迁移电脑后如果遇到 `detected dubious ownership`，确认目录可信后，仅将报错的具体仓库路径加入 Git 的 `safe.directory` 配置。

虚拟环境、依赖目录、SQLite 数据库、缓存和构建产物不应提交。
