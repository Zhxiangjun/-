# -*- coding: utf-8 -*-
"""电脑环境配置方案 —— 可复用章节模块

把「步骤内容」与「机器编排」解耦：
  - steps_wsl(doc)      WSL2 + Ubuntu 基础环境
  - steps_docker(doc)   Docker Desktop 与依赖服务全栈
  - steps_app(doc)      Python 后端 + 前端
  - steps_ai(doc)       AI 训练环境 + ONNX 导出
  - steps_misc(doc)     设备模拟 / 本地 Nginx / 监控
  - acceptance_full(doc)     全栈环境验收清单（25 项）
  - acceptance_simple(doc)   单机开发环境验收清单（15 项，快速上手用）
这样同一批步骤既能生成「一台电脑全栈」版，也能生成「只做某一段」的版本。
"""
from docx_kit import *


def steps_wsl(doc):
    """WSL2 + Ubuntu：所有服务端组件（Docker、后端、AI 推理）的运行底座。"""
    h(doc, "安装 WSL2 与 Ubuntu 24.04", 2)
    para(doc, "WSL2 提供与现场服务器一致的 Linux 环境，同时也是 Docker Desktop 的运行后端。"
              "开发期的服务端命令都在这里执行，可避免 Windows 与 Linux 的路径、权限与编码差异。")
    for no, title, why, ops, expect, verify in [
        ("1", "安装 WSL2 与 Ubuntu 24.04",
         "获得 Linux 开发底座，Docker 与后端服务都跑在它上面。",
         ["以管理员身份打开 PowerShell 7；",
          "执行安装命令（自动启用虚拟机平台与 WSL 组件）；",
          "按提示重启电脑；",
          "重启后首次进入 Ubuntu，设置 Linux 用户名与密码（与 Windows 密码无关，请记录）；",
          "确认默认版本为 WSL2。"],
         ["Ubuntu 发行版状态为 Running，VERSION 为 2。"],
         ["# 安装（管理员 PowerShell）",
          "wsl --install -d Ubuntu-24.04",
          "wsl --set-default-version 2",
          "",
          "# 重启后校验：",
          "wsl -l -v",
          "# 期望：Ubuntu-24.04  STATE=Running  VERSION=2"]),
        ("2", "初始化 Ubuntu 基础环境",
         "安装编译工具与视频处理工具；FFmpeg 是伪视频、算法抽帧与事件短视频生成的基础。",
         ["进入 WSL 终端；", "先按通用基线配置 apt 国内源；", "安装基础工具包。"],
         ["工具安装完成，命令可执行。"],
         ["sudo apt update && sudo apt upgrade -y",
          "sudo apt install -y build-essential curl wget git vim htop net-tools unzip zip \\",
          "  ffmpeg jq tree ncdu lsof ca-certificates gnupg lsb-release",
          "",
          "# 校验：",
          "ffmpeg -version | head -1",
          "git --version; curl --version | head -1"]),
        ("3", "配置 WSL 资源上限与代码存放位置",
         "16GB 内存的机器若不加限制，WSL 会占用过多内存导致 Windows 卡顿；代码必须放在 Linux 文件系统内以保证性能。",
         ["在 Windows 用户目录创建 .wslconfig 限制内存与 CPU；",
          "重启 WSL 使配置生效；",
          "确认代码目录位于 ~/projects，不要放在 /mnt/d。"],
         ["WSL 可用内存接近设定值；代码位于 ~/projects。"],
         ["# 创建 C:\\Users\\<你的用户名>\\.wslconfig，内容：",
          "[wsl2]",
          "memory=8GB          # 16GB 内存机器设 8GB；升级到 32GB 后可改为 16GB",
          "processors=8",
          "swap=4GB",
          "",
          "# 应用（PowerShell）",
          "wsl --shutdown",
          "wsl -d Ubuntu-24.04",
          "",
          "# 校验：WSL 内可用内存应接近设定值",
          "free -h"]),
    ]:
        step(doc, f"4.1.{no}", title, why, ops, expect, verify)


