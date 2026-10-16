# -*- coding: utf-8 -*-
"""生成 07_开发环境搭建与部署准备指南.docx"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_master import build, stage_summary
from docx_kit import *
from docx_kit import _font
from docx import Document

OUT = r"F:\职业中专\大赛\智慧园区创意\项目文档\07_开发环境搭建与部署准备指南.docx"
rows = build()
st = stage_summary(rows)

doc = Document()
setup(doc, "开发环境搭建与部署准备指南 V1.0")
cover(doc,
      "“智园卫士”智慧校园管理平台",
      "开发环境搭建、学生机房标准化与现场部署准备清单",
      [("文档名称", "开发环境搭建与部署准备指南"),
       ("文档编号", "ZYWS-DEV-2026-001"),
       ("版本号", "V1.0（概览版，已被 V2 取代）"),
       ("重要提示", "本文档为早期“三机分工”版本。环境主线已由《电脑环境配置详细方案》V2.0（文档 09）取代，"
                    "请以文档 09 V2.0 为准；本文档仅作参考与索引保留，内容仍然有效但不再更新"),
       ("替代关系", "文档 09 V2.0《电脑环境配置详细方案》（单机全栈版）+ 文档 11《电脑环境配置总览与快速开始》"),
       ("编制单位", "齐河县职业中等专业学校 项目组"),
       ("适用对象", "项目开发团队、机房管理员、实施与运维人员"),
       ("适用环境", "Windows 10/11 开发机 ｜ 阿里云等公有云服务器 ｜ 学生机房 ｜ 学校现场服务器"),
       ("编制日期", "2026 年 11 月"),
       ("密级", "内部")],
      doc_kind="开 发 环 境 搭 建 与 部 署 准 备 指 南")

# ============================================================
h(doc, "0 五分钟速览：先做什么、装在哪台机器", 1, page_break=True)
para(doc, "本指南针对团队现有的三台电脑与“本机 Windows + 公有云”的运行方式编写。不同机器的能力差异很大，"
          "如果三台机器装成一样的环境，会浪费主力机的算力、也会让弱机跑不动。因此第一步不是装软件，而是**分工**。")
add_table(doc,
          ["机器", "实际配置", "定位", "能做什么", "不要做什么"],
          [["台式机\n（主力）", "i5-13400F + RTX 3050 8GB +（建议加内存到 32GB）",
            "AI 训练机 + 全栈一体化开发机",
            "YOLO 模型训练/微调、ONNX 导出、边缘推理验证、Docker 起全栈（PG/Redis/EMQX/MinIO/FastAPI）、大屏与前端联调",
            "不要作为唯一的数据保存地（单机无冗余）；不要长期关机存放代码"],
           ["笔记本 1", "AMD Ryzen 7 5800U（8 核 16 线程）+ 16GB + 集显",
            "服务宿主 / 演示机（无 CUDA）",
            "Docker 起数据库与中间件、写后端与前端、外出演示、评委面前跑平台",
            "不要用它做模型训练（Radeon 集显不支持 CUDA，训练会慢到无法接受）"],
           ["笔记本 2", "i5-7300HQ + 16GB + GTX 1050 2GB",
            "客户端 / 设备联调机",
            "前端与文档、开浏览器做多角色测试（学生/教师/家长/门卫）、串口与网口调试、模拟终端",
            "不要装 Docker Desktop 全栈（CPU 与磁盘都吃紧）；不要装 CUDA 训练环境（算力 6.1、显存 2GB）"],
           ["阿里云 ECS\n（2 核 4G 起）", "Ubuntu 24.04 LTS，后续可升 4 核 8G",
            "业务中枢 / 对外发布 / 异地备份",
            "部署业务 API、数据库、报表与驾驶舱、小程序后端（HTTPS）、代码仓库镜像与备份",
            "不要用来接收校内摄像头视频流（带宽按量计费会非常贵，且存在合规风险）"]],
          [2.1, 3.5, 2.6, 5.0, 4.4], size=8.5)
note(doc, "一句话原则：AI 训练锁在台式机，服务与演示放在云上和笔记本 1，笔记本 2 只当客户端。视频永远留在校内，云端只收事件与缩略图。")

h(doc, "0.1 建议优先补的三件事", 2)
add_table(doc,
          ["优先级", "补强项", "花费参考", "为什么值得先花这笔钱"],
          [["高", "台式机内存 16GB → 32GB", "约 300—500 元",
            "Docker 全栈（PG+Redis+EMQX+MinIO+API）在开发机上同时跑时，16GB 会频繁触发交换，训练也会因为内存不足降低 batch"],
           ["高", "一块 1TB NVMe 固态（做数据盘/备份盘）", "约 400—600 元",
            "系统盘与数据库、视频样本、模型权重混在一张盘上，既影响性能也让备份无法落地"],
           ["中", "UPS（500—1000VA）或至少稳压插座", "约 300—800 元",
            "数据库正在写入时断电，是校园项目最常见的“数据损坏”来源；现场演示也怕跳闸"],
           ["中", "一个 32GB 以上的 USB 3.0 移动固态硬盘", "约 100—200 元",
            "用于机房批量装机镜像、离线安装包、演示环境迁移，一次投入反复使用"],
           ["低", "阿里云新用户优惠或学生认证", "首年约 100—300 元",
            "学生认证后 ECS 与 OSS 有明显折扣，云上环境的一年成本可以压到很低"]],
          [1.3, 4.4, 2.4, 7.2], size=9, align_center_cols=(0, 2))

# ============================================================
h(doc, "1 前置准备：账号、网络、镜像源", 1, page_break=True)
h(doc, "1.1 需要提前申请的账号与云资源", 2)
add_table(doc,
          ["类别", "具体内容", "用途", "优先级"],
          [["代码托管", "Gitee（国内，快）或 GitHub（国际，生态全）；建议两个都建，Gitee 作主、GitHub 作镜像", "源码版本管理、多机同步", "必办"],
           ["云服务器", "阿里云账号 → 实名认证 → 学生认证（如有）→ 创建 ECS（Ubuntu 24.04）", "云上业务中枢与对外发布", "必办"],
           ["域名与备案", "一个学校项目域名（如 xxx.edu.cn 由学校提供，或自购 .cn 域名）", "HTTPS 访问、小程序服务器白名单", "必办"],
           ["SSL 证书", "阿里云免费 DV 证书（每年申请，或 Let's Encrypt 自动续期）", "全站 HTTPS，满足小程序与合规要求", "必办"],
           ["对象存储", "阿里云 OSS（标准存储 + 生命周期转低频）", "事件快照、报表导出、备份归档", "建议"],
           ["短信与推送", "阿里云短信（需模板报备）或微信小程序订阅消息", "未归预警、审批通知的真实触达", "建议"],
           ["微信小程序", "注册企业/学校主体小程序账号，配置服务器域名白名单", "学生、教师、家长端入口", "建议"],
           ["模型与数据", "ModelScope 魔搭（国内下载模型权重）、Kaggle 账号（公开数据集）", "AI 训练数据与预训练权重", "建议"],
           ["团队协作", "飞书/钉钉（消息）、语雀/腾讯文档（文档）、Trello/看板（任务）", "进度同步与文档沉淀", "必办"]],
          [2.1, 6.0, 4.0, 1.4], size=9, align_center_cols=(3,))
note(doc, "注意：ECS 购买时系统盘建议 40—60GB ESSD，带宽选择“按使用流量”起步（固定带宽在传大文件时会成为瓶颈）；安全组只放行 22（限本人 IP）、80、443。")

h(doc, "1.2 国内镜像源配置（这一步不做，后面每一步都会很慢）", 2)
para(doc, "国内直连官方源经常超时或极慢。所有机器在装开发工具之前，先统一配置以下镜像源。")
add_table(doc,
          ["工具", "配置文件/命令", "镜像地址", "生效范围"],
          [["pip", "%APPDATA%\\pip\\pip.ini（Windows）或 ~/.pip/pip.conf",
            "https://pypi.tuna.tsinghua.edu.cn/simple（清华，也可用阿里云）", "Python 包"],
           ["npm / pnpm", "npm config set registry https://registry.npmmirror.com",
            "https://registry.npmmirror.com（淘宝镜像）", "前端依赖"],
           ["Maven/Gradle", "（本项目的 Java 端仅用于对接第三方，如无需要可跳过）", "阿里云 maven 仓库", "第三方 SDK"],
           ["apt（Ubuntu/WSL）", "/etc/apt/sources.list.d/ubuntu.sources（24.04 为 DEB822 格式）",
            "https://mirrors.aliyun.com/ubuntu 或清华源", "系统包"],
           ["Docker 镜像", "Docker Desktop → Settings → Docker Engine 中增加 registry-mirrors",
            "使用阿里云容器镜像服务（ACR）控制台提供的个人专属加速地址", "镜像拉取"],
           ["模型权重", "pip install modelscope，用 snapshot_download 拉取", "ModelScope 魔搭社区", "YOLO 预训练权重与公开数据集"],
           ["Git 大文件", "git lfs install 并在仓库启用 LFS", "Gitee/GitHub LFS", "模型权重与数据集版本管理"]],
          [2.0, 5.0, 5.0, 2.5], size=9)
para(doc, "Docker 加速器要特别说明：网上流传的公共加速地址经常失效，正确做法是登录阿里云“容器镜像服务 ACR”控制台，"
          "在“镜像工具 → 镜像加速器”里复制属于你账号的专属地址，填到 Docker Desktop 的 registry-mirrors 中。")
add_code(doc, [
    "# pip 镜像（Windows，一次配置全局生效）",
    "mkdir %APPDATA%\\pip",
    "notepad %APPDATA%\\pip\\pip.ini",
    "",
    "[global]",
    "index-url = https://pypi.tuna.tsinghua.edu.cn/simple",
    "trusted-host = pypi.tuna.tsinghua.edu.cn",
    "",
    "# npm 镜像",
    "npm config set registry https://registry.npmmirror.com",
    "npm config get registry",
])

# ============================================================
h(doc, "2 台式机（主力机）：AI 训练 + 全栈开发环境", 1, page_break=True)
para(doc, "这台机器承担最重的活：模型训练与全栈联调。安装顺序建议按本节 2.1 → 2.9 依次执行，不要跳步。")

h(doc, "2.1 Windows 基础工具链（约 30 分钟）", 2)
add_table(doc,
          ["类别", "软件", "用途", "必装"],
          [["包管理", "winget（Windows 自带）或 Chocolatey", "一条命令批量安装后续软件", "是"],
           ["终端", "Windows Terminal + PowerShell 7", "统一命令行体验，UTF-8 与脚本兼容性更好", "是"],
           ["版本控制", "Git for Windows（含 Git Bash）", "代码版本管理与多机同步", "是"],
           ["编辑器", "Visual Studio Code", "主开发工具", "是"],
           ["运行时", "Python 3.12 与 Python 3.11（两个都装）", "后端用 3.12，AI 生态兼容用 3.11", "是"],
           ["运行时", "Node.js LTS（22.x）", "前端构建与小工具", "是"],
           ["容器", "Docker Desktop（WSL2 后端）", "一键起数据库、消息、对象存储等依赖", "是"],
           ["数据库客户端", "DBeaver Community 或 Navicat", "连接与调试 PostgreSQL", "是"],
           ["接口调试", "Apifox 或 Postman", "接口联调与自动化测试", "是"],
           ["抓包与调试", "Wireshark、Fiddler 或 Charles", "排查设备协议与接口问题", "建议"],
           ["串口调试", "SSCOM / XCOM / MobaXterm", "调试 RS-485、Modbus 设备", "建议"],
           ["远程运维", "MobaXterm 或 Xshell + WinSCP", "连接云服务器与现场服务器", "是"],
           ["录屏与演示", "OBS Studio", "录参赛演示视频、备份演示方案", "建议"],
           ["文档协作", "Office/WPS、Typora 或 VS Code + Markdown 插件", "编写与维护项目文档", "是"]],
          [2.0, 4.8, 6.6, 1.2], size=9, align_center_cols=(3,))
add_code(doc, [
    "# PowerShell（管理员）中批量安装（winget 方式，软件名以实际检索为准）",
    "winget install --id Git.Git -e",
    "winget install --id Microsoft.VisualStudioCode -e",
    "winget install --id Microsoft.PowerShell -e",
    "winget install --id Microsoft.WindowsTerminal -e",
    "winget install --id Python.Python.3.12 -e",
    "winget install --id Python.Python.3.11 -e",
    "winget install --id OpenJS.NodeJS.LTS -e",
    "winget install --id Docker.DockerDesktop -e",
    "winget install --id dbeaver.dbeaver -e",
    "winget install --id OBSProject.OBSStudio -e",
    "",
    "# 装完后统一设置 UTF-8，避免中文乱码与 Python 输出报错",
    "[System.Environment]::SetEnvironmentVariable('PYTHONUTF8','1','User')",
    "$env:PYTHONUTF8=1",
])

h(doc, "2.2 WSL2 + Ubuntu（Docker 的后端，必装）", 2)
para(doc, "Windows 上跑 Linux 容器最省事的方式是 WSL2：Docker Desktop 直接使用 WSL2 后端，同时你还得到一个完整的 Ubuntu 终端，"
          "可以按架构文档里的 Linux 命令部署，与现场服务器保持一致。")
add_table(doc,
          ["步骤", "命令/操作", "说明"],
          [["1. 开启虚拟化", "BIOS 中启用 Intel VT-x（Virtualization Technology）", "BIOS 未开启时 WSL2 无法工作"],
           ["2. 安装 WSL2", "管理员 PowerShell：wsl --install -d Ubuntu-24.04", "首次安装后需重启"],
           ["3. 设为默认版本", "wsl --set-default-version 2", "确认所有发行版都在 WSL2 下运行"],
           ["4. 首次进入", "设置 Linux 用户名与密码（与 Windows 密码无关）", "该账号后续用于 sudo"],
           ["5. 更新系统", "sudo apt update && sudo apt upgrade -y", "先配好 apt 镜像源再执行，速度差异巨大"],
           ["6. 常用工具", "sudo apt install -y build-essential curl wget git vim htop net-tools unzip ffmpeg", "ffmpeg 是视频处理与推流测试必备"],
           ["7. 目录互通", "Windows 的 D:\\ 盘在 WSL 中为 /mnt/d", "代码建议放在 WSL 家目录（性能远好于 /mnt），用 VS Code 的 WSL 远程模式打开"]],
          [1.8, 8.4, 5.4], size=9, align_center_cols=(0,))
note(doc, "重要经验：代码仓库放在 WSL 文件系统内（如 ~/projects），不要放在 /mnt/c 或 /mnt/d 下。跨文件系统会让 npm install 与热更新慢数倍。")

h(doc, "2.3 Docker Desktop 与依赖服务（一键起全套）", 2)
para(doc, "架构方案中明确：竞赛版用 Docker Compose“一条命令起全栈”。因此开发机上不需要手工安装 PostgreSQL、Redis、EMQX 和 MinIO，"
          "全部用容器运行，版本与现场服务器完全一致，避免“我这里能跑”的问题。")
add_code(doc, [
    "# 1) Docker Desktop 设置：Settings → General 勾选 Use the WSL 2 based engine",
    "# 2) Settings → Docker Engine 中增加国内镜像加速地址（用阿里云 ACR 的专属地址）",
    "# 3) Settings → Resources 给 WSL 分配内存（16GB 机器建议 8GB，32GB 机器建议 16GB）",
    "",
    "# 4) 验证",
    "docker --version",
    "docker compose version",
    "docker run --rm hello-world",
    "",
    "# 5) 一键拉起开发依赖（docker-compose.dev.yml 只包含基础设施，不含业务代码）",
    "docker compose -f docker-compose.dev.yml up -d",
    "docker compose ps",
])
add_table(doc,
          ["服务", "镜像（示例）", "端口", "用途", "默认账号提示"],
          [["PostgreSQL 16", "postgres:16", "5432", "业务主库（人员、通行、事件、审批等）", "自定义强口令，禁止用 postgres/postgres"],
           ["pgvector", "pgvector/pgvector:pg16", "5432", "人脸底库向量检索（替代方案：单独装扩展）", "与 PostgreSQL 合并部署即可"],
           ["Redis 7", "redis:7-alpine", "6379", "缓存、会话、通行白名单二级缓存", "启用 AOF，设置密码"],
           ["EMQX 5", "emqx/emqx:5", "1883 / 8083 / 18083", "MQTT 设备接入与规则转发", "首次登录后立即改掉默认密码"],
           ["MinIO", "minio/minio", "9000 / 9001", "对象存储（事件截图、短视频、报表）", "设置强密钥，桶权限设为私有"],
           ["TDengine 3", "tdengine/tdengine", "6030 / 6041", "能耗与环境时序数据（V2 阶段再启用）", "可先用 PostgreSQL 分区表降级"]],
          [2.0, 3.2, 2.6, 5.4, 3.6], size=8.5)
add_code(doc, [
    "# docker-compose.dev.yml 参考骨架（放仓库 deploy/ 目录，与现场部署共用一份）",
    "services:",
    "  postgres:",
    "    image: pgvector/pgvector:pg16",
    "    environment:",
    "      POSTGRES_DB: campus",
    "      POSTGRES_USER: campus",
    "      POSTGRES_PASSWORD: ${PG_PASSWORD}   # 从 .env 读取，禁止写进代码库",
    "    ports: ['5432:5432']",
    "    volumes: ['pgdata:/var/lib/postgresql/data']",
    "    healthcheck:",
    "      test: ['CMD-SHELL', 'pg_isready -U campus']",
    "      interval: 10s",
    "  redis:",
    "    image: redis:7-alpine",
    "    command: ['redis-server', '--appendonly', 'yes', '--requirepass', '${REDIS_PASSWORD}']",
    "    ports: ['6379:6379']",
    "  emqx:",
    "    image: emqx/emqx:5",
    "    ports: ['1883:1883', '8083:8083', '18083:18083']",
    "  minio:",
    "    image: minio/minio",
    "    command: ['server', '/data', '--console-address', ':9001']",
    "    environment:",
    "      MINIO_ROOT_USER: ${MINIO_USER}",
    "      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}",
    "    ports: ['9000:9000', '9001:9001']",
    "volumes:",
    "  pgdata:",
])

h(doc, "2.4 后端开发环境（Python）", 2)
add_table(doc,
          ["能力", "工具/库", "说明"],
          [["依赖与虚拟环境", "uv（推荐，极快）或 venv + pip-tools", "每个项目独立虚拟环境，禁止全局装包"],
           ["Web 框架", "FastAPI + Uvicorn", "按架构方案，异步为主，竞赛版单进程多 Worker"],
           ["数据校验与配置", "Pydantic v2 + pydantic-settings", "统一配置与 .env 读取"],
           ["数据库访问", "SQLAlchemy 2.x（异步）+ Alembic", "迁移脚本纳入版本管理"],
           ["数据库驱动", "asyncpg（异步）/ psycopg[binary]", "PostgreSQL 连接"],
           ["缓存与队列", "redis-py、MQTT 客户端 paho-mqtt 或 gmqtt", "白名单缓存、设备消息处理"],
           ["任务调度", "APScheduler（开发期）→ Celery/RQ（生产）", "定时归寝判定、报表生成、数据同步"],
           ["鉴权", "python-jose / PyJWT + passlib[bcrypt]", "JWT 令牌与口令哈希"],
           ["接口文档", "FastAPI 自带 Swagger/ReDoc", "接口评审与联调依赖它"],
           ["测试", "pytest + httpx + pytest-asyncio", "接口自动化回归（对应功能 M12-12）"],
           ["代码质量", "ruff + mypy + black（或 ruff format）", "统一风格，减少合并冲突"],
           ["日志", "loguru 或 structlog + JSON 格式", "便于以后接入日志平台"]],
          [2.4, 4.6, 7.4], size=9)
add_code(doc, [
    "# 1) 安装 uv（Windows PowerShell）",
    "powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"",
    "",
    "# 2) 创建后端项目环境（在 WSL 中执行体验更好，Windows 亦可）",
    "cd ~/projects/campus-platform/backend",
    "uv venv --python 3.12",
    "source .venv/bin/activate        # Windows: .venv\\Scripts\\Activate.ps1",
    "",
    "# 3) 安装依赖（写入 pyproject.toml，锁定版本）",
    "uv add fastapi 'uvicorn[standard]' sqlalchemy asyncpg alembic pydantic-settings \\",
    "       redis paho-mqtt apscheduler 'python-jose[cryptography]' 'passlib[bcrypt]'",
    "uv add --dev pytest httpx pytest-asyncio ruff mypy",
    "",
    "# 4) 本地起服务并验证",
    "uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
    "# 浏览器打开 http://localhost:8000/docs 能看到 Swagger 即成功",
])

h(doc, "2.5 AI 训练环境（CUDA / PyTorch / YOLO）——仅台式机与支持 CUDA 的机器", 2)
para(doc, "RTX 3050（8GB 显存，计算能力 8.6）足以支撑本项目的模型训练需求：YOLOv8n/YOLO11n 级别模型在 640 分辨率、"
          "batch 8—16、FP16 混合精度下可以正常训练；若显存不足，把 imgsz 降到 416—512、batch 降到 4 即可。"
          "GTX 1050（2GB，计算能力 6.1）不建议装训练环境，只能做推理演示，且需使用较旧的驱动与 CUDA 11.x 组合。")
add_table(doc,
          ["环节", "内容", "关键提示"],
          [["显卡驱动", "安装 NVIDIA 官方最新 Game Ready 或 Studio 驱动（含 CUDA 运行时）", "先装驱动再装 PyTorch；驱动版本决定可用的 CUDA 上限，不必单独装完整 CUDA Toolkit"],
           ["基础环境", "Python 3.11 + PyTorch（cu12x 版本，从 PyTorch 官网获取对应命令）", "PyTorch 官方站会按你的选择生成安装命令，照抄即可；不要用 pip 默认源装 CPU 版"],
           ["训练框架", "Ultralytics（YOLO 系列）、OpenCV、NumPy、Pillow", "Ultralytics 自带训练/验证/导出全流程，一条命令起步"],
           ["标注工具", "LabelImg（矩形框）、Labelme（多边形/分割）、X-AnyLabeling（AI 辅助标注）", "标注规范必须先定：类别命名、最小框尺寸、遮挡处理、边界归属"],
           ["格式转换", "ONNX（opset 17）、onnxruntime、onnxsim", "训练用 PyTorch，交付用 ONNX，形成“一次训练、多端推理”"],
           ["数据管理", "DVC 或 Git LFS；数据集按 训练/验证/测试 分层且严格隔离", "测试集绝不能混进训练集，否则指标不可信"],
           ["训练监控", "TensorBoard 或 Ultralytics 自带可视化输出", "保存每次实验的配置与指标，便于复现"]],
          [1.8, 6.4, 6.2], size=9)
add_code(doc, [
    "# 1) 验证驱动与显卡",
    "nvidia-smi          # 能看到 GPU 型号与驱动版本即可",
    "",
    "# 2) 创建专用训练环境（Python 3.11 兼容性最好）",
    "uv venv --python 3.11 ~/.venvs/cv-train",
    "source ~/.venvs/cv-train/bin/activate     # Windows: .venv\\Scripts\\Activate.ps1",
    "",
    "# 3) 安装 PyTorch（务必到 pytorch.org 复制与你驱动匹配的 cu 版本命令，示例如下）",
    "uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124",
    "",
    "# 4) 安装训练与工具链",
    "uv pip install ultralytics opencv-python onnx onnxruntime onnxsim labelImg",
    "",
    "# 5) 验证 GPU 可用（必须输出 True 与显卡型号）",
    "python -c \"import torch;print(torch.cuda.is_available(), torch.cuda.get_device_name(0))\"",
    "",
    "# 6) 用官方小模型跑一次最小训练，验证全链路（10 分钟出结果即可）",
    "yolo detect train model=yolo11n.pt data=campus-fire.yaml epochs=10 imgsz=640 batch=8 device=0 amp=True",
    "",
    "# 7) 导出 ONNX 供边缘推理使用",
    "yolo export model=runs/detect/train/weights/best.pt format=onnx opset=17 dynamic=True simplify=True",
])

h(doc, "2.6 前端开发环境（Vue3）", 2)
add_table(doc,
          ["能力", "工具/库", "说明"],
          [["运行时与包管理", "Node.js LTS + pnpm（优于 npm，节省磁盘、安装快）", "启用 corepack 管理 pnpm 版本"],
           ["构建工具", "Vite", "开发热更新快，符合架构方案选型"],
           ["框架", "Vue 3（组合式 API）+ TypeScript", "统一用 TS，减少低级错误"],
           ["UI 组件", "Element Plus", "管理端表格/表单/弹窗直接复用"],
           ["状态与路由", "Pinia + Vue Router", "按角色划分路由与权限"],
           ["图表与大屏", "ECharts + 自研栅格缩放（1920×1080 基准）", "驾驶舱与统计图表"],
           ["3D（V3 阶段）", "Three.js", "校园三维沙盘"],
           ["网络请求", "Axios（统一拦截器：token、错误码、重试）", "与后端统一响应结构对齐"],
           ["代码质量", "ESLint + Prettier + vue-tsc", "提交前自动检查（husky + lint-staged）"],
           ["移动端", "uni-app（Vue3 语法，一套代码出小程序 + H5）", "学生/教师/家长端；也可用 HBuilderX 起步"]],
          [2.4, 5.0, 7.0], size=9)
add_code(doc, [
    "# 1) 启用 pnpm",
    "corepack enable",
    "corepack prepare pnpm@latest --activate",
    "pnpm --version",
    "",
    "# 2) 创建前端工程（Vue3 + TS）",
    "cd ~/projects/campus-platform",
    "pnpm create vite web-admin --template vue-ts",
    "cd web-admin",
    "pnpm install",
    "pnpm add element-plus echarts pinia vue-router axios dayjs",
    "pnpm add -D eslint prettier eslint-plugin-vue @typescript-eslint/parser unplugin-auto-import unplugin-vue-components",
    "",
    "# 3) 配置开发代理（vite.config.ts 中把 /api 代理到后端 8000 端口，避免跨域）",
    "pnpm dev     # 打开 http://localhost:5173",
])

h(doc, "2.7 硬件与设备模拟环境（无硬件也能开发）", 2)
para(doc, "设备到货前，开发进度不能被“等硬件”卡住。以下工具可在没有真实门禁、摄像机和传感器的情况下完成 80% 的开发与联调。")
add_table(doc,
          ["模拟对象", "工具/方法", "怎么用"],
          [["MQTT 设备", "MQTTX（图形客户端）或 Python 脚本 paho-mqtt", "用 MQTTX 模拟传感器上报与设备心跳，订阅平台下发的指令"],
           ["RTSP 视频流", "MediaMTX（轻量流媒体服务器）+ FFmpeg 循环推流", "把一段校园视频循环推成 rtsp://localhost:8554/cam1，平台按真实协议拉流"],
           ["模拟摄像头文件", "FFmpeg 直接以文件作为输入喂给算法服务", "适合算法调试阶段，可倍速回放评估准确率"],
           ["门禁一体机", "编写桩服务：模拟 HTTP/私有协议上报通行记录", "完全按真实报文格式构造，后期只换地址不换代码"],
           ["车牌识别", "桩服务 + 测试图片集", "模拟识别结果上报（车牌、时间、抓拍图 URL）"],
           ["出入闸机", "桩服务 + 开关量状态模拟", "验证策略引擎下发与放行结果回执"],
           ["环境与能耗传感器", "Python 脚本按 Modbus/MQTT 周期上报随机但合理的数值", "验证采集、存储、告警与图表"],
           ["压力与异常", "JMeter 或 Locust 打接口；脚本注入断网/超时/乱序报文", "验证性能指标（门禁鉴权 P95 ≤300ms）与容错"]],
          [2.4, 5.4, 6.6], size=9)
add_code(doc, [
    "# MediaMTX + FFmpeg 造一路假摄像头（WSL/Linux 下最省事）",
    "docker run --rm -d --name mediamtx -p 8554:8554 -p 8888:8888 bluenviron/mediamtx:latest",
    "ffmpeg -re -stream_loop -1 -i /path/to/campus.mp4 -c copy -f rtsp rtsp://localhost:8554/cam1",
    "",
    "# Python 模拟一个 MQTT 温度传感器（每 5 秒上报一次）",
    "python - <<'PY'",
    "import paho.mqtt.client as mqtt, json, random, time",
    "c = mqtt.Client('sim-env-01'); c.connect('localhost', 1883, 60)",
    "while True:",
    "    c.publish('iot/env/B01/F03/telemetry', json.dumps({'t': round(random.uniform(18,26),1),",
    "        'co2': random.randint(500,1200), 'ts': int(time.time())}))",
    "    time.sleep(5)",
    "PY",
])

h(doc, "2.8 IDE 与工程规范配置", 2)
add_table(doc,
          ["项目", "配置内容"],
          [["VS Code 扩展", "Python、Pylance、Ruff、SQLTools、Vue (Official)、ESLint、Prettier、Docker、Remote - WSL、GitLens、Markdown All in One、Error Lens"],
           ["工作区设置", "统一 UTF-8、保存自动格式化、Python 解释器指向项目虚拟环境、排除 .venv 与 node_modules 的搜索"],
           ["Git 规范", "分支策略：main（可演示）+ develop（集成分支）+ feature/xxx；提交信息格式 feat/fix/docs/test: 描述"],
           ["忽略文件", ".env、.venv、node_modules、__pycache__、runs/、*.pt、*.onnx 大文件（走 LFS）、数据集目录"],
           ["密钥管理", "所有口令、密钥放 .env（不进仓库）；仓库提供 .env.example 模板"],
           ["代码评审", "每个功能分支合并前至少 1 人 Review；MVP 阶段可用“结对提交”替代"]],
          [2.6, 11.6], size=9)

h(doc, "2.9 台式机验收清单（每项打勾才算装完）", 2)
add_table(doc,
          ["序号", "验收项", "命令/方法", "通过标准"],
          [["1", "Python 双版本可用", "python --version / py -3.11 --version", "分别输出 3.12.x 与 3.11.x"],
           ["2", "Node 与 pnpm", "node -v && pnpm -v", "Node 为 LTS，pnpm 正常输出版本"],
           ["3", "WSL2 正常", "wsl -l -v", "Ubuntu-24.04 状态为 Running，VERSION 为 2"],
           ["4", "Docker 正常", "docker run --rm hello-world", "输出 Hello from Docker!"],
           ["5", "依赖服务全起", "docker compose -f docker-compose.dev.yml ps", "5 个服务均为 healthy/running"],
           ["6", "数据库可连", "DBeaver 连接 localhost:5432", "能看到 campus 库与表结构"],
           ["7", "MQTT 可通", "MQTTX 连 localhost:1883 并收发消息", "平台能收到设备消息"],
           ["8", "后端可跑", "访问 http://localhost:8000/docs", "Swagger 正常打开"],
           ["9", "前端可跑", "pnpm dev 后访问 http://localhost:5173", "页面正常，接口代理生效"],
           ["10", "GPU 可训", "torch.cuda.is_available() 与一次 10 轮小训练", "输出 True，训练能跑完并生成权重"],
           ["11", "ONNX 可导出", "yolo export 后 onnxruntime 推理一张图", "推理结果与 PyTorch 偏差 ≤1e-3"],
           ["12", "伪视频可拉流", "平台拉 rtsp://localhost:8554/cam1", "视频画面正常，AI 分析能出结果"],
           ["13", "代码已入库", "git push 到 Gitee", "另一台机器能 clone 并跑起来"]],
          [1.0, 3.0, 5.6, 4.6], size=9, align_center_cols=(0,))

# ============================================================
h(doc, "3 笔记本 1（Ryzen 7 / 无 CUDA）：服务宿主与演示机", 1, page_break=True)
para(doc, "这台机器 CPU 较强（8 核 16 线程）但显卡不能用于 CUDA 训练（Radeon 集显 + 496MB 显存）。"
          "最优用法是**把它变成开发与演示服务器**：装 Docker 起依赖、跑后端与前端、外出时给评委演示。")
add_table(doc,
          ["环节", "做法", "注意"],
          [["系统与虚拟化", "同样启用 WSL2 + Ubuntu 24.04（BIOS 中打开 SVM 虚拟化）", "AMD 平台在 BIOS 中叫 SVM Mode"],
           ["Docker 内存分配", "Docker Desktop → Resources 建议分配 8—10GB", "16GB 物理内存要留一半给 Windows 与浏览器"],
           ["必装软件", "Git、VS Code、Python 3.12、Node + pnpm、Docker Desktop、MQTTX、Apifox、MobaXterm、OBS",
            "不需要装 PyTorch CUDA 环境；如确需推理，只装 CPU 版 onnxruntime"],
           ["承担的服务", "PostgreSQL、Redis、EMQX、MinIO、后端 API、前端构建产物 Nginx", "与台式机保持同一份 docker-compose 文件，配置差异只写在 .env"],
           ["演示用途", "把整套平台在本机跑起来，浏览器访问本地地址演示（不依赖网络）", "演示前用 OBS 录一遍完整流程作为备份"],
           ["代码角色", "作为第二开发机：前端、文档、接口调试为主", "训练与算法改动用台式机，避免两边环境不一致"]],
          [2.4, 7.4, 4.4], size=9)
note(doc, "可选优化：如果这台机器长期当演示服务器，建议装 Ubuntu 单系统或 Windows + Ubuntu 双系统，"
          "Docker 原生运行比 WSL2 更省内存；但若还要给学生日常使用，保持 Windows + WSL2 更稳妥。")

# ============================================================
h(doc, "4 笔记本 2（i5-7300HQ / GTX 1050 2GB）：客户端与设备联调机", 1, page_break=True)
add_table(doc,
          ["用途", "做法", "为什么适合"],
          [["多角色功能测试", "同时开多个浏览器（或隐私窗口）分别登录 学生/教师/家长/门卫/宿管 角色", "并发测试与权限验证最能暴露问题，笔记本 2 当作“客户端集群”"],
           ["前端开发与文档", "装 Git、VS Code、Node + pnpm 即可，不需要 Docker 与数据库", "资源占用低，适合课堂上随身使用"],
           ["设备联调", "装 MQTTX、串口工具、ONVIF Device Manager、厂商门禁调试工具", "现场接设备调试时，这台机器最适合带出去"],
           ["轻量推理验证", "如确需本地跑推理：装旧版 PyTorch（CUDA 11.x 组合）或用 CPU 版 onnxruntime 跑小模型",
            "GTX 1050 算力 6.1、显存 2GB，只适合验证流程，不能用于正式训练"],
           ["现场演示备机", "装好浏览器，直接访问笔记本 1 或云服务器地址", "不装服务端，减少现场故障面"]],
          [2.6, 6.6, 5.0], size=9)
note(doc, "提醒：GTX 1050 需要较旧的驱动与 CUDA 组合才能用（受计算能力限制），在新版 PyTorch 上很可能直接报错。"
          "不要在这台机器上折腾训练环境，时间成本远高于收益。")

# ============================================================
h(doc, "5 阿里云等公有云环境：业务中枢与对外发布", 1, page_break=True)
h(doc, "5.1 为什么云端只放业务、不放视频", 2)
para(doc, "这是本项目在云上最容易踩的坑：如果按“把摄像头全部接到云上”的思路做，按量带宽费用会迅速失控，"
          "而且学生人脸图像出校涉及合规风险。正确架构是：")
bullet(doc, "校内：摄像机 → NVR 本地录像（保留 30 天）；AI 边缘盒子本地分析，只上报“事件元数据 + 缩略图”。")
bullet(doc, "云端：接收事件、通行汇总、审批与通知、报表与驾驶舱、小程序 API。单条事件报文约 300KB（含 1 张截图），带宽压力可忽略。")
bullet(doc, "合规：原始人脸图与视频不出校园网；云端只保存脱敏后的必要信息，并在文档与同意书中明确告知。")

h(doc, "5.2 ECS 选型与配置建议", 2)
add_table(doc,
          ["项目", "起步配置（推荐先用）", "规模配置（学生团队 + 小程序上线后）", "说明"],
          [["实例规格", "2 核 4GB（经济型 e 或通用型 u1）", "4 核 8GB", "起步配置可跑通全流程；正式对师生开放前升级"],
           ["操作系统", "Ubuntu 24.04 LTS 64 位", "同左", "与 WSL、现场服务器统一，减少差异"],
           ["系统盘", "ESSD 40—60GB", "ESSD 100GB", "容器镜像与数据库都会占用空间"],
           ["带宽", "按使用流量计费（峰值 5—10Mbps）", "按量 + 峰值限速告警", "固定小带宽会在传文件、拉镜像时成为瓶颈"],
           ["安全组", "仅放行 22（限定本人 IP）、80、443", "同左并增加堡垒机或跳板策略", "数据库中端口严禁对公网开放"],
           ["快照与备份", "开启自动快照策略（每周 1 次）", "每日快照 + OSS 异地备份", "云上也要备份，删库事故一样会发生"],
           ["监控告警", "云监控：CPU、内存、磁盘、带宽阈值告警到手机", "同左 + 日志服务", "磁盘写满是最常见的线上故障"]],
          [2.0, 4.4, 4.4, 3.4], size=9)
note(doc, "成本参考（测算，以阿里云当期价格为准）：起步配置新用户首年通常数百元以内；"
          "规模配置按年约数千元；OSS 存储与流量另计。若同时启动多台实例，建议先到期后再决定是否续费升级。")

h(doc, "5.3 云端部署步骤（一次配好，之后只用脚本更新）", 2)
add_code(doc, [
    "# 1) 首次登录与基础加固",
    "ssh root@<公网IP>",
    "adduser deploy && usermod -aG sudo,docker deploy     # 用普通账号运维，禁用 root 直登",
    "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config",
    "sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config",
    "systemctl restart ssh        # 先把本机公钥传上去再执行，否则会被锁在外面",
    "",
    "# 2) 时间同步与语言环境（时间不准会导致通行记录错乱、JWT 校验失败）",
    "timedatectl set-timezone Asia/Shanghai && timedatectl status",
    "locale-gen zh_CN.UTF-8 en_US.UTF-8",
    "",
    "# 3) 安装 Docker（使用官方脚本或阿里云镜像源）",
    "curl -fsSL https://get.docker.com | sh",
    "docker --version && docker compose version",
    "",
    "# 4) 拉取代码并以生产配置启动",
    "git clone https://gitee.com/<你的仓库>/campus-platform.git /opt/campus",
    "cd /opt/campus && cp .env.example .env && vim .env      # 填入强口令与域名",
    "docker compose -f docker-compose.prod.yml up -d",
    "",
    "# 5) HTTPS（小程序与合规都要求 HTTPS）",
    "apt install -y nginx certbot python3-certbot-nginx",
    "certbot --nginx -d campus.example.com     # 证书自动续期由 certbot.timer 负责",
    "",
    "# 6) 自动备份（每日 2:00 备份数据库并上传 OSS）",
    "crontab -e",
    "0 2 * * * /opt/campus/scripts/backup.sh >> /var/log/campus-backup.log 2>&1",
])

h(doc, "5.4 本机与云端的协同方式", 2)
add_table(doc,
          ["协同事项", "推荐做法", "说明"],
          [["代码同步", "Gitee 作主仓库；本机 push，云端 pull 部署；重要版本打 tag", "禁止直接改云端代码"],
           ["配置差异", "本地与云端用同一份 compose，差异只写在各自 .env", "避免“本地能跑云端不能跑”"],
           ["数据库", "本地开发库可随容器重建；云端库每日备份到 OSS 并保留 30 天", "云端库禁止随意 drop"],
           ["设备回传通道", "MQTT over TLS（8883）或 VPN 隧道，仅允许设备网关出网到云端指定端口", "不要把 MQTT 1883 明文暴露到公网"],
           ["远程调试", "开发期用 frp 或 SSH 反向隧道临时暴露本机服务；正式环境关闭", "临时通道用完即关"],
           ["演示保障", "演示前在云端与本地各部署一份，网络异常时切换", "竞赛现场网络不可控，双份是底线"]],
          [2.4, 6.6, 5.4], size=9)

h(doc, "5.5 云端验收清单", 2)
add_table(doc,
          ["序号", "验收项", "通过标准"],
          [["1", "SSH 安全登录", "禁用口令与 root 直登，仅密钥可登"],
           ["2", "安全组最小开放", "仅 22/80/443 对公网开放；数据库与 MQTT 端口仅内网"],
           ["3", "容器全栈运行", "docker compose ps 全部 healthy"],
           ["4", "HTTPS 有效", "浏览器无证书警告，证书自动续期已配置"],
           ["5", "接口可访问", "https://域名/docs 正常，鉴权接口返回预期错误码"],
           ["6", "备份可恢复", "从 OSS 备份恢复一次到测试库，数据一致"],
           ["7", "监控告警", "手机能收到 CPU/磁盘/带宽阈值告警"],
           ["8", "时间与日志", "时间为北京时间，日志按天切割且保留 ≥30 天"],
           ["9", "设备接入验证", "一台模拟网关能通过 TLS 上报消息并被平台处理"]],
          [1.0, 4.4, 7.0], size=9, align_center_cols=(0,))

# ============================================================
h(doc, "6 学生机房标准化环境（批量、离线、可复制）", 1, page_break=True)
para(doc, "机房场景与个人电脑完全不同：机器多、无管理员权限的情况常见、外网可能被限制、学生走后环境容易被破坏。"
          "因此机房的准备目标是**批量部署 + 离线可用 + 一键还原**，而不是逐台手装。")
h(doc, "6.1 三种批量方案（按可用性从高到低选择）", 2)
add_table(doc,
          ["方案", "适用条件", "做法", "优点", "局限"],
          [["方案 A：机房同传系统", "机房装有联想/惠普/锐捷等品牌同传或还原卡系统",
            "在一台母盘机上装好全部环境 → 用同传系统把系统盘广播到所有机器", "最快、最省人力", "需要机房具备该系统与管理密码"],
           ["方案 B：系统镜像 + 克隆工具", "无同传系统，但可以自由装机",
            "母盘机装好后用 Clonezilla 或微 PE + Ghost 制作镜像，U 盘/网络分发", "兼容性好，不依赖品牌软件", "逐台恢复耗时，需统一硬件型号"],
           ["方案 C：脚本化安装（无人值守）", "不能重装系统、只有普通用户权限",
            "用 winget 或 Chocolatey 写 PowerShell 安装脚本；把安装包与 pip/npm 缓存放移动硬盘",
            "不动系统、可反复执行、留痕清晰", "个别软件需要管理员权限；耗时长"]],
          [2.6, 3.2, 4.6, 2.4, 2.6], size=8.5)

h(doc, "6.2 母盘机应装好的最小集合", 2)
para(doc, "机房机器的定位是“学生能写代码、能连开发服务器”，不是每台都跑全栈。因此母盘只装最小集合，数据库与中间件统一放在开发服务器或云端。")
add_table(doc,
          ["类别", "软件", "说明"],
          [["必备", "Git for Windows、VS Code（含 Python/Vue/中文语言包扩展）、Python 3.12、Node.js LTS + pnpm",
            "这四项是所有学生作业的基础"],
           ["必备", "DBeaver（或 pgAdmin）、Apifox、MQTTX", "连数据库、调接口、看设备消息"],
           ["必备", "MobaXterm 或 PuTTY + WinSCP、浏览器（Chrome/Edge）", "连 Linux 开发服务器、查看前端页面"],
           ["推荐", "WSL2 + Ubuntu（如机房允许虚拟化）", "与开发服务器命令一致，避免“Windows 命令对不上”"],
           ["推荐", "FFmpeg、VLC", "视频处理与流测试"],
           ["可选", "Docker Desktop", "只在机房配有 16GB 内存且允许虚拟化时装；否则引导连开发服务器"],
           ["可选", "Python 离线 wheels 目录 + pnpm store 目录", "断网机房也能装依赖"]],
          [1.6, 6.6, 6.0], size=9)
note(doc, "强烈建议：机房不要给每台机器装 PostgreSQL 与 Docker。原因有三——维护成本高、学生乱改密码导致互连失败、"
          "机房关机后服务全部消失（学生演示时数据丢失）。正确做法是：机房内指定 1—2 台机器或一台服务器集中承载依赖服务，学生机只作为客户端。")

h(doc, "6.3 离线包策略（断网机房的关键）", 2)
add_table(doc,
          ["离线包类别", "内容", "获取方式", "体积参考"],
          [["基础软件安装包", "Git、VS Code、Python、Node、DBeaver、MobaXterm 安装文件", "官网下载 Windows 版 exe/msi 后集中存放", "约 1.5—2 GB"],
           ["Python 依赖", "pip download 把后端与算法依赖下成 wheels 目录", "pip download -d wheels -r requirements.txt", "约 1—3 GB（含 torch 会更大）"],
           ["前端依赖", "pnpm fetch 或离线 store", "pnpm fetch 后整目录拷贝到学生机 PNPM_HOME/store", "约 300—800 MB"],
           ["VS Code 扩展", "VSIX 离线安装包", "vsce 或从市场页下载 .vsix，code --install-extension xxx.vsix", "约 200—500 MB"],
           ["容器镜像（如需要）", "docker save 导出的镜像 tar 包", "docker save postgres:16 redis:7-alpine emqx/emqx:5 minio/minio -o images.tar", "约 2—4 GB"],
           ["数据集与视频样本", "用于算法课的标注样本与测试视频", "从 ModelScope/Kaggle 下载后统一归档", "视规模而定"],
           ["文档与课件", "本套项目文档、操作手册、作业模板", "直接拷贝", "几十 MB"]],
          [2.4, 5.0, 5.4, 2.4], size=9)

h(doc, "6.4 机房脚本与还原策略", 2)
add_code(doc, [
    "# install-baseline.ps1 （机房批量安装脚本骨架，管理员 PowerShell 执行）",
    "$ErrorActionPreference = 'Stop'",
    "$pkgs = @('Git.Git','Microsoft.VisualStudioCode','Python.Python.3.12','OpenJS.NodeJS.LTS',",
    "          'dbeaver.dbeaver','MobaXterm.MobaXterm')",
    "foreach ($p in $pkgs) { winget install --id $p -e --accept-source-agreements --accept-package-agreements }",
    "",
    "# 配置镜像源与 UTF-8",
    "npm config set registry https://registry.npmmirror.com",
    "mkdir \"$env:APPDATA\\pip\" -Force",
    "Set-Content \"$env:APPDATA\\pip\\pip.ini\" \"[global]`nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple\"",
    "[System.Environment]::SetEnvironmentVariable('PYTHONUTF8','1','User')",
    "",
    "# 写入开发服务器地址，方便学生直接使用",
    "Set-Content \"$env:USERPROFILE\\.campus-dev\" 'DEV_HOST=192.168.1.10`nAPI=http://192.168.1.10:8000`nWEB=http://192.168.1.10:5173'",
])
bullet(doc, "还原策略：如果机房有还原卡，把母盘设为基础镜像，学生作业通过 Git 提交到 Gitee/GitLab，避免作业随还原丢失。")
bullet(doc, "无还原卡时：在教学盘（D 盘）保留一份“环境修复”脚本与离线包，出问题一键重装开发环境而不动系统。")
bullet(doc, "统一开发服务器：机房内指定一台机器（或一台塔式服务器）跑依赖服务，学生机通过 IP 访问，配置写入 .campus-dev 文件供脚本读取。")

# ============================================================
h(doc, "7 现场部署环境准备（学校机房/弱电间）", 1, page_break=True)
h(doc, "7.1 服务器与机房准备", 2)
add_table(doc,
          ["项目", "要求", "验收方法"],
          [["操作系统", "Ubuntu Server 24.04 LTS（与开发环境、云端同版本）", "cat /etc/os-release"],
           ["主机名与静态 IP", "主机名规范（如 campus-app-01）；IP 由学校网络管理员分配并固定", "ip a 与 ping 测试"],
           ["时间同步", "指向校内 NTP 或公网 NTP，偏差 ≤50ms", "timedatectl status；chronyc sources"],
           ["磁盘规划", "系统盘（SSD）与数据盘分离；数据盘挂 /data 并写入 /etc/fstab", "df -h；重启后自动挂载"],
           ["Docker 与编排", "Docker Engine + Compose v2；镜像加速或内网镜像仓库", "docker compose version"],
           ["防火墙", "ufw 仅放行必要端口；数据库与 MQTT 仅内网可达", "ufw status verbose"],
           ["BIOS 设置", "来电自启（AC Power Recovery）、开启虚拟化、关闭节能降频", "断电恢复测试"],
           ["机柜与供电", "UPS 保护服务器与核心交换机；标签化管理网线与电源", "断电演练一次"],
           ["带外管理", "如服务器支持 IPMI/iDRAC，配置管理口并记录地址", "独立网络下可访问"],
           ["运维账号", "每人独立账号 + sudo 授权，禁止共享 root；SSH 仅密钥登录", "登录审计记录"]],
          [2.4, 7.0, 5.0], size=9)

h(doc, "7.2 网络与设备接入准备（现场最容易卡住的环节）", 2)
add_table(doc,
          ["准备项", "具体内容", "负责人", "为什么关键"],
          [["VLAN 规划", "业务网 / 视频网 / 物联网与门禁网 三网隔离；跨网访问只在应用层开放必要端口",
            "学校网络管理员", "不隔离时视频广播会拖垮业务网，门禁设备也更容易被扫描攻击"],
           ["IP 地址台账", "为每台门禁、摄像机、NVR、传感器分配固定 IP 并登记（编号—位置—IP—MAC）",
            "项目组 + 弱电", "没有台账，后期排查一个离线设备要跑遍整栋楼"],
           ["协议开放确认", "采购前书面确认设备支持 GB/T 28181 或 ONVIF/RTSP、韦根或开放 SDK、Modbus/MQTT",
            "采购 + 厂商", "协议不开放是硬件对接最常见的死结，必须在合同里写明"],
           ["端口放行清单", "列出平台与设备互访所需端口（如 80/443/554/8000/1883/8883/37777 等）",
            "项目组", "现场网络策略严格，临时申请会拖慢联调"],
           ["带宽预留", "按 1080p 单路 2—4Mbps 估算并预留 30% 余量；AI 分析尽量在边缘完成",
            "网络管理员", "带宽不足会同时影响录像完整性与平台可用性"],
           ["设备间条件", "弱电间供电、接地、温度；边缘盒子与网关的安装位置与固定方式",
            "后勤 + 弱电", "边缘设备长期运行对散热与供电稳定性敏感"],
           ["厂商技术对接人", "记录每类设备厂商的对接人与联系方式，建立问题升级路径",
            "采购", "现场卡住时能不能当天解决，取决于有没有对口人"],
           ["施工窗口", "避开上课与考试时段；涉及断电与断网的作业提前报备",
            "学校", "校园施工最大的风险是影响正常教学秩序"]],
          [2.2, 6.4, 2.4, 3.2], size=8.5)

h(doc, "7.3 现场部署包（提前做好，现场不联网也能装完）", 2)
add_table(doc,
          ["内容", "制作方式", "用途"],
          [["操作系统安装盘", "Ubuntu Server 24.04 ISO + 启动 U 盘", "服务器裸装"],
           ["离线依赖仓库", "本地 apt 镜像（apt-mirror）或 deb 包目录 + Docker 镜像 tar", "无外网环境安装"],
           ["应用交付包", "docker compose 文件 + 应用镜像 + .env 模板 + 初始化 SQL", "一条命令起平台"],
           ["初始化脚本", "建库建表、创建管理员、导入基础数据（组织、场所、设备台账）", "缩短现场调试时间"],
           ["配置模板", "nginx、证书、定时备份、日志切割、监控采集配置", "现场只改域名与口令"],
           ["验收与培训材料", "部署手册、运维手册、故障处理手册、三类培训课件", "验收与知识转移"],
           ["回滚方案", "上一版本镜像与数据库备份 + 回滚脚本", "升级失败 15 分钟内可退回"]],
          [2.4, 6.6, 5.2], size=9)

h(doc, "7.4 现场部署与上线验收", 2)
add_table(doc,
          ["序号", "验收项", "通过标准"],
          [["1", "平台服务全起", "docker compose ps 全部 healthy，重启服务器后自动恢复"],
           ["2", "数据库连通与初始化", "基础数据（组织、场所、人员、设备）导入完成，无重复无遗漏"],
           ["3", "门禁联调", "现场刷卡/刷脸通行 P95 ≤300ms；断网 30 分钟仍可放行且记录完整补传"],
           ["4", "视频接入", "按点位清单逐个确认画面与录像；平台预览延时 ≤1.5 秒"],
           ["5", "AI 算法", "按验收样本测试，准确率与误报率达标（详见需求规格说明书 10.3 节）"],
           ["6", "通知通道", "短信/微信通知真实送达并记录回执"],
           ["7", "定时任务", "归寝判定、报表生成、数据备份按计划执行并留痕"],
           ["8", "备份恢复演练", "从备份恢复到测试环境，RPO ≤15 分钟、RTO ≤2 小时"],
           ["9", "培训完成", "管理员、班主任、门卫宿管三类角色各完成一次实操培训并签到"],
           ["10", "文档移交", "部署手册、运维手册、账号清单、设备台账、IP 表全部移交"]],
          [1.0, 3.6, 7.8], size=9, align_center_cols=(0,))

# ============================================================
h(doc, "8 环境验收总表与常见问题", 1, page_break=True)
h(doc, "8.1 三类环境对照表", 2)
add_table(doc,
          ["对照项", "开发机（台式机）", "云服务器", "现场服务器"],
          [["定位", "训练 + 全栈开发", "业务中枢 + 对外发布", "校内生产运行"],
           ["操作系统", "Windows 11 + WSL2 Ubuntu 24.04", "Ubuntu 24.04 LTS", "Ubuntu Server 24.04 LTS"],
           ["GPU", "RTX 3050（训练与推理）", "无", "无（AI 在边缘盒子）"],
           ["数据库", "容器 PostgreSQL（可随删随建）", "容器 PostgreSQL + 每日备份", "容器 PostgreSQL + 主备 + 定时备份"],
           ["数据", "测试数据，可重置", "真实业务数据 + 脱敏事件数据", "真实业务数据（含人脸模板，本地存储）"],
           ["视频", "伪流（FFmpeg/MediaMTX）", "不接视频，仅收事件与缩略图", "NVR 本地录像 + 边缘 AI 分析"],
           ["HTTPS", "不需要", "必须（小程序与合规）", "建议（校内可用自签或内网证书）"],
           ["备份", "Git 提交即可", "每日快照 + OSS", "每日备份 + 离线介质"],
           ["上线顺序", "先跑通", "再对外", "最后进校"]],
          [2.0, 4.4, 4.4, 4.4], size=9)

h(doc, "8.2 高频问题与解决（都是实际会遇到的）", 2)
add_table(doc,
          ["现象", "常见原因", "解决办法"],
          [["pip 安装超时或报 SSL 错误", "未配国内镜像，或公司/学校网络有代理",
            "配置清华/阿里源；必要时设置 HTTPS_PROXY；用 uv 替代 pip 提升速度"],
           ["npm install 卡住或依赖报错", "源为官方源或 Node 版本不匹配",
            "切 npmmirror；删掉 node_modules 与 lock 文件重装；统一 Node LTS 版本"],
           ["Docker 拉镜像失败/超时", "无镜像加速或加速地址失效",
            "使用阿里云 ACR 专属加速地址；必要时 docker save/load 离线导入镜像"],
           ["WSL2 启动失败", "BIOS 未开虚拟化，或与其他虚拟化软件（VMware/Hyper-V）冲突",
            "开 VT-x/SVM；关闭冲突的虚拟化组件；wsl --update 升级内核"],
           ["容器里的服务本机连不上", "端口未映射，或 Windows 防火墙拦截",
            "检查 compose 的 ports 映射；在防火墙中放行对应端口；确认服务监听 0.0.0.0"],
           ["中文乱码 / Python 输出报错", "编码不一致（GBK 与 UTF-8）",
            "设置 PYTHONUTF8=1；终端使用 Windows Terminal；文件统一保存为 UTF-8"],
           ["训练报 CUDA out of memory", "显卡显存不足（3050 为 8GB）",
            "降低 imgsz 与 batch；开启 AMP 混合精度；关闭其他占用显存的程序；必要时改用更小模型"],
           ["GTX 1050 装 PyTorch 报错", "计算能力与新版 CUDA 不兼容",
            "改用旧版组合（CUDA 11.x）或直接放弃在该机训练，仅做 CPU 推理"],
           ["ONNX 推理结果与 PyTorch 不一致", "opset、输入尺寸或预处理不一致",
            "统一 opset（建议 17）与归一化参数；导出后做逐张对比，偏差应 ≤1e-3"],
           ["数据库时间与北京时间差 8 小时", "容器未设时区", "compose 中设置 TZ=Asia/Shanghai，数据库连接参数统一时区"],
           ["演示现场网络不通", "依赖外网或校园网",
            "本地全栈部署 + 提前录屏；准备移动热点；关键页面使用本地静态资源"],
           ["机房学生乱改配置导致连不上开发服务器", "共享账号与共享数据库",
            "每人独立账号与独立 schema；数据库口令由教师统一管理；提供一键修复脚本"]],
          [3.0, 4.4, 6.8], size=8.5)

h(doc, "8.3 30 天环境准备路线", 2)
add_table(doc,
          ["周次", "任务", "产出"],
          [["第 1 周", "台式机装 Windows 基础工具链 + WSL2 + Docker；配置全部镜像源；申请云账号与 ECS",
            "主力机可跑后端与前端；云服务器可登录"],
           ["第 2 周", "台式机装 AI 训练环境并跑通一次最小训练与 ONNX 导出；搭建伪视频与 MQTT 模拟环境",
            "算法链路打通，不依赖真实硬件即可开发"],
           ["第 3 周", "笔记本 1 配成演示服务器；笔记本 2 配成客户端；仓库规范与分支策略落地；代码首次入库",
            "三机分工明确，代码可同步"],
           ["第 4 周", "云端部署业务侧（数据库、API、HTTPS、备份与监控）；制作机房离线包与安装脚本",
            "云端可对外访问；机房具备批量部署条件"],
           ["第 5 周（衔接）", "现场勘察：VLAN、IP 台账、设备协议与端口确认；输出部署包与回滚方案",
            "现场部署条件具备，可启动 M2 门禁联调"]],
          [1.8, 8.4, 4.2], size=9, align_center_cols=(0,))

# ============================================================
h(doc, "9 附：一条命令验证整套环境", 1, page_break=True)
para(doc, "把下面这段脚本保存为 check-env.py，在任意机器上运行，可一次性检查本机环境是否满足开发要求，"
          "输出“通过/缺失”清单，便于装机后自检与机房批量核查。")
add_code(doc, [
    "# check-env.py —— 环境自检脚本（无第三方依赖即可运行）",
    "import importlib.util, platform, shutil, socket, subprocess, sys",
    "",
    "def has(cmd):",
    "    return shutil.which(cmd) is not None",
    "",
    "def run(cmd):",
    "    try:",
    "        return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=20).stdout.strip()",
    "    except Exception as e:",
    "        return f'ERROR: {e}'",
    "",
    "def port_open(host, port):",
    "    s = socket.socket(); s.settimeout(1.5)",
    "    try:",
    "        s.connect((host, port)); return True",
    "    except Exception:",
    "        return False",
    "    finally:",
    "        s.close()",
    "",
    "checks = [",
    "    ('Python', has('python') or has('python3'), (has('python') and run('python --version')) or run('python3 --version')),",
    "    ('Node.js', has('node'), run('node -v')),",
    "    ('pnpm', has('pnpm'), run('pnpm -v')),",
    "    ('Git', has('git'), run('git --version')),",
    "    ('Docker', has('docker'), run('docker --version')),",
    "    ('ffmpeg', has('ffmpeg'), run('ffmpeg -version | head -1')),",
    "]",
    "for name, ok, detail in checks:",
    "    print(f\"[{'OK ' if ok else 'MISS'}] {name:<10} {detail}\")",
    "",
    "print('\\n-- GPU --')",
    "print(run('nvidia-smi --query-gpu=name,memory.total --format=csv,noheader') or '未检测到 NVIDIA GPU（训练需在带 CUDA 的机器上进行）')",
    "try:",
    "    import torch",
    "    print('torch', torch.__version__, 'cuda_available=', torch.cuda.is_available())",
    "except Exception:",
    "    print('未安装 PyTorch（仅算法机需要）')",
    "",
    "print('\\n-- 依赖服务端口 --')",
    "for p, label in [(5432,'PostgreSQL'),(6379,'Redis'),(1883,'MQTT'),(9000,'MinIO'),(8000,'后端API'),(5173,'前端')]:",
    "    print(f\"  {label:<12} {'OPEN' if port_open('127.0.0.1', p) else 'closed'}\")",
    "",
    "print('\\n-- 网络与镜像 --')",
    "print(' pip 源 :', run('pip config get global.index-url') or '未配置（建议配置清华源）')",
    "print(' npm 源 :', run('npm config get registry') or '未配置（建议配置 npmmirror）')",
    "print('\\n系统:', platform.platform())",
])
para(doc, "使用方式：在开发机上执行 python check-env.py；在机房批量核查时，把脚本与 Python 便携版一起放移动硬盘，"
          "逐台运行并收集输出即可形成环境台账。")

doc.save(OUT)
print("已生成:", OUT)
