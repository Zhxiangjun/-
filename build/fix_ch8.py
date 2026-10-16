# -*- coding: utf-8 -*-
"""修正 envcfg 第 8 章：用完整机房内容替换占位小节（仅替换 function body，保留原本已写好的 8.2/8.3）。"""
import io
import ast

P = r"F:\职业中专\大赛\智慧园区创意\build\gen_envcfg.py"
src = io.open(P, encoding="utf-8").read()

OLD_HEAD = '''def chapter8(doc):
    h(doc, "第 8 章 场景衔接：教学与机房环境（按需）", 1, page_break=True)
    para(doc, "本章说明的是**教学与团队协作场景**下的安排，它与第 4 章的单机主线并不矛盾，两者是同一套平台在"
              "不同使用场景下的两种部署方式：")
    add_table(doc, ["场景", "部署方式", "原因", "对应章节"],
              [["个人开发与调试（你的日常）", "一台台式机装全部环境（数据库、缓存、消息、对象存储均为本机容器）",
                "改动自由、随起随停、不受他人影响，90% 的工作都在这里完成", "第 4 章（主线）"],
               ["带班教学 / 学生实训", "学生机只装客户端，机房内指定 1—2 台机器集中提供依赖服务",
                "避免几十台机器各自装数据库导致密码互串、关机后服务消失、维护成本失控", "本章 8.1—8.3 节"],
               ["校内正式运行", "校内服务器部署生产编排，门禁与视频本地闭环",
                "需要 7×24 运行与真实设备接入，单机无法承担", "第 9 章（服务器环境）"]],
              [3.6, 5.4, 5.4, 2.6], size=9)
    note(doc, "一句话记住：**个人开发用单机全栈，课堂教学用集中服务，正式运行用校内服务器。**"
              "三者使用的代码仓库、compose 文件与配置模板完全相同，差异只写在各自的 .env 里。")
    para(doc, "以下为教学与机房场景下的具体做法（原第 7 章内容）。现场部署环境的配置见第 9 章。")
    doc.add_page_break()
    h(doc, "8.1 机房批量部署：三种方案", 2)
    step(doc, "8.1.1", "服务器系统安装与基础加固",
         "现场服务器将成为校内生产系统，必须先做好系统层面的规范与安全基线。",
         ["安装 Ubuntu Server 24.04 LTS（与开发环境同版本）；",
          "规划磁盘：系统盘与数据盘分离，数据盘挂载到 /data 并写入 /etc/fstab；",
          "配置静态 IP、主机名、NTP 时间同步；",
          "创建运维账号，SSH 仅密钥登录，配置 ufw 只放行必要端口；",
          "BIOS 设置来电自启、开启虚拟化。并在机柜中做好 UPS 与标签管理。"],
         ["重启后数据盘自动挂载；时间同步正常；ufw 规则符合最小开放原则。"],
         ["cat /etc/os-release | head -2",
          "lsblk -f && df -h /data",
          "timedatectl status && chronyc sources",
          "ufw status verbose",
          "",
          "# 断电恢复验证：拔掉电源再上电，服务器应自动启动并恢复服务"])

    step(doc, "8.1.2", "部署平台（生产编排 + 初始化数据）",
         "把开发、测试通过的版本部署到现场，并导入基础数据（组织、场所、人员、设备台账），使系统具备可用状态。",
         ["安装 Docker 与 Compose v2；",
          "克隆代码，配置生产 .env（现场口令与内网地址）；",
          "启动生产编排；",
          "执行数据库迁移与初始化脚本；",
          "导入基础数据（组织、班级、场所、设备台账）。"],
         ["平台服务全部运行；基础数据完整；管理员可登录。"],
         ["cd /opt/campus/deploy && docker compose -f docker-compose.prod.yml up -d",
          "docker compose -f docker-compose.prod.yml ps",
          "cd /opt/campus/backend && uv run alembic upgrade head",
          "uv run python scripts/init_data.py --org --place --device",
          "",
          "# 校验：",
          "curl -s http://127.0.0.1:8000/health",
          "docker exec campus-pg psql -U campus -d campus -c 'select count(*) from md_person;'"])
'''