def steps_docker(doc):
    """Docker 与依赖服务：PostgreSQL 16+pgvector、Redis 7、EMQX 5、MinIO、TDengine。"""
    h(doc, "安装 Docker Desktop 与依赖服务全栈", 2)
    para(doc, "按架构方案，竞赛版用 Docker Compose 一条命令起全栈（PostgreSQL 16 + pgvector、Redis 7、EMQX 5、MinIO、TDengine），"
              "使开发环境与现场服务器的组件版本完全一致。这是本方案中“不用装第二台服务器”的关键："
              "数据库、缓存、消息、对象存储全部以容器形式跑在你这台电脑上，一条命令起、一条命令停。")
    for no, title, why, ops, expect, verify in [
        ("1", "配置 Docker Desktop（WSL2 后端 + 加速 + 资源限制）",
         "让容器跑在 WSL2 上，并解决国内拉镜像慢的问题。",
         ["启动 Docker Desktop 并接受协议；",
          "Settings → General：勾选 Use the WSL 2 based engine 与开机自启；",
          "Settings → Resources → WSL Integration：启用 Ubuntu-24.04；",
          "Settings → Resources：内存 8GB、CPU 8 核（16GB 内存机器）；",
          "Settings → Docker Engine：加入阿里云 ACR 专属镜像加速地址；",
          "Apply & Restart。"],
         ["Docker Desktop 显示 Engine running；docker version 有 Client 与 Server 两段输出。"],
         ["docker version",
          "docker compose version",
          "docker info | Select-String 'Server Version','Total Memory','Registry Mirrors'",
          "docker run --rm hello-world",
          "# 期望输出：Hello from Docker!"]),
        ("2", "编写 docker-compose.dev.yml 与 .env",
         "把依赖服务的版本、端口、口令、数据卷固化到文件，保证任何机器起出来的环境完全一致；"
         "该文件与现场部署共用同一骨架，仅编排范围不同。",
         ["在仓库 deploy/ 目录创建 docker-compose.dev.yml（内容见下方代码块）；",
          "复制 .env.example 为 .env 并填写强口令；",
          "确认 .env 已被 .gitignore 忽略。"],
         ["compose 文件与 .env 就绪，且 .env 不会被提交。"],
         ["# 建议的仓库结构",
          "# campus-platform/",
          "#   deploy/docker-compose.dev.yml    开发：只起依赖服务",
          "#   deploy/docker-compose.prod.yml   生产：依赖 + 应用",
          "#   deploy/.env.example              模板（入库）",
          "#   deploy/.env                      实际口令（不入库）",
          "#   backend/  web-admin/  docs/",
          "",
          "# 校验：确认 .env 被忽略",
          "git check-ignore -v deploy/.env"]),
        ("3", "启动依赖服务并逐项校验",
         "确认五个依赖服务全部可用，这是后端、AI 与前端开发的前置条件。",
         ["在 WSL 中进入 deploy 目录；", "后台启动全部服务；", "查看状态；", "逐项验证连通性。"],
         ["五个容器状态为 running 或 healthy。"],
         ["cd ~/projects/campus-platform/deploy",
          "cp .env.example .env && vim .env      # 填入强口令",
          "docker compose -f docker-compose.dev.yml up -d",
          "docker compose -f docker-compose.dev.yml ps",
          "",
          "# 1) PostgreSQL 16 与 pgvector",
          "docker exec campus-pg psql -U campus -d campus -c 'select version();'",
          "docker exec campus-pg psql -U campus -d campus -c 'create extension if not exists vector;'",
          "docker exec campus-pg psql -U campus -d campus -c '\\dx'",
          "# 期望：扩展列表中出现 vector",
          "",
          "# 2) Redis 7",
          "docker exec campus-redis redis-cli -a \"$REDIS_PASSWORD\" ping",
          "# 期望：PONG",
          "",
          "# 3) EMQX 5（浏览器访问 http://localhost:18083，账号 admin）",
          "curl -s http://localhost:18083/status",
          "",
          "# 4) MinIO（浏览器访问 http://localhost:9001）",
          "curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/minio/health/live",
          "# 期望：200",
          "",
          "# 5) TDengine（V2 阶段启用后校验）",
          "curl -s -u root:taosdata -d 'show databases' http://localhost:6041/rest/sql"]),
    ]:
        step(doc, f"4.2.{no}", title, why, ops, expect, verify)
    note(doc, "首次登录 EMQX Dashboard（18083）后立即修改默认口令；MinIO 控制台（9001）创建的桶一律设为私有（private）。")
    add_code(doc, [
        "# deploy/docker-compose.dev.yml —— 开发依赖服务（与总体技术架构方案选型一致）",
        "services:",
        "  postgres:",
        "    image: pgvector/pgvector:pg16          # PostgreSQL 16 + pgvector 向量检索",
        "    container_name: campus-pg",
        "    environment:",
        "      POSTGRES_DB: campus",
        "      POSTGRES_USER: campus",
        "      POSTGRES_PASSWORD: ${PG_PASSWORD}",
        "      TZ: Asia/Shanghai",
        "    ports: ['5432:5432']",
        "    volumes:",
        "      - pgdata:/var/lib/postgresql/data",
        "      - ../backend/scripts/init:/docker-entrypoint-initdb.d:ro",
        "    healthcheck:",
        "      test: ['CMD-SHELL', 'pg_isready -U campus -d campus']",
        "      interval: 10s",
        "      timeout: 5s",
        "      retries: 5",
        "    restart: unless-stopped",
        "",
        "  redis:",
        "    image: redis:7-alpine                  # Redis 7 单实例 + AOF",
        "    container_name: campus-redis",
        "    command: ['redis-server','--appendonly','yes','--requirepass','${REDIS_PASSWORD}']",
        "    ports: ['6379:6379']",
        "    volumes: ['redisdata:/data']",
        "    healthcheck:",
        "      test: ['CMD','redis-cli','-a','${REDIS_PASSWORD}','ping']",
        "      interval: 10s",
        "    restart: unless-stopped",
        "",
        "  emqx:",
        "    image: emqx/emqx:5                     # MQTT 设备接入",
        "    container_name: campus-emqx",
        "    environment:",
        "      EMQX_DASHBOARD__DEFAULT_PASSWORD: ${EMQX_DASHBOARD_PASSWORD}",
        "      TZ: Asia/Shanghai",
        "    ports:",
        "      - '1883:1883'      # MQTT",
        "      - '8083:8083'      # MQTT over WebSocket",
        "      - '18083:18083'    # Dashboard",
        "    volumes: ['emqxdata:/opt/emqx/data']",
        "    restart: unless-stopped",
        "",
        "  minio:",
        "    image: minio/minio                     # 对象存储：事件截图、短视频、附件",
        "    container_name: campus-minio",
        "    command: ['server','/data','--console-address',':9001']",
        "    environment:",
        "      MINIO_ROOT_USER: ${MINIO_USER}",
        "      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}",
        "      TZ: Asia/Shanghai",
        "    ports: ['9000:9000','9001:9001']",
        "    volumes: ['miniodata:/data']",
        "    restart: unless-stopped",
        "",
        "  tdengine:",
        "    image: tdengine/tdengine               # 时序库（V2 阶段启用，可先注释）",
        "    container_name: campus-tdengine",
        "    environment:",
        "      TZ: Asia/Shanghai",
        "    ports: ['6030:6030','6041:6041']",
        "    volumes: ['tddata:/var/lib/taos']",
        "    restart: unless-stopped",
        "",
        "volumes:",
        "  pgdata:",
        "  redisdata:",
        "  emqxdata:",
        "  miniodata:",
        "  tddata:",
    ])


