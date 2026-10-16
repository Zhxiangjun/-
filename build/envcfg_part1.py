# -*- coding: utf-8 -*-
"""生成《电脑环境配置详细方案（可执行版）》— 共享构建工具与前置章节（第 1—2 章、第 3.1—3.2 节）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_kit import *
from docx_kit import _font
from docx import Document
from docx.shared import Pt, Cm

OUT = r"F:\职业中专\大赛\智慧园区创意\项目文档\09_电脑环境配置详细方案.docx"


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


def new_doc():
    doc = Document()
    setup(doc, "电脑环境配置详细方案 V2.0")
    cover(doc,
          "“智园卫士”智慧校园管理平台",
          "电脑环境配置详细方案（可执行版）— 依据总体技术架构方案 V1.0 选型",
          [("文档名称", "电脑环境配置详细方案（可执行版）"),
           ("文档编号", "ZYWS-ENV-2026-002"),
           ("版本号", "V2.0（单机全栈版）"),
           ("版本要点", "以“一台台式机完成全部开发与测试”为主线；笔记本、协作电脑与服务器降级为可选外援环境"),
           ("编制单位", "齐河县职业中等专业学校 项目组"),
           ("编制依据", "《总体技术架构方案》V1.0 第 7 章关键技术选型、第 8 章 AI 视觉能力设计、第 5 章部署架构"),
           ("适用对象", "台式机（唯一主线环境）；演示笔记本、协作电脑、云服务器与校内服务器（按需）"),
           ("使用方式", "按第 3 章确认环境类型后，执行第 2 章通用基线与第 4 章台式机全栈；每步均含命令、预期结果与校验方法"),
           ("配套文件", "文档 10（进度与验收台账）、文档 11（总览与快速开始）、文档 12（协作环境指引）、环境工具/scripts/"),
           ("编制日期", "2026 年 11 月（V2.0 修订于 2026-10-14）"),
           ("密级", "内部")],
          doc_kind="电 脑 环 境 配 置 详 细 方 案")
    doc.add_page_break()
    h(doc, "修订记录", 1)
    add_table(doc, ["版本", "日期", "修订内容", "编制人", "审核"],
              [["V0.5", "2026-11-20", "依据总体技术架构方案 V1.0 确定技术栈与机器分工", "项目组", "指导教师"],
               ["V0.9", "2026-11-26", "补充逐步命令、预期结果与校验方法，形成可执行步骤", "项目组", "指导教师"],
               ["V1.0", "2026-11-28", "全文评审通过，作为环境构建与验收的执行基线（三机分工版）", "项目组", "学校信息中心"],
               ["V2.0", "2026-10-14", "重构为“单台式机全栈”主线：原第 3—9 章合并为第 4 章；笔记本 1、2 降级为第 5、6 章外援环境；"
                                     "新增第 3 章环境类型与文档导航、第 4.6 节 15 项单机快速验收；服务器与机房顺延为第 7、8 章",
                "项目组", "指导教师"]],
              [1.6, 2.2, 8.0, 2.0, 2.0], size=9, align_center_cols=(0, 1, 3, 4))
    note(doc, "本方案的技术选型与《总体技术架构方案》V1.0 保持一致；若架构方案变更，本方案需同步修订并更新版本号。"
              "V2.0 与 V1.0 的章节对应关系见《文档关系与口径对照说明》（文档 13），台账中也附有新老编号对照表。")
    return doc


def chapter1(doc):
    h(doc, "第 1 章 环境配置总览", 1, page_break=True)
    h(doc, "1.1 本方案的定位与使用方法", 2)
    para(doc, "本方案是环境构建的唯一执行依据：从一台空白电脑开始，按章节顺序操作，即可得到可用于本项目开发、演示与部署的完整环境。"
              "每个配置项都按“目的 → 操作步骤 → 预期结果 → 校验”四段式编写，校验命令的通过标准明确，未通过不得继续。")
    add_table(doc, ["你要做什么", "看哪一章", "预计耗时", "完成标志"],
              [["先看清三种环境分别干什么", "第 1 章 / 文档 11", "10 分钟", "知道自己的电脑属于哪一类"],
               ["把台式机装成完整开发环境（主线）", "第 4 章", "1—2 个工作日", "15 项单机验收全绿，能写功能代码"],
               ["严格验收全栈环境（25 项）", "第 9 章", "1 小时", "25 项全绿，可开始 M2 开发"],
               ["顺手配一台笔记本做演示备份（可选）", "第 5 章", "3—4 小时", "断网也能完整演示"],
               ["给协作同学一份装机清单（可选）", "第 6 章 / 文档 12", "对方 2 小时", "对方能拉代码、跑前端、连你的后端"],
               ["把平台放到服务器上（上线时才要）", "第 7 章", "2—3 小时", "外网可访问，备份可恢复"]],
              [5.4, 2.6, 2.4, 4.6], size=9, align_center_cols=(2,))

    h(doc, "1.2 环境总览：三种环境类型", 2)
    para(doc, "本项目共需三类环境，其中只有第一类是开发必需，另外两类是“外援”：一类用于外出演示与备用运行，"
              "一类用于协作者和服务器。相关文档见《电脑环境配置总览与快速开始》。")
    add_table(doc, ["环境类型", "谁需要", "装在哪", "配置内容", "是否开发必需"],
              [["① 单机全栈开发环境", "你（项目负责人/开发者）", "台式机（i5-13400F + RTX 3050）",
                "WSL2 + Docker 依赖服务（PG/Redis/EMQX/MinIO）+ 后端 + 前端 + AI 训练 + 设备模拟", "必需（主线）"],
               ["② 备份/演示环境", "外出演示、断网答辩", "任一台笔记本（或装 Ubuntu 的旧电脑）",
                "只装 Docker 全栈 + 前端静态产物 + Nginx，用同一份 compose 与仓库，不写代码", "非必需"],
               ["③ 角色化协作环境", "协作同学、学生团队", "协作同学的电脑（客户端）",
                "Git + VS Code + Node + 浏览器 + 连你的机器或云端，按“客户端”清单安装", "非必需"],
               ["③ 角色化协作环境", "上线运行、对外服务", "阿里云 ECS 或校内服务器",
                "Docker Engine + Compose v2 + 依赖服务 + 应用 + Nginx/HTTPS + 备份", "非必需（上线时才要）"]],
              [3.0, 2.6, 3.4, 6.2, 2.4], size=8.5)
    para(doc, "配置原则：能在一台电脑上完成的，绝不拆到两台。只有“需要 7×24 运行”或“需要外部访问”时，"
              "才把服务放到服务器上。", size=10)

    h(doc, "1.3 技术栈锁定表（严格照此版本，不自行替换）", 2)
    para(doc, "下表逐项对应《总体技术架构方案》V1.0 第 7 章推荐选型（竞赛版）。安装时按“锁定选型”列执行；如遇组件更新，"
              "保持主版本号不变（例如 PostgreSQL 16.x），并在环境报告中记录实际版本。")
    add_table(doc, ["层次", "技术域", "锁定选型（架构方案推荐）", "安装位置", "关键配置点"],
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
               ["消息", "IoT 接入", "EMQX 5 开源版（+ Redis Stream 做业务异步）", "台式机、笔记本1、云、现场", "1883 / 8083 / 18083，改默认密码"],
               ["AI", "训练", "PyTorch 2.x + CUDA 12 + Ultralytics（YOLOv8n/s）", "台式机（仅此一台）", "独立虚拟环境，不与业务依赖混装"],
               ["AI", "推理", "ONNX Runtime（CPU / 单 GPU），导出 opset 17", "台式机、边缘盒子", "与 PyTorch 结果偏差 ≤1e-3"],
               ["AI", "向量检索", "pgvector（人脸底库 ≤5 万）", "随 PostgreSQL 一并部署", "ivfflat 索引，维度与特征模型一致"],
               ["运行", "容器与编排", "Docker Compose（一键起全栈）", "台式机、笔记本1、云、现场", "数据卷持久化 + 健康检查"],
               ["运行", "网关", "Nginx（反向代理 + 静态资源 + 限流）", "笔记本1、云、现场", "HTTPS 终止、gzip、静态缓存"],
               ["运行", "监控", "Prometheus + Grafana（单机）", "云、现场（可选）", "核心服务与端口存活监控"]],
              [1.4, 2.0, 5.4, 3.0, 3.6], size=8.5, align_center_cols=(0, 1))

    h(doc, "1.4 配置实施顺序（跨机器）", 2)
    para(doc, "环境构建按依赖关系推进：先通底座，再通数据，最后通应用。推荐按下表顺序执行，每完成一行在核对表中勾选。")
    add_table(doc, ["顺序", "任务", "在哪台机器", "前置条件", "产出"],
              [["①", "通用基线环境（第 2 章）", "三台 Windows 机器", "可联网、有管理员权限", "基础工具链与镜像源就绪"],
               ["②", "WSL2 + Ubuntu 24.04", "台式机、笔记本 1", "BIOS 已开启虚拟化", "可用的 Linux 环境"],
               ["③", "Docker Desktop + 依赖服务全栈", "台式机、笔记本 1", "② 完成", "PG / Redis / EMQX / MinIO 一条命令起"],
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
    bullet(doc, "命令约定：以 PS> 开头表示 Windows PowerShell 7（管理员）；以 $ 开头表示 WSL/Linux 终端；文件路径按提示区分 Windows 与 Linux 写法。")
    bullet(doc, "口令约定：所有服务口令统一使用强口令（12 位以上，含大小写字母、数字、符号），集中登记在密码管理表；禁止使用 123456、postgres 等默认口令。")
    bullet(doc, "密钥红线：口令、密钥、令牌只允许存放在 .env 文件或系统环境变量中，禁止写入代码、文档、截图与聊天记录；.env 必须加入 .gitignore。")
    bullet(doc, "数据红线：人脸模板与人脸原图只允许保存在校内设备与本地开发机，禁止上传公有云、网盘或第三方平台；开发与测试阶段使用合成人脸数据。")
    bullet(doc, "网络红线：数据库（5432）、Redis（6379）、MQTT（1883）禁止对公网开放；云端只放行 22（限定来源 IP）、80、443。")
    bullet(doc, "变更约定：如需替换架构方案中的选型（例如改用 MySQL），必须先更新《总体技术架构方案》并说明理由，不得在环境层面私自替换。")


def chapter2(doc):
    h(doc, "第 2 章 通用基线环境（三台 Windows 机器都要做）", 1, page_break=True)
    para(doc, "本章内容三台 Windows 电脑都要执行。完成后每台机器都具备统一的基础工具链、编码环境与镜像源，"
              "后续章节只在此基础上追加各自特有的组件。本章大部分工作可由配套脚本自动完成，再按步骤手工补齐。")

    h(doc, "2.1 机器信息登记与前置检查", 2)
    step(doc, "2.1.1", "登记机器信息并确认硬件条件",
         "建立机器档案，后续排查问题时能快速定位是哪台机器、什么配置。",
         ["记录计算机名、CPU、内存、显卡型号、驱动版本、系统版本、磁盘可用空间。",
          ("code", ["# 在 PowerShell 中执行，输出即机器档案",
                    "systeminfo | Select-String 'OS 名称','OS 版本','系统型号','总物理内存'",
                    "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors",
                    "Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion",
                    "Get-PSDrive -PSProvider FileSystem | Select-Object Name,@{n='可用GB';e={[math]::Round($_.Free/1GB,1)}}"]),
          "把结果填入《环境准备与选型核对表》的“机器分工”工作表。"],
         ["系统为 Windows 10 21H2 以上或 Windows 11；",
          "磁盘可用空间：台式机 C 盘 ≥60GB、D 盘 ≥150GB；笔记本 1 C 盘 ≥60GB；笔记本 2 C 盘 ≥40GB。"],
         ["Get-CimInstance Win32_ComputerSystem | Select-Object @{n='内存GB';e={[math]::Round($_.TotalPhysicalMemory/1GB,0)}}",
          "# 期望 16；若为 8 则先加内存再继续（否则第 3 章会明显卡顿）"])

    step(doc, "2.1.2", "开启 CPU 虚拟化（WSL2 与 Docker 的硬前提）",
         "WSL2 与 Docker Desktop 依赖硬件虚拟化，未开启则第 3、4 章无法进行。",
         ["重启电脑进入 BIOS/UEFI（开机按 Del / F2 / F10，视主板品牌而定）；",
          "Intel 平台开启 Intel Virtualization Technology（VT-x），AMD 平台开启 SVM Mode；",
          "保存退出（通常是 F10）后回到 Windows。"],
         ["系统显示虚拟化已启用。"],
         ["(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled",
          "# 期望 True；也可在任务管理器 → 性能 → CPU 中查看“虚拟化：已启用”"])

    step(doc, "2.1.3", "系统准备：更新、时间、电源、长路径",
         "避免因系统补丁缺失、时间不同步、休眠断网、路径过长导致后续诡异故障。",
         ["执行 Windows Update 至最新；",
          "确认时区为北京（UTC+8）并开启自动同步；",
          "电源计划改为高性能，关闭硬盘与网卡节能、关闭自动休眠（演示机尤其重要）；",
          "启用 NTFS 长路径（Node 与 Python 嵌套目录容易超长）。"],
         ["无待安装关键更新；时间准确；插电不休眠；长路径已启用。"],
         ["Get-TimeZone | Select-Object Id,DisplayName",
          "powercfg /getactivescheme",
          "(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem').LongPathsEnabled",
          "# 期望：China Standard Time / 高性能 / 长路径返回 1"])

    h(doc, "2.2 安装基础软件（winget 批量）", 2)
    step(doc, "2.2.1", "确认 winget 可用",
         "winget 是 Windows 官方包管理器，可一条命令安装后续所有软件，避免逐个下载安装包。",
         ["打开 Microsoft Store，搜索并安装或更新“应用安装程序（App Installer）”；",
          "打开 PowerShell 7（管理员），执行校验命令。"],
         ["能输出版本号。"],
         ["winget --version",
          "# 若提示找不到命令：访问 https://aka.ms/getwinget 安装，或改用第 7 章离线包手工安装"])

    step(doc, "2.2.2", "按机器角色批量安装基础软件",
         "一次装齐全部基础工具，并保证三台机器版本一致，避免“我这里能跑”的问题。",
         ["确认当前是管理员 PowerShell；",
          "按机器角色执行对应安装命令；",
          "安装过程中若弹出 UAC 或重启提示，按提示处理后继续。"],
         ["各软件安装成功，命令可执行。"],
         ["# 角色一：台式机（dev，全量）",
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
          "# 角色二：笔记本 1（server）",
          "winget install --id Git.Git -e; winget install --id Microsoft.VisualStudioCode -e",
          "winget install --id Microsoft.PowerShell -e; winget install --id Microsoft.WindowsTerminal -e",
          "winget install --id Python.Python.3.12 -e; winget install --id OpenJS.NodeJS.LTS -e",
          "winget install --id Docker.DockerDesktop -e; winget install --id dbeaver.dbeaver -e",
          "",
          "# 角色三：笔记本 2（client）",
          "winget install --id Git.Git -e; winget install --id Microsoft.VisualStudioCode -e",
          "winget install --id OpenJS.NodeJS.LTS -e",
          "",
          "# 校验（重开终端后执行）：",
          "git --version; python --version; node -v; docker --version"])

    step(doc, "2.2.3", "安装图形化辅助工具（按机器需要）",
         "部分工具未提供 winget 包，需手工下载；这些是设备联调与接口调试的必备工具。",
         ["MQTTX（MQTT 调试）：https://mqttx.app 下载 Windows 版；",
          "Apifox 或 Postman（接口调试）：官网下载；",
          "MobaXterm（SSH 运维）：https://mobaxterm.mobatek.net 下载 Home Edition；",
          "SSCOM 或 XCOM（串口调试，RS-485 / Modbus）：仅笔记本 2 需要；",
          "ONVIF Device Manager（摄像机发现）：GitHub 下载，仅笔记本 2 需要；",
          "Wireshark（抓包）：台式机与笔记本 2 需要。"],
         ["各工具可正常启动。"],
         ["# 校验：确认关键工具已安装（图形界面手工确认启动即可）",
          "Get-ChildItem 'C:\\Program Files' -Filter '*MQTT*' -ErrorAction SilentlyContinue"])

    h(doc, "2.3 统一编码与语言环境", 2)
    step(doc, "2.3.1", "设置 UTF-8 与 Python 编码环境变量",
         "中文 Windows 默认 GBK，会导致 Python 输出乱码、脚本报 UnicodeEncodeError、日志不可读。",
         ["控制面板 → 区域 → 管理 → 更改系统区域设置 → 勾选 Beta 版 UTF-8；",
          "设置用户环境变量 PYTHONUTF8=1、PYTHONIOENCODING=utf-8；",
          "重启电脑使区域设置全局生效。"],
         ["chcp 显示 65001；Python 打印中文不乱码。"],
         ["chcp",
          "$env:PYTHONUTF8; [Environment]::GetEnvironmentVariable('PYTHONUTF8','User')",
          "python -c \"print('中文编码测试：智慧园区平台')\"",
          "# 期望输出：中文编码测试：智慧园区平台（无乱码）"])

    h(doc, "2.4 配置国内镜像源（务必先做这一步）", 2)
    step(doc, "2.4.1", "配置 pip 清华源",
         "国内直连 PyPI 极慢或超时，不配镜像会导致依赖安装反复失败。",
         ["创建 %APPDATA%\\pip 目录；", "写入 pip.ini 配置文件。"],
         ["pip config list 显示清华源。"],
         ["mkdir \"$env:APPDATA\\pip\" -Force",
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
          "pip install --upgrade pip"])

    step(doc, "2.4.2", "配置 npm 淘宝源",
         "默认 npm 源在国内安装依赖经常卡住。",
         ["设置 registry 为 npmmirror；", "延长超时时间。"],
         ["npm config get registry 返回 npmmirror 地址。"],
         ["npm config set registry https://registry.npmmirror.com",
          "npm config set fetch-timeout 120000",
          "",
          "# 校验：",
          "npm config get registry"])

    step(doc, "2.4.3", "配置 Docker 镜像加速（安装 Docker 后执行）",
         "默认从 Docker Hub 拉镜像在国内常超时。注意网上流传的公共加速地址大多已失效，"
         "应使用自己阿里云账号的专属加速地址。",
         ["登录阿里云控制台 → 容器镜像服务 ACR → 镜像工具 → 镜像加速器；",
          "复制专属加速地址（形如 https://xxxx.mirror.aliyuncs.com）；",
          "Docker Desktop → Settings → Docker Engine，将地址加入 registry-mirrors 数组；",
          "Apply & Restart。"],
         ["配置保存成功，Docker 正常重启。"],
         ["docker info | Select-String -Pattern 'Registry Mirrors' -Context 0,3",
          "docker pull hello-world"])

    step(doc, "2.4.4", "配置 Ubuntu / WSL 的 apt 源",
         "WSL 内默认为国外源，apt 更新一次可能耗时十几分钟。",
         ["备份原源文件；", "替换为阿里云镜像（Ubuntu 24.04 为 DEB822 格式）；", "执行 apt update 验证。"],
         ["apt update 快速完成且无报错。"],
         ["# 在 WSL 中执行",
          "sudo cp /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list.d/ubuntu.sources.bak",
          "sudo sed -i 's|http://archive.ubuntu.com/ubuntu|https://mirrors.aliyun.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources",
          "sudo sed -i 's|http://security.ubuntu.com/ubuntu|https://mirrors.aliyun.com/ubuntu|g' /etc/apt/sources.list.d/ubuntu.sources",
          "sudo apt update"])

    h(doc, "2.5 建立标准目录与 Git 全局配置", 2)
    step(doc, "2.5.1", "创建标准工作目录",
         "统一目录结构，避免代码、数据、样本、权重混在系统盘，也为备份脚本提供固定路径。",
         ["在 D 盘创建目录结构；", "注意代码仓库本身放在 WSL 家目录（性能关键）。"],
         ["目录创建成功。"],
         ["New-Item -ItemType Directory -Force -Path D:\\campus\\repo, D:\\campus\\data, D:\\campus\\weights, D:\\campus\\backup, D:\\campus\\installers, D:\\campus\\preview",
          "",
          "# 校验：",
          "Get-ChildItem D:\\campus | Select-Object Name"])

    step(doc, "2.5.2", "Git 全局配置与克隆仓库",
         "统一换行、编码、长路径与大小写行为，避免跨机器协作产生无意义差异改动；同时获取统一代码基线。",
         ["执行 Git 全局配置；", "在 WSL 中克隆仓库（代码放 Linux 文件系统）。"],
         ["git config --list 含全部配置；仓库克隆成功。"],
         ["git config --global core.autocrlf false",
          "git config --global core.quotepath false",
          "git config --global core.longpaths true",
          "git config --global core.ignorecase false",
          "git config --global pull.rebase false",
          "git config --global init.defaultBranch main",
          "git config --global user.name \"你的姓名\"",
          "git config --global user.email \"你的邮箱\"",
          "",
          "# 在 WSL 中克隆（注意：不要克隆到 /mnt/d，性能差数倍）",
          "mkdir -p ~/projects && cd ~/projects",
          "git clone https://gitee.com/<你的仓库>/campus-platform.git",
          "cd campus-platform && ls -la && git remote -v"])

    h(doc, "2.6 VS Code 与开发插件", 2)
    step(doc, "2.6.1", "配置 VS Code 与必备扩展",
         "统一开发工具与插件，保证代码规范与调试体验三台机器一致。",
         ["命令行批量安装扩展；", "使用 WSL 时另装 Remote - WSL；", "开启保存自动格式化与 UTF-8。"],
         ["扩展列表可见全部插件。"],
         ["code --install-extension ms-python.python",
          "code --install-extension ms-python.vscode-pylance",
          "code --install-extension charliermarsh.ruff",
          "code --install-extension ms-azuretools.vscode-docker",
          "code --install-extension ms-vscode-remote.remote-wsl",
          "code --install-extension Vue.volar",
          "code --install-extension dbaeumer.vscode-eslint",
          "code --install-extension esbenp.prettier-vscode",
          "code --install-extension eamodio.gitlens",
          "code --install-extension yzhang.markdown-all-in-one",
          "",
          "# 校验：",
          "code --list-extensions | Select-String -Pattern 'python|volar|docker|remote-wsl'"])

    h(doc, "2.7 通用基线验收（完成本章必须全绿）", 2)
    add_table(doc, ["编号", "验收项", "校验命令", "通过标准"],
              [["B-01", "机器信息已登记", "systeminfo", "已填入核对表"],
               ["B-02", "虚拟化已启用", "(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled", "True"],
               ["B-03", "系统更新完成", "Windows Update", "无关键更新待安装"],
               ["B-04", "时区与时间正确", "Get-TimeZone", "China Standard Time"],
               ["B-05", "休眠与节能已关闭", "powercfg /getactivescheme", "高性能且插电不休眠"],
               ["B-06", "长路径已启用", "(Get-ItemProperty 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\FileSystem').LongPathsEnabled", "1"],
               ["B-07", "基础软件齐全", "git --version; python --version; node -v", "均有版本输出"],
               ["B-08", "UTF-8 生效", "chcp", "65001"],
               ["B-09", "pip 镜像生效", "pip config list", "清华源"],
               ["B-10", "npm 镜像生效", "npm config get registry", "npmmirror"],
               ["B-11", "工作目录已建立", "Get-ChildItem D:\\campus", "目录齐全"],
               ["B-12", "Git 全局配置完成", "git config --global --list", "含 user.name / user.email"],
               ["B-13", "仓库已克隆", "git remote -v", "能看到远端地址"]],
              [1.2, 3.4, 6.4, 3.2], size=8.5, align_center_cols=(0,))
    note(doc, "建议直接运行配套脚本一次性完成本章大部分配置：以管理员身份打开 PowerShell 7，执行 环境工具\\scripts\\install-base.ps1，按提示选择机器角色。")
