# -*- coding: utf-8 -*-
"""《电脑环境配置详细方案》— 台式机全栈配置与「外援环境」（协作者客户端 / 服务器）章节"""
from docx_kit import *
from envcfg_part1 import step, chapter1, chapter2, new_doc
from envcfg_shared import (
    steps_wsl as _steps_wsl,
    steps_docker as _steps_docker,
    steps_app as _steps_app,
    steps_ai as _steps_ai,
    steps_misc as _steps_misc,
    acceptance_full as _acceptance_full,
    acceptance_simple as _acceptance_simple,
)


def chapter3_old(doc):
    h(doc, "第 3 章 台式机（主力开发机）详细配置", 1, page_break=True)
    para(doc, "本章是环境构建的核心。台式机 i5-13400F + RTX 3050 8GB 承担 AI 训练与全栈开发，配置完成后即可独立完成"
              "“模型训练 → 导出 ONNX → 平台联调 → 演示”全流程。请严格按 3.1 → 3.10 顺序执行。")
    add_table(doc, ["章节", "配置内容", "预计耗时", "完成标志"],
              [["3.1", "WSL2 + Ubuntu 24.04（Linux 开发底座）", "30—60 分钟", "wsl -l -v 显示 Running 且 VERSION 为 2"],
               ["3.2", "Docker Desktop 与依赖服务全栈", "60—90 分钟", "5 个服务 healthy，PG / Redis / EMQX / MinIO 可连"],
               ["3.3", "Python 后端开发环境", "40 分钟", "Swagger 页面可打开"],
               ["3.4", "AI 训练环境（CUDA / PyTorch / YOLO）", "90—150 分钟", "torch.cuda.is_available() 为 True，训练出权重"],
               ["3.5", "ONNX 导出与推理验证", "40 分钟", "与 PyTorch 结果偏差 ≤1e-3"],
               ["3.6", "前端开发环境", "40 分钟", "页面能调用后端接口"],
               ["3.7", "设备与外设模拟环境", "60 分钟", "伪视频可拉流、模拟设备可上报"],
               ["3.8", "Nginx 本地网关（可选）", "20 分钟", "通过 8080 访问平台"],
               ["3.9", "监控与日志（可选）", "40 分钟", "Prometheus 抓到后端指标"],
               ["3.10", "台式机验收清单（25 项）", "60 分钟", "全部通过"]],
              [1.4, 6.0, 2.4, 6.4], size=9, align_center_cols=(0, 2))

    h(doc, "3.1 安装 WSL2 与 Ubuntu 24.04", 2)
    step(doc, "3.1.1", "安装 WSL2 与 Ubuntu 24.04",
         "WSL2 提供与现场服务器一致的 Linux 环境，同时也是 Docker Desktop 的运行后端。"
         "开发期的服务端命令都在这里执行，可避免 Windows 与 Linux 的路径、权限与编码差异。",
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
          "wsl --status",
          "# 期望：Ubuntu-24.04  STATE=Running  VERSION=2"])

    step(doc, "3.1.2", "初始化 Ubuntu 基础环境",
         "安装编译工具与视频处理工具。FFmpeg 是后续伪视频、算法抽帧与事件短视频生成的基础。",
         ["进入 WSL 终端；", "先按 2.4.4 配置 apt 国内源；", "安装基础工具包。"],
         ["工具安装完成，命令可执行。"],
         ["sudo apt update && sudo apt upgrade -y",
          "sudo apt install -y build-essential curl wget git vim htop net-tools unzip zip \\",
          "  ffmpeg jq tree ncdu lsof ca-certificates gnupg lsb-release",
          "",
          "# 校验：",
          "ffmpeg -version | head -1",
          "git --version; curl --version | head -1"])

    step(doc, "3.1.3", "配置 WSL 资源上限与文件互通",
         "16GB 内存的机器若不加限制，WSL 会占用过多内存导致 Windows 卡顿；同时必须明确代码存放位置以保证性能。",
         ["在 Windows 用户目录创建 .wslconfig 限制内存与 CPU；",
          "重启 WSL 使配置生效；",
          "确认代码目录位于 Linux 文件系统内（~/projects），不要放在 /mnt/d。"],
         ["WSL 可用内存接近设定值；代码目录位于 ~/projects。"],
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
          "free -h"])

    h(doc, "3.2 安装 Docker Desktop 与依赖服务全栈", 2)
    step(doc, "3.2.1", "配置 Docker Desktop（WSL2 后端 + 加速 + 资源限制）",
         "按架构方案，竞赛版用 Docker Compose 一条命令起全栈（PostgreSQL 16 + pgvector、Redis 7、EMQX 5、MinIO、TDengine），"
         "使开发环境与现场服务器的组件版本完全一致。",
         ["启动 Docker Desktop 并接受协议；",
          "Settings → General：勾选 Use the WSL 2 based engine 与开机自启；",
          "Settings → Resources → WSL Integration：启用 Ubuntu-24.04；",
          "Settings → Resources：内存 8GB、CPU 8 核（16GB 机器）；",
          "Settings → Docker Engine：加入 registry-mirrors（见 2.4.3）；",
          "Apply & Restart。"],
         ["Docker Desktop 显示 Engine running；docker version 有 Client 与 Server 两段输出。"],
         ["docker version",
          "docker compose version",
          "docker info | Select-String 'Server Version','Total Memory','Registry Mirrors'",
          "docker run --rm hello-world",
          "# 期望输出：Hello from Docker!"])

    step(doc, "3.2.2", "编写开发用 docker-compose.dev.yml",
         "把依赖服务的版本、端口、口令、数据卷固化到文件，保证任何机器起出来的环境完全一致；"
         "该文件与现场部署共用同一骨架，仅编排范围与 .env 不同。",
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
          "git check-ignore -v deploy/.env"])
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

    step(doc, "3.2.3", "启动依赖服务并逐项校验",
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
          "# 5) TDengine（启用后校验）",
          "curl -s -u root:taosdata -d 'show databases' http://localhost:6041/rest/sql"])
    note(doc, "首次登录 EMQX Dashboard（18083）后立即修改默认口令；MinIO 控制台（9001）创建的桶一律设为私有（private）。")

    h(doc, "3.3 配置 Python 后端开发环境", 2)
    step(doc, "3.3.1", "安装 uv 并创建后端虚拟环境",
         "uv 是目前最快的 Python 包与虚拟环境管理器，可替代 pip 使用，显著缩短依赖安装时间；"
         "每个项目使用独立虚拟环境，避免不同项目依赖互相污染。",
         ["安装 uv（见 2.2.2 脚本或官方安装命令）；",
          "在 backend 目录创建 Python 3.12 虚拟环境；",
          "确认解释器指向虚拟环境。"],
         ["uv --version 输出版本；虚拟环境目录 .venv 已创建。"],
         ["# 安装 uv（PowerShell）",
          "powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"",
          "uv --version",
          "",
          "# 在 WSL 中创建后端环境",
          "cd ~/projects/campus-platform/backend",
          "uv venv --python 3.12",
          "source .venv/bin/activate      # Windows 原生：.\\.venv\\Scripts\\Activate.ps1",
          "",
          "# 校验：",
          "python -V && which python      # 应指向 .venv 内"])

    step(doc, "3.3.2", "安装后端依赖（按架构方案选型）",
         "按架构方案锁定 FastAPI、SQLAlchemy 2.x 异步、asyncpg、Pydantic v2、Redis、MQTT 客户端、APScheduler 等依赖。",
         ["添加运行时依赖与开发依赖；", "确认生成 lock 文件；", "导入关键库验证。"],
         ["pyproject.toml 与 uv.lock 生成；关键库可导入。"],
         ["uv add fastapi 'uvicorn[standard]' sqlalchemy asyncpg alembic \\",
          "  pydantic pydantic-settings redis paho-mqtt apscheduler \\",
          "  'python-jose[cryptography]' 'passlib[bcrypt]' python-multipart \\",
          "  minio 'prometheus-client' loguru",
          "uv add --dev pytest httpx pytest-asyncio ruff mypy",
          "",
          "# 校验：",
          "uv run python -c \"import fastapi, sqlalchemy, asyncpg, redis, paho.mqtt; print('后端依赖 OK')\""])

    step(doc, "3.3.3", "配置后端 .env 并启动首个接口",
         "让后端连上 3.2 起的依赖服务，并验证 FastAPI 自动生成的 OpenAPI 文档可访问。",
         ["复制 .env.example 为 .env，填写数据库、Redis、MQTT、MinIO 连接信息；",
          "启动开发服务器；",
          "浏览器访问 /docs 与 /health。"],
         ["Swagger 页面可打开；/health 返回 200 与依赖服务状态。"],
         ["# backend/.env（示例，口令请自行替换）",
          "APP_ENV=dev",
          "DB_URL=postgresql+asyncpg://campus:你的口令@localhost:5432/campus",
          "REDIS_URL=redis://:你的口令@localhost:6379/0",
          "MQTT_HOST=localhost",
          "MQTT_PORT=1883",
          "MINIO_ENDPOINT=localhost:9000",
          "JWT_SECRET=请生成32位以上随机串",
          "",
          "# 启动",
          "uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
          "",
          "# 校验：",
          "curl -s http://localhost:8000/health",
          "# 期望：{\"status\":\"ok\",\"db\":true,\"redis\":true}"])

    step(doc, "3.3.4", "初始化数据库结构（Alembic 迁移）",
         "所有表结构变更通过迁移脚本管理，保证开发机、云端与现场服务器的库结构一致、可回溯。",
         ["初始化 Alembic（若仓库已有则跳过）；", "生成并执行首次迁移；", "用 DBeaver 或 psql 确认表已创建。"],
         ["数据库中可见业务表；alembic_version 表存在。"],
         ["uv run alembic revision --autogenerate -m \"init schema\"",
          "uv run alembic upgrade head",
          "",
          "# 校验：",
          "docker exec campus-pg psql -U campus -d campus -c '\\dt'",
          "docker exec campus-pg psql -U campus -d campus -c 'select version_num from alembic_version;'"])

    h(doc, "3.4 配置 AI 训练环境（CUDA / PyTorch / YOLO）", 2)
    para(doc, "本节只在这一台带 NVIDIA 显卡的机器上执行。架构方案给出的训练环境最低要求为 RTX 3060 12GB，"
              "本项目现有 RTX 3050 8GB 属于可用的下限配置：训练 YOLOv8n/s 时需把 batch 调小（8 或 4）、"
              "开启 FP16 混合精度、必要时降低 imgsz；数据集规模较大时可临时使用实验室或云端算力。")
    add_table(doc, ["项目", "架构方案要求（最低）", "本项目实际（RTX 3050 8GB）", "调整策略"],
              [["GPU", "1×RTX 3060 12GB", "RTX 3050 8GB（算力 8.6）", "可用，按下方参数下调 batch 与 imgsz"],
               ["内存", "32GB", "16GB（建议升级）", "训练时关闭浏览器与 Docker，或先升内存"],
               ["存储", "1TB NVMe", "1TB NVMe（按第 0 章建议加装）", "数据集与权重放 D 盘数据目录"],
               ["框架", "PyTorch 2.x + CUDA 12 + Ultralytics", "同左", "严格按此版本安装"],
               ["单次训练（1.5 万张 / 200 轮）", "8—12 小时", "约 12—20 小时（小 batch、FP16）", "先小数据集跑通，再放大"]],
              [3.0, 4.0, 4.6, 4.0], size=9)

    step(doc, "3.4.1", "安装 NVIDIA 驱动并确认显卡可用",
         "PyTorch 的 CUDA 能力由驱动决定，必须先装官方驱动再装框架；驱动版本决定可用的 CUDA 上限。",
         ["到 NVIDIA 官网下载与 RTX 3050 匹配的 Game Ready 或 Studio 驱动（Windows 版）；",
          "安装时选择“自定义安装”并勾选执行清洁安装；",
          "安装完成后重启；",
          "用 nvidia-smi 确认驱动与显存。"],
         ["nvidia-smi 能输出显卡型号、驱动版本、显存总量。"],
         ["nvidia-smi",
          "nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv",
          "# 期望：NVIDIA GeForce RTX 3050，显存约 8192 MiB"])

    step(doc, "3.4.2", "创建独立训练虚拟环境并安装 PyTorch（CUDA 12 版）",
         "AI 训练依赖体积大、版本敏感，必须与后端业务环境隔离，避免相互破坏。",
         ["创建专用虚拟环境（Python 3.11，兼容性最好）；",
          "访问 pytorch.org，按“Windows + CUDA 12.x”生成官方安装命令并执行（切勿使用默认 pip 源安装，否则会装成 CPU 版）；",
          "验证 CUDA 可用。"],
         ["torch.cuda.is_available() 为 True，且输出显卡型号与 CUDA 版本。"],
         ["# 创建环境（建议放在用户目录，避免与后端 .venv 混淆）",
          "uv venv --python 3.11 ~/.venvs/cv-train",
          "source ~/.venvs/cv-train/bin/activate",
          "",
          "# 安装 PyTorch（务必用 pytorch.org 生成的 cu12x 命令，示例如下）",
          "uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124",
          "",
          "# 校验：",
          "python -c \"import torch;print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0), torch.version.cuda)\"",
          "# 期望：2.x.x True NVIDIA GeForce RTX 3050 12.x"])

    step(doc, "3.4.3", "安装训练与工具链依赖",
         "安装 Ultralytics（YOLO 全流程）、OpenCV、ONNX 导出与推理、标注工具，构成本项目 AI 开发的完整工具链。",
         ["安装训练框架与图像处理库；", "安装 ONNX 相关工具；", "安装标注工具（也可用 Label Studio / CVAT 替代）。"],
         ["各库可导入；yolo 命令可用。"],
         ["uv pip install ultralytics opencv-python numpy pillow onnx onnxruntime onnxsim labelImg",
          "",
          "# 校验：",
          "python -c \"import ultralytics, cv2, onnx, onnxruntime; print('AI 工具链 OK', ultralytics.__version__)\"",
          "yolo version"])

    step(doc, "3.4.4", "准备数据集并跑通一次最小训练",
         "先用公开小数据集跑通“数据 → 训练 → 评估 → 权重”全链路，确认环境无问题，再投入真实数据标注。",
         ["按架构方案的数据集流程（8.2 节）准备数据：采集 → 清洗 → 标注 → 复核 → 划分 7:1.5:1.5；",
          "编写 data.yaml（指定训练/验证/测试路径与类别名）；",
          "用官方预训练权重做迁移学习，先跑 10 轮验证链路；",
          "观察显存占用，按结果调整 batch 与 imgsz。"],
         ["训练正常收敛，生成 runs/detect/train/weights/best.pt。"],
         ["# data.yaml 示例",
          "path: /mnt/d/campus/data/dataset/fire",
          "train: images/train",
          "val: images/val",
          "test: images/test",
          "names:",
          "  0: smoke",
          "  1: fire",
          "",
          "# 最小训练（RTX 3050 8GB：batch 8 + amp，若显存不足改为 batch 4）",
          "yolo detect train model=yolo11n.pt data=/mnt/d/campus/data/dataset/fire/data.yaml \\",
          "  epochs=10 imgsz=640 batch=8 device=0 amp=True workers=4 project=runs name=smoke-test",
          "",
          "# 校验：",
          "ls -lh runs/detect/smoke-test/weights/",
          "python -c \"from ultralytics import YOLO; m=YOLO('runs/detect/smoke-test/weights/best.pt'); print(m.val(data='/mnt/d/campus/data/dataset/fire/data.yaml')[:1])\""])
    note(doc, "显存不足（CUDA out of memory）时的处理顺序：① batch 8 → 4；② imgsz 640 → 512 → 416；"
              "③ 关闭 AMP 之外的占用（浏览器、Docker 中的 AI 服务）；④ 减小数据集分辨率而非盲目减少轮次。")

    h(doc, "3.5 导出 ONNX 并验证推理一致性", 2)
    step(doc, "3.5.1", "导出 ONNX 模型",
         "按架构方案，训练用 PyTorch 保研发效率，交付用 ONNX 由 ONNX Runtime 统一承载，"
         "实现“一次训练、多端推理”，并使边缘盒子与开发机行为一致。",
         ["用 Ultralytics 导出 ONNX（opset 17、动态 batch、简化计算图）；",
          "记录导出后的输入输出规格。"],
         ["生成 best.onnx 文件；输入为 [batch,3,640,640]。"],
         ["yolo export model=runs/detect/smoke-test/weights/best.pt \\",
          "  format=onnx opset=17 dynamic=True simplify=True",
          "",
          "# 校验：确认文件与输入输出规格",
          "ls -lh runs/detect/smoke-test/weights/best.onnx",
          "python -c \"import onnx;m=onnx.load('runs/detect/smoke-test/weights/best.onnx');print(onnx.helper.printable_graph(m.graph)[:500])\""])

    step(doc, "3.5.2", "验证 ONNX 与 PyTorch 推理结果一致",
         "架构方案的验收标准是两者偏差 ≤1e-3；若不一致，通常是预处理、归一化或输入尺寸不同导致的。",
         ["用同一张图片分别走 PyTorch 与 ONNX Runtime；",
          "比较输出张量的最大绝对偏差；",
          "记录结果作为验收证据。"],
         ["最大绝对偏差 ≤1e-3。"],
         ["python - <<'PY'",
          "import numpy as np, onnxruntime as ort, torch, cv2",
          "from ultralytics import YOLO",
          "img = cv2.imread('test.jpg')",
          "m = YOLO('runs/detect/smoke-test/weights/best.pt')",
          "pt = m.predict(img, imgsz=640, verbose=False)[0].boxes.data.cpu().numpy()[:5]",
          "sess = ort.InferenceSession('runs/detect/smoke-test/weights/best.onnx')",
          "x = cv2.resize(img, (640, 640)).transpose(2, 0, 1)[None].astype(np.float32) / 255.0",
          "on = sess.run(None, {sess.get_inputs()[0].name: x})[0]",
          "print('PyTorch 前5行:', pt)",
          "print('ONNX 输出形状:', on.shape)",
          "print('判定：形状与数值分布应一致；检测框坐标偏差应 <=1e-3')",
          "PY"])

    h(doc, "3.6 配置前端开发环境", 2)
    step(doc, "3.6.1", "启用 pnpm 并创建前端工程",
         "按架构方案，前端使用 Vue3 + Vite + Element Plus + ECharts，pnpm 比 npm 更快且更省磁盘。",
         ["启用 corepack 并激活 pnpm；",
          "用 Vite 创建 Vue3 + TypeScript 工程；",
          "安装 Element Plus、ECharts、Pinia、Vue Router、Axios 等依赖。"],
         ["pnpm dev 启动成功，浏览器可访问 5173。"],
         ["corepack enable",
          "corepack prepare pnpm@latest --activate",
          "pnpm --version",
          "",
          "cd ~/projects/campus-platform",
          "pnpm create vite web-admin --template vue-ts",
          "cd web-admin && pnpm install",
          "pnpm add element-plus echarts pinia vue-router axios dayjs",
          "pnpm add -D eslint prettier eslint-plugin-vue @typescript-eslint/parser \\",
          "  unplugin-auto-import unplugin-vue-components",
          "",
          "# 校验：",
          "pnpm dev",
          "# 浏览器访问 http://localhost:5173 应看到 Vite + Vue 初始页面"])

    step(doc, "3.6.2", "配置开发代理并联调后端接口",
         "开发期前端（5173）与后端（8000）分离部署，需要配置代理避免跨域问题，同时保持与生产 Nginx 配置一致。",
         ["在 vite.config.ts 中配置 /api 代理到 http://localhost:8000；",
          "在前端调用 /health 接口；",
          "确认浏览器无跨域报错。"],
         ["页面能显示后端返回的健康检查结果。"],
         ["# vite.config.ts 片段",
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

    h(doc, "3.7 搭建设备与外设模拟环境（无硬件也能开发）", 2)
    step(doc, "3.7.1", "搭建伪视频流（RTSP）",
         "设备到货前必须能开发视频接入与 AI 分析，用 MediaMTX + FFmpeg 模拟真实摄像机最接近现场协议。",
         ["用 Docker 启动 MediaMTX 流媒体服务器；",
          "用 FFmpeg 把一段校园视频循环推成 RTSP 流；",
          "用 VLC 或平台拉流验证。"],
         ["可拉取 rtsp://localhost:8554/cam1 并看到画面。"],
         ["# 启动流媒体服务器",
          "docker run --rm -d --name mediamtx -p 8554:8554 -p 8888:8888 bluenviron/mediamtx:latest",
          "",
          "# 推一路伪摄像头（把视频文件路径换成你本机的样本视频）",
          "ffmpeg -re -stream_loop -1 -i /mnt/d/campus/data/sample/campus.mp4 \\",
          "  -c copy -f rtsp rtsp://localhost:8554/cam1",
          "",
          "# 校验：",
          "ffprobe -rtsp_transport tcp -i rtsp://localhost:8554/cam1 -show_streams | head -30",
          "# 也可用 VLC 打开该地址确认画面",
          "",
          "# 多路模拟（对应多路摄像机并发分析）",
          "for i in 2 3 4; do ffmpeg -re -stream_loop -1 -i /mnt/d/campus/data/sample/campus.mp4 \\",
          "  -c copy -f rtsp rtsp://localhost:8554/cam$i & done"])

    step(doc, "3.7.2", "搭建 MQTT 设备模拟器",
         "门禁、环境传感器、能耗表等设备在到货前无法联调，用脚本按真实报文格式上报即可完成 80% 的开发。",
         ["安装 paho-mqtt（后端环境已含）；",
          "编写设备模拟脚本，模拟传感器周期上报与门禁通行上报；",
          "用 MQTTX 或订阅端确认平台能收到。"],
         ["平台/MQTTX 能持续收到模拟设备消息。"],
         ["python - <<'PY'",
          "import json, random, time, paho.mqtt.client as mqtt",
          "c = mqtt.Client('sim-gateway-01')",
          "c.connect('localhost', 1883, 60)",
          "c.loop_start()",
          "while True:",
          "    # 环境传感器：温湿度与 CO2",
          "    c.publish('iot/env/B01/F03/telemetry', json.dumps({",
          "        't': round(random.uniform(18, 26), 1), 'co2': random.randint(500, 1200),",
          "        'ts': int(time.time())}))",
          "    # 门禁通行上报（模拟人员通过闸机）",
          "    c.publish('iot/access/gate-01/event', json.dumps({",
          "        'person_id': 'S2026001', 'direction': 'in', 'credential': 'face',",
          "        'confidence': 0.98, 'ts': int(time.time())}))",
          "    time.sleep(5)",
          "PY",
          "",
          "# 校验：另开终端或用 MQTTX 订阅确认",
          "docker run --rm -it eclipse-mosquitto mosquitto_sub -h host.docker.internal -t 'iot/#' -v"])

    step(doc, "3.7.3", "准备门禁与车牌识别的桩服务",
         "真实设备协议往往不开放或文档不全；先用桩服务把平台的接收端与业务逻辑写完，设备到位后只需替换地址。",
         ["用 FastAPI 写一个极简桩服务，暴露通行上报与车牌上报接口；",
          "按真实报文结构返回平台期望的字段；",
          "在平台侧配置设备地址指向桩服务。"],
         ["平台可接收桩服务上报的通行与车牌事件，并生成记录与事件。"],
         ["# stub_device.py —— 设备桩服务（FastAPI）",
          "from fastapi import FastAPI",
          "import time, random",
          "app = FastAPI(title='设备桩服务')",
          "",
          "@app.post('/api/device/access/report')",
          "def access_report():",
          "    return {'code': 0, 'data': {'person_id': 'S2026001', 'direction': 'in',",
          "            'credential': 'face', 'confidence': 0.98, 'ts': int(time.time())}}",
          "",
          "@app.post('/api/device/vehicle/report')",
          "def vehicle_report():",
          "    return {'code': 0, 'data': {'plate': '鲁N12345', 'type': 'sedan',",
          "            'gate': 'gate-north', 'ts': int(time.time())}}",
          "",
          "# 启动：uv run uvicorn stub_device:app --port 9100",
          "# 校验：curl -X POST http://localhost:9100/api/device/access/report"])

    h(doc, "3.8 配置本地 Nginx 网关（可选）", 2)
    step(doc, "3.8.1", "用 Nginx 反向代理前后端",
         "与生产环境保持一致的反代结构（前端静态 + /api 转发后端 + 限流），提前暴露路径与缓存类问题。",
         ["下载 Windows 版 Nginx 或直接用 Docker 运行；",
          "编写站点配置：静态根指向前端构建产物，/api 转发到 8000；",
          "启动并用 8080 端口访问验证。"],
         ["通过 http://localhost:8080 能打开前端，且 /api/health 正常。"],
         ["# 用 Docker 运行 Nginx（挂载配置与前端产物）",
          "docker run --rm -d --name campus-nginx -p 8080:80 \\",
          "  -v ~/projects/campus-platform/deploy/nginx/dev.conf:/etc/nginx/conf.d/default.conf:ro \\",
          "  -v ~/projects/campus-platform/web-admin/dist:/usr/share/nginx/html:ro \\",
          "  nginx:alpine",
          "",
          "# 校验：",
          "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/",
          "curl -s http://localhost:8080/api/health"])

    h(doc, "3.9 配置监控与日志（可选，建议 V1 阶段补上）", 2)
    step(doc, "3.9.1", "部署 Prometheus + Grafana 采集后端指标",
         "架构方案将 Prometheus + Grafana 列为推荐监控方案；提前接入可在联调阶段发现性能退化。",
         ["后端启用 prometheus-client 暴露 /metrics；",
          "用 Docker 启动 Prometheus 与 Grafana；",
          "在 Grafana 中导入基础面板查看接口 QPS 与延迟。"],
         ["Grafana 能显示后端指标曲线。"],
         ["# 后端：app/main.py 中挂载指标",
          "# from prometheus_client import make_asgi_app",
          "# app.mount('/metrics', make_asgi_app())",
          "",
          "# 启动监控栈",
          "docker run -d --name campus-prom -p 9090:9090 \\",
          "  -v ~/projects/campus-platform/deploy/prometheus.yml:/etc/prometheus/prometheus.yml \\",
          "  prom/prometheus",
          "docker run -d --name campus-grafana -p 3000:3000 grafana/grafana",
          "",
          "# 校验：",
          "curl -s http://localhost:8000/metrics | head -5",
          "curl -s http://localhost:9090/-/healthy",
          "# Grafana: http://localhost:3000（默认 admin/admin，首次登录需改口令）"])

    h(doc, "3.10 台式机验收清单（25 项，全部通过方可进入后续开发）", 2)
    add_table(doc, ["编号", "验收项", "校验命令", "通过标准"],
              [["D-01", "WSL2 正常", "wsl -l -v", "Ubuntu-24.04 Running，VERSION=2"],
               ["D-02", "WSL 资源限制生效", "wsl -d Ubuntu-24.04 -- free -h", "内存接近 .wslconfig 设定值"],
               ["D-03", "apt 源为国内", "grep -r aliyun /etc/apt/sources.list.d/", "有 aliyun 记录"],
               ["D-04", "Docker 可用", "docker run --rm hello-world", "输出 Hello from Docker!"],
               ["D-05", "Docker 加速生效", "docker info | Select-String 'Registry Mirrors'", "显示专属加速地址"],
               ["D-06", "PG16 + pgvector", "docker exec campus-pg psql -U campus -d campus -c '\\dx'", "扩展列表含 vector"],
               ["D-07", "Redis 7 连通", "docker exec campus-redis redis-cli -a <口令> ping", "PONG"],
               ["D-08", "EMQX 连通", "curl -s http://localhost:18083/status", "返回状态信息"],
               ["D-09", "MinIO 存活", "curl -s http://localhost:9000/minio/health/live", "HTTP 200"],
               ["D-10", "后端依赖齐全", "uv run python -c \"import fastapi, sqlalchemy, asyncpg\"", "无报错"],
               ["D-11", "后端服务可启", "curl -s http://localhost:8000/health", "status=ok"],
               ["D-12", "Swagger 可访问", "浏览器打开 /docs", "接口文档正常显示"],
               ["D-13", "数据库迁移成功", "alembic current", "显示最新版本号"],
               ["D-14", "NVIDIA 驱动正常", "nvidia-smi", "显示 RTX 3050 与驱动版本"],
               ["D-15", "PyTorch CUDA 可用", "python -c \"import torch;print(torch.cuda.is_available())\"", "True"],
               ["D-16", "Ultralytics 可用", "yolo version", "输出版本号"],
               ["D-17", "最小训练跑通", "查看 runs/detect/*/weights/best.pt", "权重文件存在"],
               ["D-18", "ONNX 导出成功", "ls runs/detect/*/weights/best.onnx", "文件存在"],
               ["D-19", "推理一致性达标", "对比脚本输出", "与 PyTorch 偏差 ≤1e-3"],
               ["D-20", "前端可启动", "浏览器访问 http://localhost:5173", "页面正常"],
               ["D-21", "前后端联调通", "curl -s http://localhost:5173/api/health", "返回后端 JSON"],
               ["D-22", "伪视频可拉流", "ffprobe rtsp://localhost:8554/cam1", "输出视频流信息"],
               ["D-23", "MQTT 模拟可上报", "MQTTX 订阅 iot/#", "持续收到模拟消息"],
               ["D-24", "桩服务可访问", "curl -X POST http://localhost:9100/api/device/access/report", "返回模拟数据"],
               ["D-25", "环境自检通过", "python 环境工具\\scripts\\check-env.py --role dev", "通过率 100%"]],
              [1.2, 3.2, 6.8, 3.4], size=8.5, align_center_cols=(0,))


def chapter3(doc):
    """单台式机全栈：本项目的唯一环境主线。"""
    h(doc, "第 4 章 台式机全栈环境（本方案主线：一台电脑搞定全部开发与测试）", 1, page_break=True)
    para(doc, "本项目只需要在台式机上搭一套完整环境，就能完成开发、联调、算法训练与演示。"
              "本章按 4.1 → 4.6 顺序执行即可，全程约 1—2 个工作日。"
              "笔记本、协作同学电脑与服务器都不是开发的前置条件，其环境配置见第 5—7 章。")
    add_table(doc, ["章节", "配置内容", "为什么要它", "预计耗时", "完成标志"],
              [["4.1", "WSL2 + Ubuntu 24.04", "所有服务端组件的运行底座，与现场服务器命令一致", "30—60 分钟", "wsl -l -v 显示 Running / VERSION 2"],
               ["4.2", "Docker Desktop + 依赖服务全栈", "把数据库、缓存、消息、对象存储装进容器，一条命令起停", "60—90 分钟", "4 个服务 healthy，PG/Redis/EMQX/MinIO 可连"],
               ["4.3", "Python 后端 + Vue 前端", "业务代码开发与前后端联调", "约 80 分钟", "Swagger 可打开、页面能调后端接口"],
               ["4.4", "AI 训练环境与 ONNX 导出", "模型训练、导出与推理验证（本项目技术亮点）", "90—150 分钟", "CUDA 可用，训练出权重并导出 ONNX"],
               ["4.5", "设备模拟、本地网关与监控", "没有真实硬件也能跑通“采集→分析→告警”全链路", "60—90 分钟", "伪视频可拉流、模拟设备可上报"],
               ["4.6", "单机开发环境验收（15 项）", "确认环境可用，可以开始写功能", "30 分钟", "15 项全部通过"]],
              [1.2, 4.4, 5.6, 2.4, 4.6], size=8.5, align_center_cols=(0, 3))

    h(doc, "4.1 WSL2 与 Ubuntu 24.04", 2)
    para(doc, "这一节装的是“Linux 底座”：数据库容器、后端服务、AI 推理都跑在它上面。"
              "如果只写前端可以暂时跳过；但要做后端或算法，这一步不能省。", size=10)
    _steps_wsl(doc)

    h(doc, "4.2 Docker Desktop 与依赖服务全栈", 2)
    para(doc, "这一节解决“没有服务器也能开发”的问题：PostgreSQL 16、Redis 7、EMQX 5、MinIO 全部以容器形式"
              "装进你的电脑，一条命令起、一条命令停，不污染系统、不怕装坏、删掉不留垃圾。", size=10)
    _steps_docker(doc)

    h(doc, "4.3 后端与前端开发环境", 2)
    para(doc, "这一节装业务开发环境：后端 FastAPI（8000 端口）与前端 Vue3（5173 端口）都在本机运行，"
              "前端通过代理访问后端，因此单机即可完成联调，不需要额外的开发服务器。", size=10)
    _steps_app(doc)

    h(doc, "4.4 AI 训练环境与 ONNX 导出", 2)
    para(doc, "这一节是本项目的技术亮点：训练 YOLO 模型并导出 ONNX 供边缘推理使用。"
              "只有带 NVIDIA 显卡的电脑需要做这一节（本方案的台式机符合条件）。", size=10)
    _steps_ai(doc)

    h(doc, "4.5 设备模拟、本地网关与监控", 2)
    _steps_misc(doc)

    h(doc, "4.6 单机开发环境验收", 2)
    para(doc, "以下 15 项全部通过，说明这台电脑已具备完整开发能力，可以开始写功能代码。"
              "更严格的 25 项全栈验收见第 9 章。", size=10)
    _acceptance_simple(doc)


def chapter_extra1(doc):
    h(doc, "第 5 章 外援环境一：备份与演示环境（笔记本或旧电脑，可选）", 1, page_break=True)
    para(doc, "这一台机器的作用只有一个：在断网、出差、答辩现场等场景下，把已经开发好的平台完整跑起来演示。"
              "它不写代码、不做算法训练，因此配置极简：同一份仓库、同一份 compose、加一个 Nginx。")
    add_table(doc, ["用途", "说明", "要用到的组件"],
              [["离线演示", "竞赛现场或外出教研时断网演示，数据由模拟设备产生（伪视频 + MQTT 模拟器）",
                "Docker 全栈 + 前端构建产物 + Nginx + 模拟脚本"],
               ["备用运行", "开发机送去维修或临时当服务器用，保证演示环境不中断", "Docker 全栈 + 备份的数据库快照"],
               ["不做的事", "不在上面写业务代码、不训练模型、不做数据库结构变更", "—"]],
              [2.6, 8.0, 4.0], size=9)
    add_table(doc, ["配置项", "是否安装", "原因"],
              [["Git / VS Code / Node LTS + pnpm", "安装", "拉取仓库、构建前端产物"],
               ["Python 3.12", "安装", "运行后端与模拟脚本"],
               ["WSL2 + Ubuntu 24.04", "安装", "与开发机、服务器命令一致"],
               ["Docker Desktop", "安装（内存限 8—10GB）", "承载 PG / Redis / EMQX / MinIO 与平台服务"],
               ["PyTorch + CUDA / Ultralytics", "不安装", "训练统一在台式机，权重作为文件拷贝过来即可"],
               ["OBS Studio", "安装", "录制演示视频作为比赛备份"]],
              [4.0, 2.6, 7.4], size=9)

    h(doc, "5.1 三步配好演示环境", 2)
    step(doc, "5.1.1", "完成通用基线并拉起依赖服务",
         "复用与开发机完全相同的仓库与编排文件，保证演示环境与开发环境行为一致。",
         ["按第 2 章完成通用基线（跳过 AI 与 Python 双版本）；",
          "克隆同一仓库；",
          "用同一份 docker-compose.dev.yml 起依赖服务。"],
         ["依赖服务全部 healthy。"],
         ["cd ~/projects/campus-platform/deploy",
          "cp .env.example .env && vim .env      # 口令可与开发机相同",
          "docker compose -f docker-compose.dev.yml up -d",
          "docker compose -f docker-compose.dev.yml ps",
          "",
          "# 校验：",
          "curl -s -o /dev/null -w '%{http_code}' http://localhost:9000/minio/health/live"])
    step(doc, "5.1.2", "构建前端产物并用 Nginx 托管",
         "演示时不依赖 Vite 开发服务器，用静态产物 + Nginx，启动快、断网也不影响。",
         ["构建前端生产产物；", "用 Nginx 容器托管并反代后端；", "从 8080 端口访问验证。"],
         ["通过 http://localhost:8080 可完整访问平台。"],
         ["cd ~/projects/campus-platform/web-admin && pnpm build",
          "docker run --rm -d --name demo-nginx -p 8080:80 \\",
          "  -v ~/projects/campus-platform/deploy/nginx/demo.conf:/etc/nginx/conf.d/default.conf:ro \\",
          "  -v ~/projects/campus-platform/web-admin/dist:/usr/share/nginx/html:ro nginx:alpine",
          "",
          "# 校验：",
          "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/",
          "curl -s http://localhost:8080/api/health"])
    step(doc, "5.1.3", "准备断网演示包与录屏备份",
         "现场网络不可控，必须做到拔掉网线也能演示；同时准备录屏作为最终兜底。",
         ["预拉并导出全部容器镜像；",
          "准备伪视频素材与 MQTT 模拟脚本；",
          "用 OBS 完整录制一遍演示流程，文件放本机与移动硬盘各一份。"],
         ["断网后 8080 端口完整可用；录屏文件可播放。"],
         ["docker pull pgvector/pgvector:pg16 redis:7-alpine emqx/emqx:5 minio/minio nginx:alpine",
          "docker save pgvector/pgvector:pg16 redis:7-alpine emqx/emqx:5 minio/minio nginx:alpine \\",
          "  -o D:\\campus\\installers\\images-demo.tar",
          "",
          "# 校验：",
          "Get-ChildItem D:\\campus\\preview -Filter *.mp4 | Select-Object Name,@{n='MB';e={[math]::Round($_.Length/1MB,1)}}"])

    h(doc, "5.2 演示环境验收清单", 2)
    add_table(doc, ["编号", "验收项", "通过标准"],
              [["S-01", "依赖服务全起", "docker compose ps 全部 healthy"],
               ["S-02", "后端 /health 正常", "status=ok"],
               ["S-03", "前端可从 8080 访问", "页面正常且 /api 可用"],
               ["S-04", "断网演示可用", "拔网线后完整演示无异常"],
               ["S-05", "镜像已本地备份", "images-demo.tar 存在且可导入"],
               ["S-06", "演示录屏已备份", "录屏文件存在且可播放"]],
              [1.4, 4.6, 8.0], size=9, align_center_cols=(0,))


def chapter_extra2(doc):
    h(doc, "第 6 章 外援环境二：协作同学 / 学生电脑（角色化协作环境）", 1, page_break=True)
    para(doc, "当需要别人协助开发（同学、学生团队、外部顾问）时，对方的电脑不需要复制你的整套环境，"
              "只需要装“开发工具 + 客户端”，通过网络连到你的机器或云端。这样既省事，也避免环境不一致带来的扯皮。"
              "本章给出可直接转发给对方的清单；可转发的独立文件见《协作开发环境配置指引》。")
    add_table(doc, ["协作角色", "对方需要装什么", "对方能做什么", "不需要装什么"],
              [["前端开发", "Git、VS Code、Node LTS + pnpm、浏览器", "改页面与样式，通过代理访问你的后端接口", "数据库、Docker、Python、AI 环境"],
               ["后端开发", "Git、VS Code、Python 3.12、DBeaver、Apifox", "改接口与业务逻辑，连你的数据库或本地库", "AI 训练环境（除非兼做算法）"],
               ["算法 / 数据标注", "Git、Python 3.11、Ultralytics、标注工具", "标注数据、小规模训练、导出 ONNX", "完整平台栈"],
               ["测试 / 演示", "浏览器、MQTTX、Apifox", "多角色测试、接口验证、页面走查", "全部开发环境"],
               ["仅查看成果", "浏览器", "打开你部署好的地址查看效果", "全部"]],
              [2.4, 4.4, 5.2, 3.4], size=8.5)

    h(doc, "6.1 协作同学的安装步骤（可直接转发给对方）", 2)
    step(doc, "6.1.1", "安装基础工具（约 30 分钟）",
         "对方只需要能写代码、能拉代码、能连服务；装得越少越不容易出问题。",
         ["以管理员身份打开 PowerShell，执行下方安装命令；",
          "配置 npm 与 pip 国内镜像源；",
          "配置 Git 用户名与邮箱。"],
         ["git / node / pnpm 均有版本输出；镜像源为国内地址。"],
         ["winget install --id Git.Git -e",
          "winget install --id Microsoft.VisualStudioCode -e",
          "winget install --id OpenJS.NodeJS.LTS -e",
          "corepack enable",
          "corepack prepare pnpm@latest --activate",
          "",
          "npm config set registry https://registry.npmmirror.com",
          "git config --global user.name \"对方姓名\"",
          "git config --global user.email \"对方邮箱\"",
          "",
          "# 校验：",
          "git --version; node -v; pnpm -v; npm config get registry"])
    step(doc, "6.1.2", "拉取代码并连上你的后端",
         "让对方使用你的仓库与你的服务地址工作，避免各自维护不同版本。",
         ["获取仓库地址与你机器的 IP（或云端域名）；",
          "克隆仓库并安装前端依赖；",
          "配置前端接口地址指向你的后端；",
          "启动前端并验证能调通接口。"],
         ["对方浏览器能打开页面并成功加载后端数据。"],
         ["git clone https://gitee.com/<你的仓库>/campus-platform.git",
          "cd campus-platform/web-admin && pnpm install",
          "",
          "# 在 .env.development 中配置后端地址（换成你的 IP 或域名）",
          "VITE_API_BASE=http://192.168.1.10:8000",
          "",
          "pnpm dev",
          "# 校验：浏览器打开 http://localhost:5173，能加载到后端返回的数据"])
    step(doc, "6.1.3", "交接访问清单与协作约定",
         "让对方知道该连哪里、该守什么规矩，减少来回沟通成本。",
         ["提供访问清单：仓库、后端、前端、MQTT 地址与测试账号；",
          "约定分支策略与提交规范；",
          "强调敏感数据红线（人脸数据不外传、口令不写进代码）。"],
         ["对方按清单可独立完成一次提交。"],
         ["# 访问清单模板（发给协作者）",
          "仓库：https://gitee.com/<你的仓库>/campus-platform.git",
          "后端 API：http://192.168.1.10:8000        （Swagger: /docs）",
          "前端页面：http://192.168.1.10:5173",
          "MQTT：192.168.1.10:1883（外网用 TLS 8883）",
          "EMQX 控制台：http://192.168.1.10:18083",
          "测试账号：见 项目文档/环境记录/测试账号.md（口令单独发送）",
          "",
          "# 协作红线：",
          "# 1) 不把 .env、口令、人脸样本提交到仓库",
          "# 2) 分支命名 feature/xxx，提交前先 git pull --rebase",
          "# 3) 涉及数据库结构变更必须先说明并走 Alembic 迁移脚本"])

    h(doc, "6.2 协作环境验收清单", 2)
    add_table(doc, ["编号", "验收项", "通过标准"],
              [["C-01", "基础工具就绪", "git / node / pnpm 均有版本输出"],
               ["C-02", "镜像源为国内", "npm registry 为 npmmirror"],
               ["C-03", "代码可拉取", "git clone 成功且能 push"],
               ["C-04", "前端可启动", "pnpm dev 后页面正常"],
               ["C-05", "能连你的后端", "页面可加载后端数据，无跨域报错"],
               ["C-06", "能完成一次提交", "远端可见其提交记录"],
               ["C-07", "已知晓协作红线", "确认不提交口令与人脸数据"]],
              [1.4, 4.6, 8.0], size=9, align_center_cols=(0,))