def steps_app(doc):
    """后端与前端：FastAPI + Vue3，单机即可完成前后端联调。"""
    h(doc, "配置后端与前端开发环境（同一台电脑即可联调）", 2)
    para(doc, "后端与前端都跑在这一台电脑上：后端监听 8000，前端监听 5173，前端通过代理访问后端，"
              "因此不需要额外的开发服务器，也不需要跨机器配置。")

    h(doc, "4.3.1 安装 uv 并创建后端虚拟环境", 3)
    para(doc, "目的：uv 是目前最快的 Python 包与虚拟环境管理器；每个项目使用独立虚拟环境，避免依赖互相污染。", size=10)
    para(doc, "操作步骤：", indent=False, bold=True, space_after=2)
    bullet(doc, "安装 uv（见通用基线脚本或官方安装命令）；", size=10)
    bullet(doc, "在 backend 目录创建 Python 3.12 虚拟环境；", size=10)
    bullet(doc, "确认解释器指向虚拟环境。", size=10)
    para(doc, "校验（必须实测通过再进入下一步）：", indent=False, bold=True, space_after=2)
    add_code(doc, ["powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"",
                   "uv --version",
                   "",
                   "cd ~/projects/campus-platform/backend",
                   "uv venv --python 3.12",
                   "source .venv/bin/activate      # Windows 原生：.\\.venv\\Scripts\\Activate.ps1",
                   "python -V && which python      # 应指向 .venv 内"])

    h(doc, "4.3.2 安装后端依赖", 3)
    para(doc, "目的：按架构方案锁定 FastAPI、SQLAlchemy 2.x 异步、asyncpg、Pydantic v2、Redis、MQTT 客户端、APScheduler 等依赖。", size=10)
    para(doc, "校验（必须实测通过再进入下一步）：", indent=False, bold=True, space_after=2)
    add_code(doc, ["uv add fastapi 'uvicorn[standard]' sqlalchemy asyncpg alembic \\",
                   "  pydantic pydantic-settings redis paho-mqtt apscheduler \\",
                   "  'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart \\",
                   "  minio 'prometheus-client' loguru",
                   "uv add --dev pytest httpx pytest-asyncio ruff mypy",
                   "",
                   "uv run python -c \"import fastapi, sqlalchemy, asyncpg, redis, paho.mqtt; print('后端依赖 OK')\""])

    h(doc, "4.3.3 配置 .env 并启动接口", 3)
    para(doc, "目的：让后端连上本机容器里的依赖服务，并验证 FastAPI 自动生成的 OpenAPI 文档可访问。", size=10)
    para(doc, "校验（必须实测通过再进入下一步）：", indent=False, bold=True, space_after=2)
    add_code(doc, ["# backend/.env（示例，口令请自行替换）",
                   "APP_ENV=dev",
                   "DB_URL=postgresql+asyncpg://campus:你的口令@localhost:5432/campus",
                   "REDIS_URL=redis://:你的口令@localhost:6379/0",
                   "MQTT_HOST=localhost",
                   "MQTT_PORT=1883",
                   "MINIO_ENDPOINT=localhost:9000",
                   "JWT_SECRET=请生成32位以上随机串",
                   "",
                   "uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
                   "",
                   "# 校验：",
                   "curl -s http://localhost:8000/health",
                   "# 期望：{\"status\":\"ok\",\"db\":true,\"redis\":true}"])

    h(doc, "4.3.4 初始化数据库结构（Alembic 迁移）", 3)
    para(doc, "目的：所有表结构变更通过迁移脚本管理，保证开发机与后续云端、现场服务器的库结构一致、可回溯。", size=10)
    para(doc, "校验（必须实测通过再进入下一步）：", indent=False, bold=True, space_after=2)
    add_code(doc, ["uv run alembic revision --autogenerate -m \"init schema\"",
                   "uv run alembic upgrade head",
                   "",
                   "# 校验：",
                   "docker exec campus-pg psql -U campus -d campus -c '\\dt'",
                   "docker exec campus-pg psql -U campus -d campus -c 'select version_num from alembic_version;'"])

    h(doc, "4.3.5 启用 pnpm 并创建前端工程", 3)
    para(doc, "目的：按架构方案，前端使用 Vue3 + Vite + Element Plus + ECharts；pnpm 比 npm 更快且更省磁盘。", size=10)
    para(doc, "校验（必须实测通过再进入下一步）：", indent=False, bold=True, space_after=2)
    add_code(doc, ["corepack enable",
                   "corepack prepare pnpm@latest --activate",
                   "pnpm --version",
                   "",
                   "cd ~/projects/campus-platform",
                   "pnpm create vite web-admin --template vue-ts",
                   "cd web-admin && pnpm install",
                   "pnpm add element-plus echarts pinia vue-router axios dayjs",
                   "pnpm dev",
                   "# 浏览器访问 http://localhost:5173 应看到初始页面"])

    h(doc, "4.3.6 配置开发代理并联调后端", 3)
    para(doc, "目的：前端（5173）通过代理访问后端（8000），避免跨域，并与生产 Nginx 的路径结构保持一致。", size=10)
    para(doc, "校验（必须实测通过再进入下一步）：", indent=False, bold=True, space_after=2)
    add_code(doc, ["# vite.config.ts 片段",
                   "export default defineConfig({",
                   "  server: {",
                   "    host: '0.0.0.0',",
                   "    port: 5173,",
                   "    proxy: { '/api': { target: 'http://localhost:8000', changeOrigin: true } }",
                   "  }",
                   "})",
                   "",
                   "# 校验：",
                   "curl -s http://localhost:5173/api/health",
                   "# 期望：返回与直连 8000 端口一致的 JSON"])


