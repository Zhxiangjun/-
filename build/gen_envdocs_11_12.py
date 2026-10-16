# -*- coding: utf-8 -*-
"""生成 11_电脑环境配置总览与快速开始.docx 与 12_协作开发环境配置指引.docx"""
import os
from docx_kit import *
from envcfg_shared import acceptance_simple
from docx import Document


def doc_quickstart(path):
    doc = Document()
    setup(doc, "电脑环境配置总览与快速开始 V1.0")
    cover(doc,
          "“智园卫士”智慧校园管理平台",
          "电脑环境配置总览与快速开始",
          [("文档名称", "电脑环境配置总览与快速开始"),
           ("文档编号", "ZYWS-ENV-2026-003"),
           ("版本号", "V1.0（单机全栈版）"),
           ("一句话说明", "只需一台台式机即可完成全部开发与测试；本文档说明三类环境分别干什么、你先做哪一步"),
           ("配套文档", "文档 09《电脑环境配置详细方案》（执行手册）、文档 10（进度与验收台账）、文档 12（协作环境指引）"),
           ("配套脚本", "环境工具/scripts/install-base.ps1（一键基础环境）、check-env.py（环境自检）"),
           ("编制日期", "2026 年 11 月"),
           ("密级", "内部")],
          doc_kind="总 览 与 快 速 开 始")

    h(doc, "1 这张图先看一遍", 1, page_break=True)
    para(doc, "本项目的环境只有三类，用途完全不同。记住一句话就能分清：你的台式机是“干活的地方”，"
              "另外两类要么是“播放机”，要么是“给别人用的电脑”。")
    add_table(doc, ["环境类型", "这台电脑是干什么的", "谁用", "装什么", "不装什么"],
              [["① 开发环境\n（台式机，主线）",
                "写代码、调接口、训练模型、跑模拟设备、本地看效果。项目约 90% 的工作在这里完成",
                "你本人", "WSL2 + Docker（PG/Redis/EMQX/MinIO）+ 后端 + 前端 + AI 训练 + 设备模拟",
                "不需要额外服务器"],
               ["② 演示 / 备份环境\n（任一台笔记本，可选）",
                "外出演示、比赛答辩时播放已做好的平台；断网也要能演示",
                "外出演示的人", "Docker 全栈 + 前端静态产物 + Nginx + 模拟设备脚本",
                "不装 AI 训练、不写代码"],
               ["③ 协作环境\n（同学/学生电脑，可选）",
                "协作同学改代码、跑前端、连你的后端；测试人员验证功能",
                "协作同学、学生", "Git + VS Code + Node + 浏览器（+ 可选 Python/数据库客户端）",
                "不装 Docker、数据库、AI 环境"],
               ["③ 服务器环境\n（云或校内服务器，上线才要）",
                "7×24 运行、对外访问、小程序后端、数据备份",
                "学校信息中心", "Docker Engine + Compose + 依赖服务 + 应用 + Nginx/HTTPS + 备份",
                "不接收校内视频流"]],
              [3.2, 5.4, 2.2, 4.6, 2.6], size=8.5)
    para(doc, "重要观念：开发阶段不要引入第二台服务器。数据库、缓存、消息队列、对象存储全部以容器形式"
              "跑在你的台式机上，一条命令启动、一条命令停止，随时可重置，不污染系统。"
              "只有“需要 7×24 运行”或“需要外网访问”时，才把服务搬到服务器上。", size=10)

    h(doc, "2 你现在该做什么（先看这张表）", 1)
    add_table(doc, ["你的情况", "你要做的事", "看哪里", "预计耗时"],
              [["只有一台台式机，想尽快跑起来", "做通用基线 + 台式机全栈环境，然后跑 15 项快速验收",
                "文档 09 第 2 章、第 4 章", "1—2 个工作日"],
               ["想让环境更规范、可追溯", "在上一行基础上完成 25 项全栈验收并归档", "文档 09 第 9 章 + 台账 10", "加 1—2 小时"],
               ["要带出去演示或参加比赛", "再配一台笔记本做“播放机”", "文档 09 第 5 章", "半天"],
               ["有同学/学生协助开发", "把文档 12 整份发给对方，让其按角色安装", "文档 12", "对方约 2 小时"],
               ["要上线给全校用或做小程序", "再配服务器环境（云或校内）", "文档 09 第 7 章", "半天"],
               ["要带班教学、机房统一环境", "按机房批量部署方案执行", "文档 09 第 8 章", "1—2 天"]],
              [4.6, 5.6, 3.6, 2.4], size=9, align_center_cols=(3,))

    h(doc, "3 五分钟路线图（一台电脑的全部流程）", 1, page_break=True)
    add_table(doc, ["步骤", "做什么", "完成标志", "预计耗时"],
              [["第 1 步", "装通用基线：Git、VS Code、Python、Node、镜像源、目录规范（可直接运行一键脚本）",
                "git / python / node 有版本输出，pip 与 npm 用国内源", "1—2 小时"],
               ["第 2 步", "装 WSL2 + Ubuntu 24.04（服务端底座）", "wsl -l -v 显示 Ubuntu Running、VERSION 2", "30—60 分钟"],
               ["第 3 步", "装 Docker Desktop，用一条命令起 PG / Redis / EMQX / MinIO", "四个容器 healthy，能连上数据库", "60—90 分钟"],
               ["第 4 步", "拉起后端（8000）与前端（5173），完成一次接口联调", "/docs 可打开，前端能调通 /api/health", "约 80 分钟"],
               ["第 5 步", "装 AI 训练环境（仅带 NVIDIA 显卡的机器需要），跑通最小训练并导出 ONNX",
                "CUDA 可用，生成 best.pt 与 best.onnx", "90—150 分钟"],
               ["第 6 步", "配设备模拟（伪视频 + MQTT 模拟器），没有真实硬件也能跑全链路",
                "伪视频可拉流，平台能收到模拟设备数据", "60—90 分钟"],
               ["第 7 步", "跑验收清单，归档环境报告", "15 项快速验收全绿（严格版 25 项见文档 09 第 9 章）", "30 分钟"]],
              [1.4, 6.6, 5.0, 2.0], size=8.5, align_center_cols=(0, 3))
    para(doc, "每一步都有一句“完成标志”。**只有标志达成才继续下一步**，否则后面的问题会互相叠加，"
              "很难判断到底哪一步错了。详细命令与校验方法见文档 09 对应章节。", size=10)

    h(doc, "4 三类环境详细介绍", 1, page_break=True)
    h(doc, "4.1 开发环境（台式机）——干什么、装什么", 2)
    para(doc, "这台机器就是你的“工作台”。所有开发动作都在它上面完成：改业务代码、调试接口、训练与导出模型、"
              "模拟门禁与摄像头数据、在浏览器里看效果。它的特点是“什么都有，但都在容器里，随时可以推倒重来”。")
    add_table(doc, ["组件", "在本机的位置", "作用", "坏了怎么办"],
              [["WSL2 + Ubuntu 24.04", "Windows 子系统", "服务端运行底座，与现场服务器命令一致", "wsl --shutdown 后重启；实在坏了可卸载重装"],
               ["PostgreSQL 16 + pgvector", "容器 campus-pg，端口 5432", "业务数据与人脸向量检索", "删掉数据卷重建 + 用备份恢复"],
               ["Redis 7", "容器 campus-redis，端口 6379", "缓存、会话、通行白名单", "重启容器即可（AOF 会恢复）"],
               ["EMQX 5", "容器 campus-emqx，端口 1883/18083", "模拟与真实设备的 MQTT 接入", "重启容器；配置在数据卷中"],
               ["MinIO", "容器 campus-minio，端口 9000/9001", "事件截图、短视频、报表附件", "重启容器；数据在数据卷中"],
               ["后端 FastAPI", "本机 8000 端口", "业务接口与接口文档", "重启进程；代码在 Git 仓库"],
               ["前端 Vue3", "本机 5173 端口", "管理端页面与驾驶舱", "pnpm dev 重启即可"],
               ["AI 环境（PyTorch/Ultralytics）", "独立虚拟环境 ~/.venvs/cv-train", "模型训练与 ONNX 导出", "删除该虚拟环境重建，不影响业务代码"]],
              [3.4, 3.4, 4.6, 4.0], size=8.5)

    h(doc, "4.2 演示 / 备份环境（笔记本）——干什么、装什么", 2)
    para(doc, "这台机器的唯一任务是**播放**：把已经开发好的平台完整跑起来，用于外出演示、比赛答辩、临时顶替。"
              "它不需要 AI 训练环境，也不需要改代码，因此配置量只有开发环境的三分之一。")
    bullet(doc, "用途一：**断网演示**。竞赛现场网络不可控，平台、数据与模拟设备全部在本机运行，拔掉网线也能演示。")
    bullet(doc, "用途二：**备份运行**。开发机送修或临时需要第二套环境时，直接用它顶上。")
    bullet(doc, "用途三：**分组演示**。多组学生同时演示时，每台笔记本一套环境，互不干扰。")
    add_table(doc, ["要装的", "不要装的", "为什么这样取舍"],
              [["Git、VS Code、Node + pnpm、Python 3.12、WSL2、Docker Desktop、OBS",
                "PyTorch/CUDA、Ultralytics、数据库客户端（可选）",
                "训练统一在台式机完成；权重与 ONNX 文件直接拷过来即可；演示不需要写代码"]],
              [6.6, 4.0, 4.6], size=9)

    h(doc, "4.3 协作环境（同学/学生的电脑）——干什么、装什么", 2)
    para(doc, "协作的本质是**分工而不是复制环境**。对方不需要你的数据库、Docker 与 AI 环境，"
              "只需要能拉代码、能改代码、能连上你的服务。这样对方的电脑装 2 小时就能开工，"
              "也不会出现“我这儿跑不起来”的扯皮。")
    add_table(doc, ["协作角色", "对方装什么", "对方能做什么", "对方连什么"],
              [["前端开发", "Git、VS Code、Node LTS + pnpm、浏览器", "改页面与样式、调接口", "你的后端 8000（写进 .env.development）"],
               ["后端开发", "Git、VS Code、Python 3.12、DBeaver、Apifox", "改接口与业务逻辑、调数据库", "你的数据库 5432 或自建本地库"],
               ["算法 / 标注", "Git、Python 3.11、Ultralytics、标注工具", "标注数据、小规模训练、导出 ONNX", "共享的数据集目录"],
               ["测试 / 演示", "浏览器、MQTTX、Apifox", "多角色测试、接口验证、页面走查", "你的前端 5173 与后端 8000"],
               ["仅查看成果", "浏览器", "查看效果、提意见", "你部署好的地址"]],
              [2.4, 4.6, 4.4, 4.4], size=8.5)
    para(doc, "可直接转发给对方的内容见文档 12《协作开发环境配置指引》；其中包含对方的安装命令、"
              "验收清单与协作红线（不提交口令与人脸数据、分支规范等）。", size=10)

    h(doc, "4.4 服务器环境（云或校内）——干什么、装什么", 2)
    para(doc, "服务器只在两种情况下需要：**要对外访问**（小程序、外网查询）或**要 7×24 运行**（真实门禁与告警）。"
              "开发阶段完全可以不碰它。一条必须守住的原则：**视频与人脸原图不出校园网**，"
              "服务器只接收事件元数据与缩略图，否则带宽费用与合规风险都会失控。")
    add_table(doc, ["服务器能做什么", "服务器不要做什么", "原因"],
              [["业务 API、报表与驾驶舱、小程序后端、数据备份、事件汇总",
                "接收校内摄像头视频流、存人脸原图、做实时 AI 分析",
                "视频按量带宽费用极高；人脸数据出校涉及合规风险；实时分析应在校内边缘完成"]],
              [6.0, 5.4, 4.6], size=9)

    h(doc, "5 快速验收（15 项，半天内应全部通过）", 1, page_break=True)
    para(doc, "在台式机上运行下面的自检脚本，并逐项核对。全绿就说明你可以开始写功能代码了。")
    acceptance_simple(doc)
    add_code(doc, [
        "# 一键自检（在台式机上执行）",
        "python 环境工具\\scripts\\check-env.py --role dev",
        "",
        "# 输出 JSON 便于归档（放进 项目文档/环境记录/）",
        "python 环境工具\\scripts\\check-env.py --role dev --json > env-report-dev.json",
        "",
        "# 期望结尾：合计 N 项，通过 N 项，未通过 0 项，通过率 100.0%",
    ])

    h(doc, "6 三个最常见的卡点（先看，能省你几个小时）", 1)
    add_table(doc, ["卡点现象", "根本原因", "正确做法"],
              [["Docker 拉镜像一直超时", "没有配置镜像加速，或用了失效的公共加速地址",
                "登录阿里云 ACR 控制台复制自己账号的专属加速地址，填到 Docker Desktop 的 registry-mirrors"],
               ["WSL2 装不上或启动失败", "BIOS 没开虚拟化，或与 VMware/Hyper-V 冲突",
                "开机进 BIOS 打开 VT-x（Intel）或 SVM（AMD）；卸载冲突的虚拟化软件；执行 wsl --update"],
               ["训练报 CUDA out of memory", "RTX 3050 只有 8GB 显存",
                "batch 8→4→2，imgsz 640→512→416，开启 AMP；关闭浏览器与容器中的占用进程"],
               ["前端连不上后端（跨域/404）", "代理未配置或后端地址写错",
                "在 vite.config.ts 配置 /api 代理到 8000；跨机器时用 .env.development 的 VITE_API_BASE"]],
              [4.0, 4.6, 7.4], size=9)

    h(doc, "7 四份文档怎么配合使用", 1)
    add_table(doc, ["顺序", "文档/工具", "用途", "什么时候用"],
              [["1", "文档 11（本文档）", "决策与路线：三类环境是什么、先做哪一步", "开始之前，读 10 分钟"],
               ["2", "环境工具/scripts/install-base.ps1", "一键完成通用基线（软件、编码、镜像源、目录、Git）", "每台 Windows 机器第一步"],
               ["3", "文档 09《电脑环境配置详细方案》", "执行手册：每个配置项的命令、预期结果与校验", "配置环境时按章节执行"],
               ["4", "文档 10《环境配置进度与验收台账》", "勾选台账：进度、验收清单、命令速查、口令与 IP 台账", "配置时同步打勾，验收时签字"],
               ["5", "环境工具/scripts/check-env.py", "环境自检，输出通过率与未通过清单", "配置完成后、每次演示前"],
               ["6", "文档 12《协作开发环境配置指引》", "整份转发给协作者，对方照做即可", "需要别人协助开发时"]],
              [1.2, 5.6, 5.8, 3.2], size=9, align_center_cols=(0,))
    note(doc, "本文档只回答“做什么、先做哪个、做到什么程度算完成”；具体命令与排错细节一律以文档 09 为准，避免两份文档出现不一致。")

    doc.save(path)
    print("已生成:", path)


