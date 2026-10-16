# -*- coding: utf-8 -*-
"""生成《电脑环境配置详细方案（可执行版）》
分两部分写入同一文件：本文件为第一部分。
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_kit import *
from docx_kit import _font
from docx import Document
from docx.shared import Pt, Cm

OUT = r"F:\职业中专\大赛\智慧园区创意\项目文档\09_电脑环境配置详细方案.docx"
SCRIPT_DIR = r"F:\职业中专\大赛\智慧园区创意\环境工具\scripts"


def step(doc, no, title, why, ops, expect, verify):
    """一个标准操作步骤：目的 → 操作 → 预期 → 校验。"""
    h(doc, f"{no} {title}", 3)
    para(doc, f"目的：{why}", size=10)
    para(doc, "操作步骤：", indent=False, bold=True, space_after=2)
    for i, op in enumerate(ops, start=1):
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


doc = Document()
setup(doc, "电脑环境配置详细方案 V1.0")
cover(doc,
      "“智园卫士”智慧校园管理平台",
      "电脑环境配置详细方案（可执行版）— 依据总体技术架构方案 V1.0 选型",
      [("文档名称", "电脑环境配置详细方案（可执行版）"),
       ("文档编号", "ZYWS-ENV-2026-002"),
       ("版本号", "V1.0"),
       ("编制单位", "齐河县职业中等专业学校 项目组"),
       ("编制依据", "《总体技术架构方案》V1.0 第 7 章关键技术选型、第 8 章 AI 视觉能力设计、第 5 章部署架构"),
       ("适用对象", "台式机（主力开发机）、笔记本 1（服务宿主）、笔记本 2（客户端）、阿里云 ECS、学生机房、现场服务器"),
       ("使用方式", "按第 1 章顺序逐节执行；每个步骤均含命令、预期结果与校验方法，校验未通过不得进入下一步"),
       ("配套文件", "《环境准备与选型核对表》xlsx（进度勾选）、环境工具/scripts/install-base.ps1、环境工具/scripts/check-env.py"),
       ("编制日期", "2026 年 11 月"),
       ("密级", "内部")],
      doc_kind="电 脑 环 境 配 置 详 细 方 案")

doc.add_page_break()
h(doc, "修订记录", 1)
add_table(doc, ["版本", "日期", "修订内容", "编制人", "审核"],
          [["V0.5", "2026-11-20", "依据总体技术架构方案 V1.0 确定技术栈与机器分工", "项目组", "指导教师"],
           ["V0.9", "2026-11-26", "补充逐步命令、预期结果与校验方法，形成可执行步骤", "项目组", "指导教师"],
           ["V1.0", "2026-11-28", "全文评审通过，作为环境构建与验收的执行基线", "项目组", "学校信息中心"]],
          [1.6, 2.2, 8.0, 2.0, 2.0], size=9, align_center_cols=(0, 1, 3, 4))
note(doc, "本方案的所有技术选型与《总体技术架构方案》V1.0 保持一致；若架构方案发生变更，本方案需同步修订并更新版本号。")

# ============================================================
h(doc, "第 1 章 环境配置总览", 1, page_break=True)
h(doc, "1.1 本方案的定位与使用方法", 2)
para(doc, "本方案是环境构建的唯一执行依据：从一台空白电脑开始，按章节顺序操作，即可得到可用于本项目开发、演示与部署的完整环境。"
          "每个配置项都按“目的 → 操作步骤 → 预期结果 → 校验”四段式编写，校验命令的通过标准明确，未通过不得继续。")
add_table(doc, ["你要做什么", "看哪一章", "预计耗时", "完成标志"],
          [["先把所有机器的基础环境装好", "第 2 章（通用基线）", "每台 1—2 h", "13 项基础校验全绿"],
           ["配置台式机（主力开发机）", "第 3 章", "1—2 个工作日", "25 项验收清单全绿，能训练能联调"],
           ["配置笔记本 1（演示服务器）", "第 4 章", "3—4 h", "整套平台可在本机离线运行并演示"],
           ["配置笔记本 2（客户端）", "第 5 章", "1—2 h", "多角色测试与设备联调可用"],
           ["配置阿里云 ECS", "第 6 章", "2—3 h", "HTTPS 可访问、备份可恢复"],
           ["配置学生机房（批量）", "第 7 章", "1—2 个工作日", "批量部署 + 离线可用 + 可还原"],
           ["配置现场服务器（校内上线）", "第 8 章", "按现场条件", "现场验收 10 项全过"],
           ["一次性把整体跑通并自检", "第 9 章", "2—4 h", "check-env.py 通过率 100%"]],
          [4.6, 2.4, 2.4, 5.6], size=9, align_center_cols=(0, 2))

h(doc, "1.2 机器分工与选型对应关系", 2)
para(doc, "三台电脑的能力差异决定了它们不能装成一样的环境。下表是本项目的正式分工，请严格按此执行。")
add_table(doc, ["机器", "实际配置", "环境定位", "按架构方案需要安装的核心组件"],
          [["台式机\n（主力机）", "i5-13400F / 16GB（建议升 32GB）/ RTX 3050 8GB / Windows 11",
            "AI 训练 + 全栈开发 + Docker 依赖服务 + 边缘推理验证",
            "Python 3.11+、FastAPI+Uvicorn、PyTorch 2.x+CUDA 12、Ultralytics、ONNX Runtime、Vue3+Vite+Element Plus+ECharts、Docker Compose（PG16+pgvector/Redis7/EMQX5/MinIO/TDengine）、Nginx"],
           ["笔记本 1", "Ryzen 7 5800U / 16GB / 集显 / Windows 11",
            "服务宿主与演示机（离线演示、评委现场演示）",
            "Docker Compose 全栈（PG16+pgvector/Redis7/EMQX5/MinIO）、后端运行环境、前端构建产物 + Nginx、Prometheus+Grafana（可选）"],
           ["笔记本 2", "i5-7300HQ / 16GB / GTX 1050 2GB / Windows 10/11",
            "客户端与设备联调（多角色测试、串口/网口调试）",
            "Git、VS Code、Node LTS + pnpm、MQTTX、Apifox、串口工具、ONVIF Device Manager、浏览器（不装 Docker 与训练环境）"],
           ["阿里云 ECS", "Ubuntu 24.04 LTS / 2 核 4G 起（可升 4 核 8G）",
            "业务中枢与对外发布（API、数据库、报表、小程序后端）",
            "Docker Engine + Compose v2、PostgreSQL 16、Redis 7、EMQX（TLS 8883）、MinIO 或 OSS、Nginx + Certbot、Prometheus（可选）"],
           ["学生机房", "统一母盘（Win10/11）+ 集中开发服务器",
            "教学与学生开发（客户端模式，依赖服务集中部署）",
            "Git、VS Code、Python 3.12、Node LTS + pnpm、DBeaver、Apifox、MQTTX；集中一台机器跑 Docker 依赖服务"],
           ["现场服务器", "Ubuntu Server 24.04 LTS / 16 核 32 线程 / 64GB / 双千兆",
            "校内生产运行（门禁、视频、事件、审批真实业务）",
            "Docker Compose 生产编排、PG16（主备规划）、Redis7、EMQX5、MinIO、TDengine、Nginx、备份脚本、监控"]],
          [2.0, 3.6, 3.6, 6.0], size=8.5)

h(doc, "1.3 技术栈锁定表（严格照此版本，不自行替换）", 2)
para(doc, "下表逐项对应《总体技术架构方案》V1.0 第 7 章“竞赛版”推荐选型。安装时按“锁定版本”列执行；如遇版本更新，"
          "保持主版本号不变（例如 PostgreSQL 16.x），并在环境报告中记录实际版本。")
add_table(doc, ["层次", "技术域", "锁定选型（架构方案竞赛版）", "安装位置", "关键配置点"],
          [["后端", "语言与框架", "Python 3.11+ / FastAPI + Uvicorn（单机多 Worker）", "台式机、笔记本1、云、现场", "异步、自动生成 OpenAPI 文档"],
           ["后端", "数据访问", "SQLAlchemy 2.x（异步）+ Alembic + asyncpg", "同上", "迁移脚本纳入版本管理"],
           ["后端", "配置与校验", "Pydantic v2 + pydantic-settings", "同上", ".env 读取，密钥不入库"],
           ["前端", "框架与构建", "Vue3 + Vite + TypeScript", "全部机器", "/api 代理到后端 8000"],
           ["前端", "UI 与图表", "Element Plus + ECharts（+ Pinia + Vue Router）", "全部机器", "自研 1920×1080 栅格缩放"],
           ["移动端", "小程序", "uni-app（Vue3 语法）", "台式机、笔记本1", "小程序 appid 与域名白名单"],
           ["数据", "关系库", "PostgreSQL 16（+ pgvector 扩展）", "台式机、笔记本1、云、现场", "向量维度与模型输出一致（512 维）"],
           ["数据", "时序库", "TDengine 单机（V2 阶段启用）", "台式机、现场", "taosAdapter REST 端口 6041"],
           ["数据", "缓存", "Redis 7（单实例 + AOF）", "台式机、笔记本1、云、现场", "设置密码，开启 AOF 持久化"],
           ["数据", "对象存储", "MinIO 单节点", "台式机、笔记本1、云、现场", "私有桶 + 强密钥 + 生命周期"],
           ["消息", "IoT 接入", "EMQX 5 开源版（+ Redis Stream 做业务异步）", "台式机、笔记本1、云、现场", "1883/8083/18083，改默认密码"],
           ["AI", "训练", "PyTorch 2.x + CUDA 12 + Ultralytics（YOLOv8n/s）", "台式机（仅此一台）", "独立虚拟环境，不与其他依赖混装"],
           ["AI", "推理", "ONNX Runtime（CPU/单 GPU），模型导出 opset 17", "台式机、边缘盒子", "与 PyTorch 结果偏差 ≤1e-3"],
           ["AI", "向量检索", "pgvector（人脸底库 ≤5 万）", "随 PostgreSQL 一并部署", "ivfflat 索引，维度与特征模型一致"],
           ["运行", "容器与编排", "Docker Compose（一键起全栈）", "台式机、笔记本1、云、现场", "数据卷持久化 + 健康检查"],
           ["运行", "网关", "Nginx（反向代理 + 静态资源 + 限流）", "笔记本1、云、现场", "HTTPS 终止、gzip、静态缓存"],
           ["运行", "监控", "Prometheus + Grafana（单机）", "云、现场（可选，先用 check-env.py）", "核心服务与端口存活监控"]],
          [1.4, 2.0, 5.4, 3.0, 3.6], size=8.5, align_center_cols=(0, 1))

h(doc, "1.4 配置实施顺序（跨机器）", 2)
para(doc, "环境构建不是逐台装完再下一台，而是按依赖关系推进：先通底座，再通数据，最后通应用。推荐按下表顺序执行，"
          "每完成一行在《环境准备与选型核对表》中勾选。")
add_table(doc, ["顺序", "任务", "在哪台机器", "前置条件", "产出"],
          [["①", "通用基线环境（第 2 章）", "三台 Windows 机器", "可联网、有管理员权限", "基础工具链与镜像源就绪"],
           ["②", "WSL2 + Ubuntu 24.04", "台式机、笔记本 1", "BIOS 已开启虚拟化", "可用的 Linux 环境"],
           ["③", "Docker Desktop + 依赖服务全栈", "台式机、笔记本 1", "WSL2 就绪", "PG/Redis/EMQX/MinIO 一条命令起"],
           ["④", "后端开发环境 + 首个接口", "台式机", "③ 完成", "访问 /docs 可见 Swagger"],
           ["⑤", "AI 训练环境 + 最小训练 + ONNX 导出", "台式机", "NVIDIA 驱动已装", "训练出权重并导出 ONNX"],
           ["⑥", "前端开发环境 + 页面联调", "台式机", "④ 完成", "页面可调用后端接口"],
           ["⑦", "设备模拟环境（伪视频 + MQTT）", "台式机、笔记本 1", "③ 完成", "无真实硬件也能跑通采集→分析→告警"],
           ["⑧", "云服务器环境与 HTTPS", "阿里云 ECS", "域名与备案就绪", "外网可访问 API"],
           ["⑨", "机房批量环境", "学生机房", "母盘机完成", "批量部署 + 离线包"],
           ["⑩", "现场部署环境", "校内服务器", "硬件与网络就绪", "真实业务上线"],
           ["⑪", "整体自检与验收（第 9 章）", "全部", "①—⑩ 完成", "check-env.py 通过率 100%"]],
          [1.0, 4.6, 3.4, 3.2, 4.0], size=8.5, align_center_cols=(0,))

h(doc, "1.5 使用约定与安全红线", 2)
bullet(doc, "命令约定：以 PS> 开头表示 Windows PowerShell（管理员）；以 $ 开头表示 WSL/Linux 终端；以 C:\\ 或 ~/ 开头的路径按提示区分系统。")
bullet(doc, "口令约定：所有服务口令统一使用强口令（12 位以上，含大小写、数字、符号），集中记录在密码管理表；禁止使用 123456、postgres 等默认口令。")
bullet(doc, "密钥红线：任何口令、密钥、令牌只能存放在 .env 文件或系统环境变量中，禁止写入代码、文档、截图与聊天记录；.env 必须加入 .gitignore。")
bullet(doc, "数据红线：人脸模板与人脸原图只允许保存在校内设备与本地开发机，禁止上传公有云、网盘或第三方平台；测试阶段使用合成的假人脸数据。")
bullet(doc, "网络红线：数据库（5432）、Redis（6379）、MQTT（1883）端口禁止对公网开放；云端只放行 22（限定来源）、80、443。")
bullet(doc, "变更约定：如需替换架构方案中的选型（例如改用 MySQL），必须先更新《总体技术架构方案》并说明理由，不得在环境层面私自替换。")

# ============================================================
h(doc, "第 2 章 通用基线环境（三台 Windows 机器都要做）", 1, page_break=True)
para(doc, "本章内容三台 Windows 电脑都要执行。完成本章后，每台机器都具备统一的基础工具链、编码环境与镜像源，"
          "后续章节只在此基础上追加各自特有的组件。建议直接运行配套脚本完成大部分工作，再按步骤手工补齐。")

h(doc, "2.1 机器信息登记与前置检查", 2)
step(doc, "2.1.1", "登记机器信息并确认硬件条件",
     "建立机器档案，后续排查问题时能快速定位是哪台机器、什么配置。",
     ["记录：计算机名、CPU、内存、显卡型号、系统版本、磁盘分区可用空间。",
      ("code", ["# 在 PowerShell 中执行，输出即机器档案",
                "systeminfo | Select-String 'OS 名称','OS 版本','系统型号','总物理内存'",
                "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors",
                "Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion",
                "Get-PSDrive -PSProvider FileSystem | Select-Object Name,@{n='可用GB';e={[math]::Round($_.Free/1GB,1)}}"]),
      "把结果填入《环境准备与选型核对表》的“机器分工”工作表。"],
     ["系统为 Windows 10 21H2 以上或 Windows 11；",
      "磁盘可用空间：台式机 C 盘 ≥60GB、D 盘 ≥150GB；笔记本 1 C 盘 ≥60GB；笔记本 2 C 盘 ≥40GB。"],
     ["# 校验：磁盘与内存是否满足",
      "Get-CimInstance Win32_ComputerSystem | Select-Object @{n='内存GB';e={[math]::Round($_.TotalPhysicalMemory/1GB,0)}}",
      "# 内存 GB 应为 16（台式机与两台笔记本）；若为 8GB，需先加内存再继续"])

step(doc, "2.1.2", "开启 CPU 虚拟化（WSL2 与 Docker 的硬前提）",
     "WSL2 与 Docker Desktop 依赖硬件虚拟化，未开启则第 3、4 章无法进行。",
     ["重启电脑进入 BIOS/UEFI（开机按 Del/F2/F10，按主板品牌而定）；",
      "Intel 平台开启 Intel Virtualization Technology（VT-x）、VT-d（如有）；AMD 平台开启 SVM Mode；",
      "保存退出（F10）后回到 Windows。"],
     ["系统信息中“虚拟化：已启用”"],
     ["# 校验：返回 True 表示已启用",
      "(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled",
      "# 另可查看任务管理器 → 性能 → CPU → 虚拟化：应为“已启用”"])

step(doc, "2.1.3", "系统准备：更新、时间、电源、长路径",
     "避免因系统补丁缺失、时间不同步、休眠断网、路径过长导致的后续诡异故障。",
     ["执行 Windows Update 至最新（至少安装所有关键更新）；",
      "确认时区为“(UTC+08:00) 北京，重庆，香港特别行政区，乌鲁木齐”并开启自动同步；",
      "电源计划设为“高性能”，关闭硬盘与网卡节能、关闭自动休眠（服务器与演示机尤其重要）；",
      "启用 NTFS 长路径支持（Node 与 Python 嵌套目录容易超长）。"],
     ["无待安装的关键更新；时间与国家授时中心一致；插电状态下不休眠；长路径已启用。"],
     ["# 校验：时间与电源",
      "Get-TimeZone | Select-Object Id,DisplayName",
      "powercfg /getactivescheme",
      "# 校验：长路径（返回 1 表示已启用）",
      "(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem').LongPathsEnabled"])

h(doc, "2.2 安装基础软件（winget 批量）", 2)
step(doc, "2.2.1", "确认 winget 可用",
     "winget 是 Windows 官方包管理器，可一条命令安装后续所有软件，避免逐个下载安装包。",
     ["打开“Microsoft Store”，搜索并安装或更新“应用安装程序（App Installer）”；",
      "打开 PowerShell 7（管理员），执行下方校验命令。"],
     ["能输出版本号"],
     ["winget --version",
      "# 若提示找不到命令：从 https://aka.ms/getwinget 下载安装，或改用第 7 章离线包手工安装"])

step(doc, "2.2.2", "按机器角色批量安装基础软件",
     "一次装齐全部基础工具，并保证三台机器版本一致（避免“我这里能跑”）。",
     ["确认当前是管理员 PowerShell；",
      "台式机（dev）执行全量安装；笔记本 1（server）与笔记本 2（client）按需安装；",
      "安装过程中若弹出 UAC 或重启提示，按提示处理后再继续。"],
     ["各软件安装成功，命令可执行。"],
     ["# 角色一：台式机（主力机，全量）",
      "winget install --id Git.Git -e",
      "winget install --id Microsoft.VisualStudioCode -e",
      "winget install --id Microsoft.PowerShell -e",
      "winget install --id Microsoft.WindowsTerminal -e",
      "winget install --id Python.Python.3.11 -e",
      "winget install --id Python.Python.3.12 -e",
      "winget install --id OpenJS.NodeJS.LTS -e",
      "winget install --id Docker.DockerDesktop -e",
      "winget install --id dbeaver.dbeaver -e",
      "winget install --id OBSProject.OBSStudio -e",
      "",
      "# 角色二：笔记本 1（服务宿主与演示机）",
      "winget install --id Git.Git -e",
      "winget install --id Microsoft.VisualStudioCode -e",
      "winget install --id Microsoft.PowerShell -e",
      "winget install --id Microsoft.WindowsTerminal -e",
      "winget install --id Python.Python.3.12 -e",
      "winget install --id OpenJS.NodeJS.LTS -e",
      "winget install --id Docker.DockerDesktop -e",
      "winget install --id dbeaver.dbeaver -e",
      "",
      "# 角色三：笔记本 2（客户端与设备联调）",
      "winget install --id Git.Git -e",
      "winget install --id Microsoft.VisualStudioCode -e",
      "winget install --id OpenJS.NodeJS.LTS -e",
      "",
      "# 校验：版本是否都就绪（重开一个终端窗口后执行）",
      "git --version; python --version; node -v; docker --version"])

step(doc, "2.2.3", "安装图形化辅助工具（按机器需要）",
     "部分工具不便于用 winget 安装，需手工下载，这些是设备联调与接口调试的必备工具。",
     ["MQTTX（MQTT 调试）：https://mqttx.app 下载 Windows 版；",
      "Apifox 或 Postman（接口调试）：官网下载；",
      "MobaXterm（SSH 运维）：https://mobaxterm.mobatek.net 下载 Home Edition；",
      "SSCOM / XCOM（串口调试）：用于 RS-485/Modbus 设备，仅笔记本 2 需要；",
      "ONVIF Device Manager（摄像机发现）：GitHub 下载，仅笔记本 2 需要；",
      "Wireshark（抓包）：仅台式机与笔记本 2 需要。"],
     ["各工具可正常启动。"],
     ["# 校验：MQTT 客户端能否启动（可选，图形界面手工确认）",
      "Get-Command MQTTX -ErrorAction SilentlyContinue"])

h(doc, "2.3 统一编码与语言环境", 2)
step(doc, "2.3.1", "设置 UTF-8 与 Python 编码环境变量",
     "中文 Windows 默认使用 GBK，会导致 Python 输出乱码、脚本报 UnicodeEncodeError、日志不可读。",
     ["设置系统区域使用 UTF-8（控制面板 → 区域 → 管理 → 更改系统区域设置 → 勾选 Beta 版 UTF-8）；",
      "设置用户环境变量 PYTHONUTF8 与 PYTHONIOENCODING；",
      "重启电脑使区域设置全局生效。"],
     ["PowerShell 中执行 chcp 显示 65001；Python 打印中文不乱码。"],
     ["# 校验：编码设置",
      "chcp",
      "$env:PYTHONUTF8; [Environment]::GetEnvironmentVariable('PYTHONUTF8','User')",
      "python -c \"print('中文编码测试：智慧园区平台')\"",
      "# 输出应为：中文编码测试：智慧园区平台（无乱码、无报错）"])

step(doc, "2.3.2", "安装中文字体与终端配置（可选但建议）",
     "保证大屏与文档渲染一致，避免字体缺失导致图表中文显示为方框。",
     ["确认系统已安装微软雅黑（Windows 默认已有）；",
      "Windows Terminal 设置为默认终端；",
      "在 Windows Terminal 中设置字体为 Consolas 或 Cascadia Mono（代码可读性更好）。"],
     ["终端中文与代码显示正常。"],
     ["# 校验：确认字体存在",
      "Get-ChildItem C:\\Windows\\Fonts -Filter 'msyh*' | Select-Object Name"])

h(doc, "2.4 配置国内镜像源（关键，先做这一步）", 2)
step(doc, "2.4.1", "配置 pip 清华源",
     "国内直连 PyPI 极慢或超时，不配镜像会导致依赖安装反复失败，浪费大量时间。",
     ["创建 %APPDATA%\\pip 目录；", "写入 pip.ini 配置文件（内容见下）。"],
     ["pip config list 能显示 index-url。"],
     ["# 创建配置目录并写入文件",
      "mkdir \"$env:APPDATA\\pip\" -Force",
      "notepad \"$env:APPDATA\\pip\\pip.ini\"",
      "",
      "# 文件内容：",
      "[global]",
      "index-url = https://pypi.tuna.tsinghua.edu.cn/simple",
      "trusted-host = pypi.tuna.tsinghua.edu.cn",
      "timeout = 60",
      "",
      "# 校验：",
      "pip config list",
      "pip install --upgrade pip            # 观察是否使用清华源且速度快"])

step(doc, "2.4.2", "配置 npm 淘宝源",
     "默认 npm 源在国内安装依赖经常卡住。",
     ["设置 npm registry 为 npmmirror；", "延长超时时间。"],
     ["npm config get registry 返回 npmmirror 地址。"],
     ["npm config set registry https://registry.npmmirror.com",
      "npm config set fetch-timeout 120000",
      "",
      "# 校验：",
      "npm config get registry",
      "# 期望输出：https://registry.npmmirror.com"])

step(doc, "2.4.3", "配置 Docker 镜像加速（安装 Docker 后再执行）",
     "默认从 Docker Hub 拉镜像在国内常常超时。注意：网上流传的公共加速地址大多已失效，"
     "正确做法是使用自己阿里云账号的专属加速地址。",
     ["登录阿里云控制台 → 容器镜像服务 ACR → 镜像工具 → 镜像加速器；",
      "复制属于你账号的专属加速地址（形如 https://xxxx.mirror.aliyuncs.com）；",
      "打开 Docker Desktop → Settings → Docker Engine，把地址加入 registry-mirrors 数组；",
      "点击 Apply & Restart。"],
     ["Docker Engine 配置保存成功且 Docker 正常重启。"],
     ["# 校验：查看 Docker 是否已应用加速器",
      "docker info | Select-String -Pattern 'Registry Mirrors' -Context 0,3",
      "",
      "# 实测拉取速度（能快速拉下小镜像即正常）",
      "docker pull hello-world"])

step(doc, "2.4.4", "配置 Ubuntu/WSL 的 apt 源（WSL 安装后执行）",
     "WSL 内默认为国外源，apt 更新一次可能耗时十几分钟。",
     ["在 WSL 中备份原源文件；", "替换为阿里云镜像（Ubuntu 24.04 使用 DEB822 格式）；", "执行 apt update 验证。"],
     ["apt update 快速完成且无报错。"],
     ["# 在 WSL 终端中执行（Ubuntu 24.04）",
      "sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak",
      "sudo sed -i 's|http://archive.ubuntu.com/ubuntu|https://mirrors.aliyun.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources",
      "sudo sed -i 's|http://security.ubuntu.com/ubuntu|https://mirrors.aliyun.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources",
      "sudo apt update",
      "",
      "# 校验：更新耗时应在 1 分钟内，且无 Failed to fetch"])

h(doc, "2.5 建立标准目录与 Git 全局配置", 2)
step(doc, "2.5.1", "创建标准工作目录",
     "统一目录结构，避免代码、数据、样本、权重混在系统盘；也为后续备份脚本提供固定路径。",
     ["在 D 盘（数据盘）创建目录结构；", "笔记本 2 只需 repo 目录。"],
     ["目录创建成功。"],
     ["# 台式机与笔记本 1：",
      "New-Item -ItemType Directory -Force -Path D:\\campus\\repo, D:\\campus\\data, D:\\campus\\weights, D:\\campus\\backup, D:\\campus\\installers, D:\\campus\\preview",
      "",
      "# 注意：代码仓库本身放在 WSL 家目录（~/projects），D 盘目录用于数据、样本、权重与备份",
      "# 校验：",
      "Get-ChildItem D:\\campus | Select-Object Name"])

step(doc, "2.5.2", "Git 全局配置",
     "统一换行、编码、长路径与大小写行为，避免跨机器协作时出现大量无意义的差异改动。",
     ["执行全局配置命令；", "设置用户名与邮箱。"],
     ["git config --list 能看到上述配置。"],
     ["git config --global core.autocrlf false",
      "git config --global core.quotepath false",
      "git config --global core.longpaths true",
      "git config --global core.ignorecase false",
      "git config --global pull.rebase false",
      "git config --global init.defaultBranch main",
      "git config --global user.name \"你的姓名\"",
      "git config --global user.email \"你的邮箱\"",
      "",
      "# 校验：",
      "git config --global --list"])

step(doc, "2.5.3", "克隆项目仓库",
     "获取统一代码基线；仓库结构包含后端、前端、部署编排与文档。",
     ["在 WSL 家目录创建 projects 目录；", "克隆仓库并查看目录结构。"],
     ["仓库成功克隆，能看到 backend/、web-admin/、deploy/、docs/ 等目录。"],
     ["# 在 WSL 中（代码放 Linux 文件系统，性能远好于 /mnt/d）",
      "mkdir -p ~/projects && cd ~/projects",
      "git clone https://gitee.com/<你的仓库>/campus-platform.git",
      "cd campus-platform && ls -la",
      "",
      "# 校验：确认远端与分支",
      "git remote -v; git branch -a"])

h(doc, "2.6 VS Code 与开发插件", 2)
step(doc, "2.6.1", "配置 VS Code 与必备扩展",
     "统一开发工具与插件，保证代码规范、调试体验与三台机器一致。",
     ["安装扩展（可直接用命令行批量安装）；", "如使用 WSL，另装 Remote - WSL 扩展；", "在设置中开启保存自动格式化、统一 UTF-8。"],
     ["扩展列表中能看到全部已安装插件。"],
     ["# 批量安装扩展（在 PowerShell 或 WSL 中均可）",
      "code --install-extension ms-python.python",
      "code --install-extension ms-python.vscode-pylance",
      "code --install-extension charliermarsh.ruff",
      "code --install-extension ms-azuretools.vscode-docker",
      "code --install-extension ms-vscode-remote.remote-wsl",
      "code --install-extension Vue.volar",
      "code --install-extension dbaeumer.vscode-eslint",
      "code --install-extension esbenp.prettier-vscode",
      "code --install-extension mtxr.sqltools",
      "code --install-extension eamodio.gitlens",
      "code --install-extension yzhang.markdown-all-in-one",
      "",
      "# 校验：",
      "code --list-extensions | Select-String -Pattern 'python|volar|docker|remote-wsl'"])

h(doc, "2.7 通用基线验收（完成本章必须全绿）", 2)
add_table(doc, ["编号", "验收项", "校验命令", "通过标准"],
          [["B-01", "机器信息已登记", "systeminfo", "信息已填入核对表"],
           ["B-02", "虚拟化已启用", "(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled", "True"],
           ["B-03", "系统更新完成", "Windows Update", "无关键更新待安装"],
           ["B-04", "时区与时间正确", "Get-TimeZone", "China Standard Time 且时间准确"],
           ["B-05", "休眠与节能已关闭", "powercfg /getactivescheme", "高性能方案，插电不休眠"],
           ["B-06", "长路径已启用", "(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem').LongPathsEnabled", "1"],
           ["B-07", "基础软件齐全", "git --version; python --version; node -v", "均有版本输出"],
           ["B-08", "UTF-8 生效", "chcp", "65001"],
           ["B-09", "pip 镜像生效", "pip config list", "index-url 为清华源"],
           ["B-10", "npm 镜像生效", "npm config get registry", "npmmirror"],
           ["B-11", "工作目录已建立", "Get-ChildItem D:\\campus", "目录齐全"],
           ["B-12", "Git 全局配置完成", "git config --global --list", "含 user.name/user.email"],
           ["B-13", "仓库已克隆", "git remote -v", "能看到远端地址"]],
          [1.2, 3.4, 6.4, 3.2], size=8.5, align_center_cols=(0,))
note(doc, "建议直接运行配套脚本一次性完成本章大部分配置：环境工具/scripts/install-base.ps1（管理员 PowerShell 中执行，按提示选择机器角色）。")

# ============================================================
h(doc, "第 3 章 台式机（主力开发机）详细配置", 1, page_break=True)
para(doc, "本章是环境构建的核心。台式机 i5-13400F + RTX 3050 8GB 承担 AI 训练与全栈开发，配置完成后即可独立完成"
          "“模型训练 → 导出 ONNX → 平台联调 → 演示”的全流程。请严格按 3.1 → 3.10 顺序执行。")
add_table(doc, ["章节", "配置内容", "预计耗时", "完成标志"],
          [["3.1", "WSL2 + Ubuntu 24.04（Linux 开发底座）", "30—60 分钟", "wsl -l -v 显示 Running / VERSION 2"],
           ["3.2", "Docker Desktop 与依赖服务全栈", "60—90 分钟", "5 个服务 healthy，PG/Redis/EMQX/MinIO 可连"],
           ["3.3", "Python 后端开发环境", "40 分钟", "Swagger 页面可打开"],
           ["3.4", "AI 训练环境（CUDA / PyTorch / YOLO）", "90—150 分钟", "torch.cuda.is_available() 为 True，训练出权重"],
           ["3.5", "ONNX 导出与推理验证", "40 分钟", "推理与 PyTorch 偏差 ≤1e-3"],
           ["3.6", "前端开发环境", "40 分钟", "页面能调用后端接口"],
           ["3.7", "设备与外设模拟环境", "60 分钟", "伪视频可拉流、模拟设备可上报"],
           ["3.8", "Nginx 本地网关（可选）", "20 分钟", "通过 8080 端口访问平台"],
           ["3.9", "监控与日志（可选）", "40 分钟", "Prometheus 能抓到后端指标"],
           ["3.10", "台式机验收清单（25 项）", "60 分钟", "全部通过"]],
          [1.4, 6.0, 2.4, 6.4], size=9, align_center_cols=(0, 2))

h(doc, "3.1 安装 WSL2 与 Ubuntu 24.04", 2)
step(doc, "3.1.1", "安装 WSL2 与 Ubuntu 24.04",
     "WSL2 提供与现场服务器一致的 Linux 环境，也是 Docker Desktop 的运行后端；"
     "开发期的所有服务端命令都在这里执行，可避免 Windows 与 Linux 的路径/权限差异。",
     ["以管理员身份打开 PowerShell 7；",
      "执行安装命令（会自动启用虚拟机平台与 WSL 组件）；",
      "按提示重启电脑；",
      "重启后首次进入 Ubuntu，设置 Linux 用户名与密码（与 Windows 密码无关，请记录）；",
      "确认默认版本为 WSL2。"],
     ["ubuntu 发行版状态为 Running，VERSION 为 2。"],
     ["# 安装（管理员 PowerShell）",
      "wsl --install -d Ubuntu-24.04",
      "wsl --set-default-version 2",
      "",
      "# 重启后校验：",
      "wsl -l -v",
      "wsl --status",
      "# 期望：Ubuntu-24.04  STATE=Running  VERSION=2"])

step(doc, "3.1.2", "初始化 Ubuntu 基础环境",
     "安装编译工具、命令行工具与视频处理工具（FFmpeg 是后续伪视频与算法调试的基础）。",
     ["进入 WSL 终端；", "先按 2.4.4 配置 apt 国内源；", "安装基础工具包。"],
     ["工具安装完成，命令可执行。"],
     ["# 在 WSL 中执行",
      "sudo apt update && sudo apt upgrade -y",
      "sudo apt install -y build-essential curl wget git vim htop net-tools unzip zip \\",
      "  ffmpeg jq tree ncdu lsof ca-certificates gnupg lsb-release",
      "",
      "# 校验：",
      "ffmpeg -version | head -1",
      "git --version; curl --version | head -1"])

step(doc, "3.1.3", "配置 WSL 资源与文件互通",
     "限制 WSL 内存占用（避免 16GB 机器被吃满），并规划代码存放位置（性能关键）。",
     ["创建 / 编辑 .wslconfig 限制内存与 CPU；", "重启 WSL 使配置生效；", "确认代码目录放在 Linux 文件系统内。"],
     ["WSL 内存占用不超过上限；代码目录位于 ~/projects。"],
     ["# 在 Windows 用户目录创建 C:\\Users\\<你的用户名>\\.wslconfig",
      "[wsl2]",
      "memory=8GB          # 16GB 内存机器建议 8GB；升级到 32GB 后可改为 16GB",
      "processors=8",
      "swap=4GB",
      "",
      "# 应用配置（PowerShell 中执行）",
      "wsl --shutdown",
      "wsl -d Ubuntu-24.04",
      "",
      "# 校验：WSL 内查看可用内存（应接近 memory 设置值）",
      "free -h"])

h(doc, "3.2 安装 Docker Desktop 与依赖服务全栈", 2)
step(doc, "3.2.1", "配置 Docker Desktop（WSL2 后端 + 加速 + 资源限制）",
     "按架构方案，竞赛版用 Docker Compose 一条命令起全栈（PostgreSQL 16 + pgvector、Redis 7、EMQX 5、MinIO、TDengine），"
     "这样开发环境与现场服务器的版本完全一致。",
     ["启动 Docker Desktop，首次运行会要求接受协议；",
      "Settings → General：勾选 Use the WSL 2 based engine，勾选 Start Docker Desktop when you sign in；",
      "Settings → Resources → WSL Integration：启用 Ubuntu-24.04；",
      "Settings → Resources：内存限制 8GB（16GB 机器）、CPU 8 核；",
      "Settings → Docker Engine：加入 registry-mirrors（见 2.4.3）；",
      "Apply & Restart。"],
     ["Docker Desktop 显示 Engine running；docker version 有 Client 与 Server 两段输出。"],
     ["docker version",
      "docker compose version",
      "docker info | Select-String 'Server Version','Total Memory','Registry Mirrors'",
      "docker run --rm hello-world",
      "# 期望：输出 Hello from Docker!"])

step(doc, "3.2.2", "编写开发用 docker-compose.dev.yml",
     "把依赖服务的版本、端口、口令、数据卷固化到文件，保证任何一台机器起出来的环境完全一致；"
     "该文件与现场部署共用同一份骨架，仅 .env 与编排差异不同。",
     ["在仓库 deploy/ 目录创建 docker-compose.dev.yml；",
      "创建 .env（从 .env.example 复制）并填写强口令；",
      "确认 .env 已在 .gitignore 中。"],
     ["compose 文件与 .env 就绪，且 .env 不会被提交到仓库。"],
     ["# 仓库结构（建议）",
      "# campus-platform/",
      "#   deploy/",
      "#     docker-compose.dev.yml      开发：只起依赖服务",
      "#     docker-compose.prod.yml     生产：依赖 + 应用",
      "#     .env.example                模板（入库）",
      "#     .env                        实际口令（不入库）",
      "#   backend/   web-admin/   docs/",
      "",
      "# 校验：确认 .env 已被忽略",
      "git check-ignore -v deploy/.env"])

add_code(doc, [
    "# deploy/docker-compose.dev.yml —— 开发依赖服务（与架构方案选型一致）",
    "services:",
    "  postgres:",
    "    image: pgvector/pgvector:pg16          # PostgreSQL 16 + pgvector（向量检索）",
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
    "    image: redis:7-alpine                  # Redis 7 单实例 + AOF（架构方案竞赛版）",
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
    "    image: emqx/emqx:5                     # MQTT 设备接入（架构方案推荐）",
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
    "    image: minio/minio                     # 对象存储（事件截图、短视频、附件）",
    "    container_name: campus-minio",
    "    command: ['server','/data','--console-address',':9001']",
    "    environment:",
    "      MINIO_ROOT_USER: ${MINIO_USER}",
    "      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}",
    "      TZ: Asia/Shanghai",
    "    ports: ['9000:9000','9001:9001']",
    "    volumes: ['miniodata:/data']",
    "    healthcheck:",
    "      test: ['CMD','mc','ready','local']",
    "      interval: 15s",
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
     ["在 WSL 中进入 deploy 目录；", "后台启动全部服务；", "查看状态与日志；", "逐项验证连通性。"],
     ["五个容器状态为 running/healthy。"],
     ["# 在 WSL 中执行",
      "cd ~/projects/campus-platform/deploy",
      "cp .env.example .env && vim .env      # 填入强口令",
      "docker compose -f docker-compose.dev.yml up -d",
      "docker compose -f docker-compose.dev.yml ps",
      "",
      "# 逐项校验：",
      "# 1) PostgreSQL 16",
      "docker exec -it campus-pg psql -U campus -d campus -c 'select version();'",
      "docker exec -it campus-pg psql -U campus -d campus -c 'create extension if not exists vector;'",
      "docker exec -it campus-pg psql -U campus -d campus -c 'select extversion from pg_extension where extname=$$vector$$;'",
      "# 2) Redis 7",
      "docker exec -it campus-redis redis-cli -a $REDIS_PASSWORD ping",
      "# 期望：PONG",
      "# 3) EMQX 5（浏览器打开 http://localhost:18083，默认账号 admin）",
      "curl -s http://localhost:18083/status",
      "# 4) MinIO（浏览器打开 http://localhost:9001）",
      "curl -s -o /dev/null -w '%{http_code}\\n' http://localhost:9000/minio/health/live",
      "# 期望：200",
      "# 5) TDengine（V2 阶段再启用，启用后校验）",
      "curl -s -u root:taosdata -d 'show databases' http://localhost:6041/rest/sql",
])
note(doc, "首次登录 EMQX Dashboard（18083）后立即修改默认口令；MinIO 控制台（9001）创建的桶一律设为私有（private），不要设为 public。")