def steps_ai(doc):
    """AI 训练与 ONNX 导出：只在这一台带 NVIDIA 显卡的电脑上做。"""
    h(doc, "配置 AI 训练环境与 ONNX 导出", 2)
    para(doc, "本节只在这一台带 NVIDIA 显卡的电脑上执行。架构方案给出的训练环境最低要求为 RTX 3060 12GB，"
              "本项目现有 RTX 3050 8GB 属于可用下限：训练 YOLOv8n/s 时需把 batch 调小、开启 FP16 混合精度、"
              "必要时降低 imgsz；数据集规模较大时可临时使用实验室或云端算力训练，训练产物（权重与 ONNX）仍回到本机使用。")
    add_table(doc, ["项目", "架构方案要求（最低）", "本项目实际（RTX 3050 8GB）", "调整策略"],
              [["GPU", "1×RTX 3060 12GB", "RTX 3050 8GB（算力 8.6）", "可用，按下方参数下调 batch 与 imgsz"],
               ["内存", "32GB", "16GB（建议升级）", "训练时关闭浏览器与容器中的占用进程"],
               ["存储", "1TB NVMe", "1TB NVMe（建议加装数据盘）", "数据集与权重放 D 盘数据目录"],
               ["框架", "PyTorch 2.x + CUDA 12 + Ultralytics", "同左", "严格按此版本安装"],
               ["单次训练（1.5 万张 / 200 轮）", "8—12 小时", "约 12—20 小时（小 batch + FP16）", "先小数据集跑通，再放大"]],
              [3.0, 4.0, 4.6, 4.0], size=9)
    for no, title, why, ops, expect, verify in [
        ("1", "安装 NVIDIA 驱动并确认显卡可用",
         "PyTorch 的 CUDA 能力由驱动决定，必须先装官方驱动再装框架。",
         ["到 NVIDIA 官网下载与 RTX 3050 匹配的 Game Ready 或 Studio 驱动；",
          "安装时选择自定义安装并勾选清洁安装；",
          "重启后用 nvidia-smi 确认。"],
         ["nvidia-smi 输出显卡型号、驱动版本与显存总量。"],
         ["nvidia-smi",
          "nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv",
          "# 期望：NVIDIA GeForce RTX 3050，显存约 8192 MiB"]),
        ("2", "创建独立训练环境并安装 PyTorch（CUDA 12 版）",
         "AI 训练依赖体积大、版本敏感，必须与后端业务环境隔离。",
         ["创建专用虚拟环境（Python 3.11）；",
          "到 pytorch.org 按 Windows + CUDA 12.x 生成官方安装命令并执行（切勿用默认 pip 源，否则会装成 CPU 版）；",
          "验证 CUDA 可用。"],
         ["torch.cuda.is_available() 为 True 并输出显卡型号与 CUDA 版本。"],
         ["uv venv --python 3.11 ~/.venvs/cv-train",
          "source ~/.venvs/cv-train/bin/activate",
          "uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124",
          "",
          "python -c \"import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.version.cuda)\""]),
        ("3", "安装训练与工具链依赖",
         "安装 Ultralytics、OpenCV、ONNX 导出与推理、标注工具，构成完整 AI 工具链。",
         ["安装训练框架与图像处理库；", "安装 ONNX 相关工具；", "安装标注工具。"],
         ["各库可导入；yolo 命令可用。"],
         ["uv pip install ultralytics opencv-python numpy pillow onnx onnxruntime onnxsim labelImg",
          "python -c \"import ultralytics, cv2, onnx, onnxruntime; print('AI 工具链 OK', ultralytics.__version__)\"",
          "yolo version"]),
        ("4", "准备数据集并跑通一次最小训练",
         "先用小数据集跑通“数据 → 训练 → 评估 → 权重”全链路，确认环境无问题再投入真实标注。",
         ["按架构方案数据集流程准备数据（采集→清洗→标注→复核→按 7:1.5:1.5 划分）；",
          "编写 data.yaml；",
          "用官方预训练权重做迁移学习，先跑 10 轮验证链路；",
          "观察显存占用并调整 batch 与 imgsz。"],
         ["训练正常收敛并生成 best.pt。"],
         ["# data.yaml 示例",
          "path: /mnt/d/campus/data/dataset/fire",
          "train: images/train",
          "val: images/val",
          "test: images/test",
          "names:",
          "  0: smoke",
          "  1: fire",
          "",
          "# 最小训练（RTX 3050 8GB：batch 8 + amp；显存不足改为 batch 4）",
          "yolo detect train model=yolo11n.pt data=/mnt/d/campus/data/dataset/fire/data.yaml \\",
          "  epochs=10 imgsz=640 batch=8 device=0 amp=True workers=4 project=runs name=smoke-test",
          "",
          "ls -lh runs/detect/smoke-test/weights/"]),
        ("5", "导出 ONNX 并验证推理一致性",
         "按架构方案，训练用 PyTorch、交付用 ONNX，由 ONNX Runtime 统一承载，实现一次训练多端推理。",
         ["用 Ultralytics 导出 ONNX（opset 17、动态 batch、简化计算图）；",
          "用同一张图分别走 PyTorch 与 ONNX Runtime 并比较偏差。"],
         ["生成 best.onnx；两者偏差 ≤1e-3。"],
         ["yolo export model=runs/detect/smoke-test/weights/best.pt \\",
          "  format=onnx opset=17 dynamic=True simplify=True",
          "",
          "# 校验：",
          "ls -lh runs/detect/smoke-test/weights/best.onnx",
          "python - <<'PY'",
          "import numpy as np, onnxruntime as ort, cv2",
          "from ultralytics import YOLO",
          "img = cv2.imread('test.jpg')",
          "m = YOLO('runs/detect/smoke-test/weights/best.pt')",
          "print(m.predict(img, imgsz=640, verbose=False)[0].boxes.data.cpu().numpy()[:3])",
          "sess = ort.InferenceSession('runs/detect/smoke-test/weights/best.onnx')",
          "x = cv2.resize(img, (640, 640)).transpose(2, 0, 1)[None].astype(np.float32) / 255.0",
          "print(sess.run(None, {sess.get_inputs()[0].name: x})[0].shape)",
          "print('判定：形状与数值分布一致，坐标偏差应 <=1e-3')",
          "PY"]),
    ]:
        step(doc, f"4.4.{no}", title, why, ops, expect, verify)
    note(doc, "显存不足（CUDA out of memory）的处理顺序：① batch 8 → 4 → 2；② imgsz 640 → 512 → 416；"
              "③ 关闭浏览器与容器中的 AI 服务；④ 减小数据集分辨率，而不是盲目减少轮次。")