NEW_HEAD = '''def chapter8(doc):
    h(doc, "第 8 章 场景衔接：教学与机房环境（按需）", 1, page_break=True)
    para(doc, "本章说明的是**教学与团队协作场景**下的安排。它与第 4 章的单机主线并不矛盾，"
              "两者是同一套平台在不同使用场景下的两种部署方式：")
    add_table(doc, ["场景", "部署方式", "原因", "对应章节"],
              [["个人开发与调试（你的日常）", "一台台式机装全部环境（数据库、缓存、消息、对象存储均为本机容器）",
                "改动自由、随起随停、不受他人影响，90% 的工作都在这里完成", "第 4 章（主线）"],
               ["带班教学 / 学生实训", "学生机只装客户端，机房内指定 1—2 台机器集中提供依赖服务",
                "避免几十台机器各自装数据库导致密码互串、关机后服务消失、维护成本失控", "本章 8.1—8.3 节"],
               ["校内正式运行", "校内服务器部署生产编排，门禁与视频本地闭环",
                "需要 7×24 运行与真实设备接入，单机无法承担", "第 9 章（服务器与现场环境）"]],
              [3.6, 5.4, 5.4, 2.6], size=9)
    note(doc, "一句话记住：**个人开发用单机全栈，课堂教学用集中服务，正式运行用校内服务器。**"
              "三者使用的代码仓库、compose 文件与配置模板完全相同，差异只写在各自的 .env 里。")

    h(doc, "8.1 机房标准化环境的三种做法", 2)
    para(doc, "机房场景与个人电脑完全不同：机器多、常无管理员权限、外网可能受限、学生走后环境容易被破坏。"
              "因此机房的目标是“批量部署 + 离线可用 + 可还原”。")
    add_table(doc, ["方案", "适用条件", "做法", "优点", "局限"],
              [["方案 A：机房同传系统", "机房装有联想/惠普/锐捷等品牌同传或还原卡",
                "在一台母盘机上装好环境，用同传系统广播到全部机器", "最快，最省人力", "需要机房具备该系统与管理密码"],
               ["方案 B：系统镜像 + 克隆", "无同传系统但可自由装机",
                "母盘机装好后用 Clonezilla 或微 PE 制作镜像分发", "兼容性好，不依赖品牌软件", "逐台恢复耗时，需硬件型号一致"],
               ["方案 C：脚本化安装", "不能重装系统、只有普通权限",
                "用 winget/Chocolatey 脚本 + 离线安装包 + pip/npm 缓存", "不动系统、可反复执行", "部分软件需管理员权限，耗时长"],
               ["方案 D：便携式环境", "完全无管理员权限、外网受限",
                "便携版 Python + VS Code 便携版 + 离线 wheels 与 pnpm store", "零安装依赖，插 U 盘即用", "性能略低，不适合长期项目"]],
              [2.4, 3.4, 4.6, 2.4, 3.0], size=8.5)
    step(doc, "8.1.1", "在母盘机上安装最小集合环境",
         "机房机器只需“能写代码、能连服务”，不需要本地数据库与容器；装得越少越稳定、越容易还原。",
         ["按第 2 章完成通用基线（精简版）；",
          "配置集中开发服务器的访问地址；",
          "不安装 Docker 与数据库；",
          "把离线包集中放在教学盘（D 盘）目录。"],
         ["母盘机可完成一次完整的开发与作业提交流程。"],
         ["winget install --id Git.Git -e",
          "winget install --id Microsoft.VisualStudioCode -e",
          "winget install --id Python.Python.3.12 -e",
          "winget install --id OpenJS.NodeJS.LTS -e",
          "winget install --id dbeaver.dbeaver -e",
          "",
          "New-Item -ItemType Directory -Force -Path D:\\\\campus\\\\repo, D:\\\\campus\\\\offline, D:\\\\campus\\\\tools",
          "",
          "# 校验：",
          "git --version; python --version; node -v; pnpm -v"])
    step(doc, "8.1.2", "制作离线包（断网机房的关键）",
         "机房外网常被限制，依赖必须提前下载；离线包一次制作、反复使用。",
         ["在联网机器上用 pip download 下载后端依赖 wheels；",
          "用 pnpm fetch 生成前端离线 store；",
          "下载 VS Code 扩展的 vsix；",
          "必要时导出 Docker 镜像 tar；",
          "把全部内容归档到移动固态硬盘。"],
         ["离线包目录结构清晰，且能在断网机器上完成安装。"],
         ["pip download -d D:\\\\campus\\\\offline\\\\wheels -r backend\\\\requirements.txt",
          "cd web-admin && pnpm fetch        # 把 pnpm store 拷到 D:\\\\campus\\\\offline\\\\pnpm-store",
          "# VS Code 扩展：从市场页下载 .vsix 到 D:\\\\campus\\\\offline\\\\vsix",
          "docker save pgvector/pgvector:pg16 redis:7-alpine -o D:\\\\campus\\\\offline\\\\images.tar",
          "",
          "# 校验（在断网机器上）：",
          "pip install --no-index --find-links D:\\\\campus\\\\offline\\\\wheels -r requirements.txt",
          "pnpm install --offline"])
    step(doc, "8.1.3", "批量安装与修复脚本",
         "机房机器多，手工装不可行；脚本化既能批量执行，也能在学生把环境弄坏后一键修复。",
         ["复用本方案配套脚本 install-base.ps1；",
          "编写 repair-env.ps1 用于环境修复；",
          "把脚本与离线包一起放在教学盘；",
          "在母盘机上试运行确认无误。"],
         ["脚本在母盘机与任意一台学生机上均可成功执行。"],
         [".\\\\环境工具\\\\scripts\\\\install-base.ps1 -Role client -SkipWinget",
          "",
          "# repair-env.ps1 应包含：重置 npm/pip 镜像源、重建 Python 虚拟环境、",
          "# 清理并离线重装 node_modules、重置 VS Code 设置、输出修复报告",
          "",
          "# 校验：",
          ".\\\\repair-env.ps1 -WhatIf"])

    h(doc, "8.2 集中开发服务器（机房内一台机器承载依赖服务）", 2)
    step(doc, "8.2.1", "在机房指定一台机器承载依赖服务",
         "若每台学生机都装数据库，会出现三个问题：维护成本高、学生改密码导致互连失败、关机后服务消失。",
         ["选一台配置较好的机器（建议 16GB 内存以上）作为开发服务器；",
          "按第 4.2 节部署 Docker 依赖服务；",
          "为学生分配独立数据库账号与 schema；",
          "把访问地址写入学生机配置文件。"],
         ["学生机能连上数据库与 API，且账号相互隔离。"],
         ["Set-Content \\"$env:USERPROFILE\\\\.campus-dev\\" @\\"",
          "DEV_HOST=192.168.1.10",
          "API=http://192.168.1.10:8000",
          "WEB=http://192.168.1.10:5173",
          "@\\"",
          "",
          "# 校验：",
          "curl -s http://192.168.1.10:8000/health",
          "Test-NetConnection 192.168.1.10 -Port 5432"])
    step(doc, "8.2.2", "还原与作业保存策略",
         "机房有还原卡时，学生的作业必须能存活；无还原卡时，要能快速修复环境。",
         ["要求学生通过 Git 提交作业，而不是只保存在本地；",
          "在母盘或教学盘保留一份“环境修复”脚本与离线包；",
          "约定每次上机前 pull、下机前 push 的操作纪律。"],
         ["还原后环境可用、作业不丢失。"],
         ["# 学生每节课的标准动作",
          "git pull --rebase",
          "# ... 学习与编码 ...",
          "git add . && git commit -m \\"feat: 本次课堂练习\\" && git push",
          "",
          "# 校验：还原后仍能 pull 到自己的提交"])

    h(doc, "8.3 机房验收清单", 2)
    add_table(doc, ["编号", "验收项", "通过标准"],
              [["L-01", "母盘环境完成", "母盘机能独立完成一次开发与作业提交"],
               ["L-02", "批量部署完成", "随机抽查 5 台机器环境一致"],
               ["L-03", "离线包可用", "断网机器可完成依赖安装"],
               ["L-04", "集中开发服务器可用", "数据库与 API 可连，账号隔离"],
               ["L-05", "修复脚本可用", "执行后 5 分钟内恢复可用环境"],
               ["L-06", "作业不丢失", "作业通过 Git 提交，还原不影响成果"],
               ["L-07", "学生账号隔离", "学生 A 无法访问学生 B 的数据"]],
              [1.2, 4.6, 8.4], size=9, align_center_cols=(0,))
'''

assert OLD_HEAD in src, "未找到待替换的章节头"
src = src.replace(OLD_HEAD, NEW_HEAD, 1)
ast.parse(src)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("第 8 章已替换为完整机房内容，语法通过")
print("函数列表:", [l for l in src.split("\n") if l.startswith("def ")])