def doc_collab(path):
    doc = Document()
    setup(doc, "协作开发环境配置指引 V1.0")
    cover(doc,
          "“智园卫士”智慧校园管理平台",
          "协作开发环境配置指引（可直接转发给协作同学）",
          [("文档名称", "协作开发环境配置指引"),
           ("文档编号", "ZYWS-ENV-2026-004"),
           ("版本号", "V1.0"),
           ("适用对象", "参与本项目协作开发的同学、学生团队成员、外部协助人员"),
           ("使用说明", "本文档可直接整份转发；按第 2 章确认自己的角色，按第 3 章安装，按第 4 章自检"),
           ("重要提示", "你不必安装数据库、Docker 与 AI 训练环境——那些在项目负责人的台式机上运行"),
           ("编制日期", "2026 年 11 月"),
           ("密级", "内部")],
          doc_kind="协 作 开 发 环 境 配 置 指 引")

    h(doc, "1 你需要知道的三件事", 1, page_break=True)
    bullet(doc, "你不需要一台“什么都有”的电脑。数据库、消息队列、对象存储、AI 训练环境都在项目负责人的台式机上，"
                "你只需要“能写代码 + 能连上他的服务”。")
    bullet(doc, "你安装的全部内容大约 2 小时可以完成，安装包合计不超过 1GB。")
    bullet(doc, "安装完成后，你必须能完成一次“拉取代码 → 启动前端 → 看到后端数据 → 提交一次修改”，"
                "这就是协作环境验收的全部要求。")

    h(doc, "2 第一步：确认你的角色与安装清单", 1)
    add_table(doc, ["角色", "你要安装", "你要做的第一件事"],
              [["前端开发", "Git、VS Code、Node.js LTS、pnpm、浏览器（Chrome/Edge）", "拉取仓库、启动前端、改一个页面文字"],
               ["后端开发", "前端角色全部 + Python 3.12、DBeaver、Apifox", "拉取仓库、启动后端、调通一个接口"],
               ["算法 / 数据标注", "Git、Python 3.11、Ultralytics、标注工具（LabelImg 或 X-AnyLabeling）", "拉取仓库、下载数据集、标注 20 张样本"],
               ["测试 / 演示", "浏览器、MQTTX、Apifox", "打开平台地址，按测试用例走一遍"],
               ["仅查看成果", "浏览器", "打开项目负责人给你的地址查看"]],
              [2.6, 6.4, 6.6], size=9)

    h(doc, "3 第二步：安装与配置（按角色执行）", 1, page_break=True)
    h(doc, "3.1 所有人必做：基础工具与镜像源", 2)
    para(doc, "目的：获得代码管理、编辑器、前端运行时，并把依赖源切到国内，避免安装依赖时反复超时。")
    para(doc, "操作步骤：", indent=False, bold=True, space_after=2)
    bullet(doc, "以管理员身份打开 PowerShell 7（开始菜单搜索 PowerShell，右键“以管理员身份运行”）；", size=10)
    bullet(doc, "逐条执行下面的命令；", size=10)
    bullet(doc, "配置 Git 用户名与邮箱（提交记录会显示是谁改的）。", size=10)
    add_code(doc, [
        "# 1) 安装基础工具（winget 是 Windows 自带的包管理器）",
        "winget install --id Git.Git -e",
        "winget install --id Microsoft.VisualStudioCode -e",
        "winget install --id OpenJS.NodeJS.LTS -e",
        "",
        "# 2) 启用 pnpm（前端包管理器，比 npm 快）",
        "corepack enable",
        "corepack prepare pnpm@latest --activate",
        "",
        "# 3) 配置国内镜像源（重要，能省几十分钟）",
        "npm config set registry https://registry.npmmirror.com",
        "",
        "# 4) 配置 Git 身份",
        "git config --global user.name \"你的姓名\"",
        "git config --global user.email \"你的邮箱\"",
        "git config --global core.autocrlf false",
    ])
    para(doc, "校验（必须通过再继续）：", indent=False, bold=True, space_after=2)
    add_code(doc, [
        "git --version      # 期望输出 git version 2.x",
        "node -v            # 期望输出 v22.x",
        "pnpm -v            # 期望输出 9.x 或 10.x",
        "npm config get registry   # 期望输出 https://registry.npmmirror.com",
    ])

    h(doc, "3.2 前端开发者：拉代码 + 启动前端 + 连后端", 2)
    add_code(doc, [
        "# 1) 拉取仓库（地址由项目负责人提供）",
        "git clone https://gitee.com/<项目负责人提供的仓库地址>/campus-platform.git",
        "cd campus-platform/web-admin",
        "",
        "# 2) 安装依赖（首次约 3—5 分钟）",
        "pnpm install",
        "",
        "# 3) 配置后端地址：新建 .env.development，内容如下",
        "# VITE_API_BASE=http://192.168.1.10:8000        ← 换成项目负责人给你的地址",
        "",
        "# 4) 启动前端",
        "pnpm dev",
        "",
        "# 校验：浏览器打开 http://localhost:5173",
        "#   1. 页面能正常显示",
        "#   2. 打开浏览器开发者工具（F12）→ Network，能看到对后端接口的请求返回 200",
        "#   3. 控制台（Console）没有跨域（CORS）报错",
    ])

    h(doc, "3.3 后端开发者：额外装 Python 与数据库客户端", 2)
    add_code(doc, [
        "winget install --id Python.Python.3.12 -e",
        "winget install --id dbeaver.dbeaver -e",
        "",
        "# 配置 pip 国内源",
        "mkdir \"$env:APPDATA\\pip\" -Force",
        "notepad \"$env:APPDATA\\pip\\pip.ini\"",
        "# 写入以下内容：",
        "# [global]",
        "# index-url = https://pypi.tuna.tsinghua.edu.cn/simple",
        "",
        "# 创建后端环境并安装依赖",
        "cd campus-platform/backend",
        "python -m venv .venv",
        ".venv\\Scripts\\Activate.ps1",
        "pip install -r requirements.txt        # 若项目使用 uv：pip install uv && uv sync",
        "",
        "# 校验：",
        "python -c \"import fastapi; print('后端依赖 OK')\"",
        "uvicorn app.main:app --reload --port 8001   # 用 8001 避免与项目负责人机器冲突",
    ])
    note(doc, "提示：后端开发者可以不连项目负责人的数据库，改为在本机建一个测试库；但表结构必须通过 Alembic 迁移脚本生成，不要手工建表。")

    h(doc, "3.4 算法 / 标注人员：装训练与标注工具", 2)
    add_code(doc, [
        "winget install --id Python.Python.3.11 -e",
        "python -m venv .venv-cv",
        ".venv-cv\\Scripts\\Activate.ps1",
        "",
        "# 有 NVIDIA 显卡（显存 ≥6GB）：按 pytorch.org 生成的 cu12x 命令安装；",
        "# 没有显卡：先装 CPU 版用于标注与验证，训练交给项目负责人的机器",
        "pip install ultralytics opencv-python labelImg",
        "",
        "# 校验：",
        "yolo version",
        "python -c \"from ultralytics import YOLO; print('Ultralytics OK')\"",
    ])

    h(doc, "3.5 测试 / 演示人员：只装验证工具", 2)
    add_code(doc, [
        "# 浏览器用 Chrome 或 Edge 即可；再装两个接口与消息调试工具",
        "# MQTTX：https://mqttx.app",
        "# Apifox：https://apifox.com",
        "",
        "# 校验：能用 Apifox 调通项目负责人给你的 http://<地址>:8000/health",
    ])

    h(doc, "4 第三步：自检与验收（7 项）", 1, page_break=True)
    add_table(doc, ["编号", "验收项", "通过标准"],
              [["C-01", "基础工具就绪", "git / node / pnpm 均有版本输出"],
               ["C-02", "镜像源为国内", "npm registry 为 npmmirror"],
               ["C-03", "代码可拉取", "git clone 成功，且你能 push 自己的分支"],
               ["C-04", "前端可启动", "pnpm dev 后浏览器能打开页面"],
               ["C-05", "能连上负责人后端", "页面能加载后端数据，控制台无跨域报错"],
               ["C-06", "能完成一次提交", "远端仓库能看到你的提交记录"],
               ["C-07", "已知晓协作红线", "确认不会提交口令、密钥、人脸数据"]],
              [1.2, 4.4, 8.4], size=9, align_center_cols=(0,))
    add_code(doc, [
        "# 环境自检脚本（如项目负责人已给你 scripts 目录）",
        "python 环境工具\\scripts\\check-env.py --role client",
        "",
        "# 完成一次提交（验证你能正常协作）",
        "git checkout -b feature/your-name-test",
        "git add .",
        "git commit -m \"test: 验证协作环境\"",
        "git push -u origin feature/your-name-test",
    ])

    h(doc, "5 协作红线（务必遵守）", 1)
    bullet(doc, "**绝不提交**：`.env` 文件、任何口令与密钥、人脸照片与视频样本、数据库备份文件。")
    bullet(doc, "分支规范：每个功能开一个分支，命名 `feature/功能名`；完成前先 `git pull --rebase` 再提交。")
    bullet(doc, "提交信息：写清楚做了什么，例如 `feat: 新增访客预约接口`，不要写 `update`。")
    bullet(doc, "数据库结构：只通过项目里的迁移脚本（Alembic）变更，不要手工建表或改字段。")
    bullet(doc, "人脸等敏感数据：只允许在项目负责人的机器与校内设备上处理，不要下载到个人电脑或上传网盘。")
    bullet(doc, "遇到环境问题先自查：把报错信息完整发到项目群里，不要只说“跑不起来”。")

    h(doc, "6 常见问题（协作场景）", 1)
    add_table(doc, ["现象", "原因", "解决办法"],
              [["pnpm install 卡住或报错", "源不对或 Node 版本不匹配",
                "确认 npm registry 为 npmmirror；用 node -v 确认是 LTS 版本；删除 node_modules 与 pnpm-lock.yaml 后重装"],
               ["页面能开但数据是空的", "后端地址没配对，或不在同一个网络",
                "检查 .env.development 里的 VITE_API_BASE；确认能 ping 通项目负责人的电脑；确认对方防火墙放行了 8000 端口"],
               ["控制台报 CORS 跨域", "前端直接请求了后端，没有走代理",
                "开发环境统一走 /api 代理；跨机器时把后端地址写进 VITE_API_BASE，由负责人放开该来源"],
               ["git push 被拒绝", "没有权限或分支落后",
                "确认已被加入仓库成员；先 git pull --rebase 再 push；仍失败则把完整报错发给负责人"],
               ["Python 装依赖很慢", "未配置 pip 国内源", "按 3.3 节写入 pip.ini 后重试"]],
              [3.4, 3.6, 8.0], size=8.5)

    doc.save(path)
    print("已生成:", path)


if __name__ == "__main__":
    doc_quickstart(r"F:\职业中专\大赛\智慧园区创意\项目文档\11_电脑环境配置总览与快速开始.docx")
    doc_collab(r"F:\职业中专\大赛\智慧园区创意\项目文档\12_协作开发环境配置指引.docx")