def steps_misc(doc):
    """设备模拟、本地网关与监控：单机也能跑通“数据采集 → 分析 → 告警”全链路。"""
    h(doc, "配置设备模拟环境、本地网关与监控（可选但推荐）", 2)
    para(doc, "项目早期没有真实门禁、摄像机和传感器。以下三个配置让你在一台电脑上就能完整验证业务链路，"
              "也是给协作者演示时最有用的部分。")
    for no, title, why, ops, expect, verify in [
        ("1", "搭建伪视频流（RTSP）",
         "用最接近现场协议的方式模拟摄像机，保证视频接入与 AI 分析代码在设备到货前就能开发。",
         ["用 Docker 启动 MediaMTX 流媒体服务器；",
          "用 FFmpeg 把一段视频循环推成 RTSP 流；",
          "用 ffprobe 或 VLC 验证拉流。"],
         ["可拉取 rtsp://localhost:8554/cam1 并看到画面。"],
         ["docker run --rm -d --name mediamtx -p 8554:8554 -p 8888:8888 bluenviron/mediamtx:latest",
          "ffmpeg -re -stream_loop -1 -i /mnt/d/campus/data/sample/campus.mp4 \\",
          "  -c copy -f rtsp rtsp://localhost:8554/cam1",
          "",
          "# 校验：",
          "ffprobe -rtsp_transport tcp -i rtsp://localhost:8554/cam1 -show_streams | head -30",
          "",
          "# 多路模拟（模拟多路摄像机并发分析）",
          "for i in 2 3 4; do ffmpeg -re -stream_loop -1 -i /mnt/d/campus/data/sample/campus.mp4 \\",
          "  -c copy -f rtsp rtsp://localhost:8554/cam$i & done"]),
        ("2", "搭建 MQTT 设备模拟器与桩服务",
         "门禁、传感器、车牌识别在到货前无法联调；用脚本按真实报文格式上报即可完成大部分开发。",
         ["编写 MQTT 模拟脚本，周期上报传感器数据与门禁通行记录；",
          "编写设备桩服务（FastAPI）模拟设备上报接口；",
          "用 MQTTX 或订阅端确认平台能收到。"],
         ["平台/MQTTX 能持续收到模拟消息；桩服务接口可调用。"],
         ["python - <<'PY'",
          "import json, random, time, paho.mqtt.client as mqtt",
          "c = mqtt.Client('sim-gateway-01'); c.connect('localhost', 1883, 60); c.loop_start()",
          "while True:",
          "    c.publish('iot/env/B01/F03/telemetry', json.dumps({'t': round(random.uniform(18,26),1),",
          "        'co2': random.randint(500,1200), 'ts': int(time.time())}))",
          "    c.publish('iot/access/gate-01/event', json.dumps({'person_id': 'S2026001', 'direction': 'in',",
          "        'credential': 'face', 'confidence': 0.98, 'ts': int(time.time())}))",
          "    time.sleep(5)",
          "PY",
          "",
          "# 设备桩服务（stub_device.py，用 FastAPI 暴露上报接口）",
          "# uv run uvicorn stub_device:app --port 9100",
          "# 校验：curl -X POST http://localhost:9100/api/device/access/report"]),
        ("3", "本地 Nginx 与监控（可选）",
         "提前用与生产一致的反代结构暴露路径与缓存问题；监控可在联调阶段发现性能退化。",
         ["用 Docker 运行 Nginx，挂载前端构建产物与站点配置；",
          "后端暴露 /metrics，启动 Prometheus 与 Grafana。"],
         ["通过 http://localhost:8080 可访问平台；Grafana 能显示后端指标。"],
         ["cd ~/projects/campus-platform/web-admin && pnpm build",
          "docker run --rm -d --name campus-nginx -p 8080:80 \\",
          "  -v ~/projects/campus-platform/deploy/nginx/dev.conf:/etc/nginx/conf.d/default.conf:ro \\",
          "  -v ~/projects/campus-platform/web-admin/dist:/usr/share/nginx/html:ro nginx:alpine",
          "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/",
          "curl -s http://localhost:8080/api/health",
          "",
          "# 监控（可选）",
          "docker run -d --name campus-prom -p 9090:9090 prom/prometheus",
          "docker run -d --name campus-grafana -p 3000:3000 grafana/grafana"]),
    ]:
        step(doc, f"4.5.{no}", title, why, ops, expect, verify)


FULL_ACCEPT = [
    ("D-01", "WSL2 正常", "wsl -l -v", "Ubuntu-24.04 Running，VERSION=2"),
    ("D-02", "WSL 资源限制生效", "wsl -d Ubuntu-24.04 -- free -h", "内存接近 .wslconfig 设定值"),
    ("D-03", "apt 源为国内", "grep -r aliyun /etc/apt/sources.list.d/", "有 aliyun 记录"),
    ("D-04", "Docker 可用", "docker run --rm hello-world", "输出 Hello from Docker!"),
    ("D-05", "Docker 加速生效", "docker info | Select-String 'Registry Mirrors'", "显示专属加速地址"),
    ("D-06", "PG16 + pgvector", "docker exec campus-pg psql -U campus -d campus -c '\\dx'", "扩展列表含 vector"),
    ("D-07", "Redis 7 连通", "docker exec campus-redis redis-cli -a <口令> ping", "PONG"),
    ("D-08", "EMQX 连通", "curl -s http://localhost:18083/status", "返回状态信息"),
    ("D-09", "MinIO 存活", "curl -s http://localhost:9000/minio/health/live", "HTTP 200"),
    ("D-10", "后端依赖齐全", "uv run python -c \"import fastapi, sqlalchemy, asyncpg\"", "无报错"),
    ("D-11", "后端服务可启", "curl -s http://localhost:8000/health", "status=ok"),
    ("D-12", "Swagger 可访问", "浏览器打开 /docs", "接口文档正常"),
    ("D-13", "数据库迁移成功", "uv run alembic current", "显示最新版本号"),
    ("D-14", "NVIDIA 驱动正常", "nvidia-smi", "显示 RTX 3050 与驱动版本"),
    ("D-15", "PyTorch CUDA 可用", "python -c \"import torch;print(torch.cuda.is_available())\"", "True"),
    ("D-16", "Ultralytics 可用", "yolo version", "输出版本号"),
    ("D-17", "最小训练跑通", "ls runs/detect/*/weights/best.pt", "权重文件存在"),
    ("D-18", "ONNX 导出成功", "ls runs/detect/*/weights/best.onnx", "文件存在"),
    ("D-19", "推理一致性达标", "对比脚本输出", "与 PyTorch 偏差 ≤1e-3"),
    ("D-20", "前端可启动", "浏览器访问 http://localhost:5173", "页面正常"),
    ("D-21", "前后端联调通", "curl -s http://localhost:5173/api/health", "返回后端 JSON"),
    ("D-22", "伪视频可拉流", "ffprobe rtsp://localhost:8554/cam1", "输出视频流信息"),
    ("D-23", "MQTT 模拟可上报", "MQTTX 订阅 iot/#", "持续收到模拟消息"),
    ("D-24", "桩服务可访问", "curl -X POST http://localhost:9100/api/device/access/report", "返回模拟数据"),
    ("D-25", "环境自检通过", "python 环境工具\\scripts\\check-env.py --role dev", "通过率 100%"),
]

SIMPLE_ACCEPT = [
    ("Q-01", "基础软件齐全", "git --version; python --version; node -v", "均有版本输出"),
    ("Q-02", "镜像源已配置", "pip config list; npm config get registry", "清华源 + npmmirror"),
    ("Q-03", "虚拟化已开启", "(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled", "True"),
    ("Q-04", "WSL2 + Ubuntu 可用", "wsl -l -v", "Ubuntu-24.04 Running / VERSION 2"),
    ("Q-05", "Docker 可用", "docker run --rm hello-world", "输出 Hello from Docker!"),
    ("Q-06", "依赖服务全起", "docker compose -f docker-compose.dev.yml ps", "PG/Redis/EMQX/MinIO 均 healthy"),
    ("Q-07", "数据库可连", "docker exec campus-pg psql -U campus -d campus -c '\\dx'", "扩展含 vector"),
    ("Q-08", "后端可启", "curl -s http://localhost:8000/health", "status=ok"),
    ("Q-09", "接口文档可访问", "浏览器打开 http://localhost:8000/docs", "Swagger 正常"),
    ("Q-10", "前端可启", "浏览器访问 http://localhost:5173", "页面正常"),
    ("Q-11", "前后端联调通", "curl -s http://localhost:5173/api/health", "返回后端 JSON"),
    ("Q-12", "数据库迁移成功", "uv run alembic current", "显示版本号"),
    ("Q-13", "Git 仓库就绪", "git remote -v", "能看到远端地址"),
    ("Q-14", "环境自检通过", "python 环境工具\\scripts\\check-env.py --role dev", "核心项全部通过"),
    ("Q-15", "能完成一次提交", "git add . && git commit && git push", "远端可见提交记录"),
]


def acceptance_full(doc):
    h(doc, "全栈环境验收清单（25 项，全部通过方可进入功能开发）", 2)
    add_table(doc, ["编号", "验收项", "校验命令", "通过标准"],
              [list(x) for x in FULL_ACCEPT],
              [1.2, 3.2, 6.8, 3.4], size=8.5, align_center_cols=(0,))


def acceptance_simple(doc):
    h(doc, "单机开发环境验收清单（15 项，半天内应全部通过）", 2)
    add_table(doc, ["编号", "验收项", "校验命令", "通过标准"],
              [list(x) for x in SIMPLE_ACCEPT],
              [1.2, 3.4, 6.6, 3.4], size=8.5, align_center_cols=(0,))


def step(doc, no, title, why, ops, expect, verify):
    """标准操作步骤：目的 → 操作步骤 → 预期结果 → 校验。"""
    h(doc, f"{no} {title}", 3)
    para(doc, f"目的：{why}", size=10)
    para(doc, "操作步骤：", indent=False, bold=True, space_after=2)
    for op in ops:
        if isinstance(op, tuple) and op[0] == "code":
            add_code(doc, op[1])
        elif isinstance(op, tuple) and op[0] == "note":
            note(doc, op[1])
        else:
            bullet(doc, op, size=10)
    if expect:
        para(doc, "预期结果：", indent=False, bold=True, space_after=2)
        for e in expect:
            bullet(doc, e, size=10)
    if verify:
        para(doc, "校验（必须实测通过再进入下一步）：", indent=False, bold=True, space_after=2)
        add_code(doc, verify)
