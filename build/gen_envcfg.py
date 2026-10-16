# -*- coding: utf-8 -*-
"""《电脑环境配置详细方案》— 第 6—9 章与附录"""
import os
from docx_kit import *
from envcfg_part1 import step, chapter1, chapter2, new_doc
from envcfg_part2 import chapter3 as _ch3, chapter_extra1 as _ex1, chapter_extra2 as _ex2

OUT = r"F:\职业中专\大赛\智慧园区创意\项目文档\09_电脑环境配置详细方案.docx"


def chapter6(doc):
    h(doc, "第 7 章 服务器环境：阿里云与校内服务器（上线阶段才需要）", 1, page_break=True)
    para(doc, "云端承担业务中枢与对外发布：业务 API、数据库、报表、小程序后端、异地备份。"
              "必须明确一条架构原则：云端不接收校内摄像头视频流，只接收事件元数据与缩略图。"
              "视频与门禁必须在校园内本地闭环，否则带宽费用与合规风险都不可控。")
    add_table(doc, ["项目", "起步配置（建议先用）", "规模配置（对师生开放前升级）", "说明"],
              [["实例规格", "2 核 4GB（经济型 e / 通用型 u1）", "4 核 8GB", "先用小规格跑通全流程，再按需升级"],
               ["操作系统", "Ubuntu 24.04 LTS 64 位", "同左", "与 WSL、现场服务器保持同版本"],
               ["系统盘", "ESSD 40—60GB", "ESSD 100GB", "容器镜像与数据库都会占用空间"],
               ["带宽", "按使用流量计费，峰值限速 10Mbps", "按量 + 峰值告警", "固定小带宽在拉镜像时成为瓶颈"],
               ["安全组", "仅放行 22（限来源 IP）、80、443", "同左", "数据库、Redis、MQTT 端口严禁对公网开放"]],
              [2.0, 5.0, 4.6, 4.0], size=9)

    h(doc, "7.1 实例创建与初始化", 2)
    step(doc, "6.1.1", "创建 ECS 实例并完成首次登录",
         "获得一台可公网访问的 Linux 服务器，作为业务与对外服务的载体。",
         ["阿里云控制台购买 ECS：地域选择离学校近的（如华北 2 青岛）、镜像选 Ubuntu 24.04、系统盘 ESSD 60GB；",
          "设置安全组：仅放行 22（来源填你自己的公网 IP）、80、443；",
          "绑定弹性公网 IP（或直接分配）；",
          "用 SSH 密钥或强口令登录。"],
         ["能通过 SSH 登录，外网可访问 80/443 端口。"],
         ["ssh root@<公网IP>",
          "cat /etc/os-release | head -2",
          "# 期望：Ubuntu 24.04 LTS"])

    step(doc, "6.1.2", "系统加固与基础配置",
         "云服务器直接暴露在公网，是攻击重灾区；同时时间与编码必须与开发环境一致，否则通行记录与令牌校验会出错。",
         ["创建运维账号并禁用 root 直接登录；",
          "只允许密钥登录，禁用口令登录（先确认公钥已配置）；",
          "设置时区为北京时间并开启 NTP 同步；",
          "设置中文与 UTF-8 语言环境；",
          "配置 apt 国内源并更新系统。"],
         ["普通账号可 sudo；root 直登被拒；时间与本地一致。"],
         ["adduser deploy && usermod -aG sudo deploy",
          "mkdir -p /home/deploy/.ssh && cp ~/.ssh/authorized_keys /home/deploy/.ssh/ && chown -R deploy:deploy /home/deploy/.ssh",
          "sed -i 's/^#\\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config",
          "sed -i 's/^#\\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config",
          "systemctl restart ssh",
          "",
          "timedatectl set-timezone Asia/Shanghai",
          "timedatectl set-ntp true",
          "locale-gen zh_CN.UTF-8 en_US.UTF-8",
          "",
          "# 校验：",
          "timedatectl status",
          "# 期望：Time zone: Asia/Shanghai (CST, +0800)，System clock synchronized: yes"])

    step(doc, "6.1.3", "安装 Docker 与 Compose v2",
         "与本地开发环境使用同一套容器编排，实现“本地怎么跑，云端就怎么跑”。",
         ["用官方脚本或国内镜像源安装 Docker；", "将运维账号加入 docker 组；", "配置镜像加速。"],
         ["docker 与 docker compose 命令可用。"],
         ["curl -fsSL https://get.docker.com | sh",
          "usermod -aG docker deploy",
          "",
          "# 配置镜像加速（写入 /etc/docker/daemon.json，地址用阿里云 ACR 专属地址）",
          "sudo tee /etc/docker/daemon.json <<'EOF'",
          "{",
          "  \"registry-mirrors\": [\"https://<你的专属地址>.mirror.aliyuncs.com\"]",
          "}",
          "EOF",
          "sudo systemctl restart docker",
          "",
          "# 校验：",
          "docker --version && docker compose version",
          "docker run --rm hello-world"])

    h(doc, "7.2 部署业务服务", 2)
    step(doc, "6.2.1", "部署依赖服务与应用",
         "在云端拉起 PostgreSQL 16、Redis 7、EMQX 5、MinIO（可选 OSS）与后端应用，形成完整业务链。",
         ["把仓库克隆到 /opt/campus；",
          "复制 .env.example 为 .env 并填写云端口令与域名；",
          "用生产编排文件启动；",
          "确认容器状态与健康检查。"],
         ["全部容器 healthy；后端 /health 返回 ok。"],
         ["sudo mkdir -p /opt/campus && sudo chown deploy:deploy /opt/campus",
          "git clone https://gitee.com/<你的仓库>/campus-platform.git /opt/campus",
          "cd /opt/campus/deploy && cp .env.example .env && vim .env",
          "docker compose -f docker-compose.prod.yml up -d",
          "",
          "# 校验：",
          "docker compose -f docker-compose.prod.yml ps",
          "curl -s http://127.0.0.1:8000/health",
          "# 期望：status=ok 且 db/redis 均为 true"])

    step(doc, "6.2.2", "配置 Nginx 与 HTTPS",
         "小程序要求 HTTPS，合规也要求传输加密；证书采用免费证书并配置自动续期。",
         ["安装 Nginx 与 Certbot；",
          "配置站点：静态前端 + /api 反向代理到 8000；",
          "申请并自动续期证书；",
          "强制 HTTP 跳转 HTTPS。"],
         ["浏览器访问域名无证书警告；HTTPS 与跳转均正常。"],
         ["sudo apt install -y nginx certbot python3-certbot-nginx",
          "sudo tee /etc/nginx/sites-available/campus <<'EOF'",
          "server {",
          "  listen 80;",
          "  server_name campus.example.com;",
          "  root /opt/campus/web-admin/dist;",
          "  index index.html;",
          "  location /api/ { proxy_pass http://127.0.0.1:8000/; proxy_set_header Host $host;",
          "                   proxy_set_header X-Real-IP $remote_addr; }",
          "  location / { try_files $uri $uri/ /index.html; }",
          "}",
          "EOF",
          "sudo ln -s /etc/nginx/sites-available/campus /etc/nginx/sites-enabled/",
          "sudo nginx -t && sudo systemctl reload nginx",
          "sudo certbot --nginx -d campus.example.com",
          "",
          "# 校验：",
          "curl -sI https://campus.example.com | head -3",
          "curl -s https://campus.example.com/api/health",
          "sudo certbot renew --dry-run"])

    step(doc, "6.2.3", "配置设备回传通道（MQTT over TLS）",
         "校园设备或校内网关需要把事件推送到云端。明文 MQTT 暴露在公网会被扫描与滥用，必须走 TLS 并限制来源。",
         ["在 EMQX 中启用 8883（MQTT over TLS）并配置证书；",
          "为每台校内网关分配独立的用户名/密码或客户端证书；",
          "ACL 限制主题范围（只能写自己的上行主题）；",
          "安全组放行 8883（建议限定校园出口 IP）。"],
         ["校内网关能用 TLS 连接并上报消息，越权主题被拒绝。"],
         ["# 服务端校验（在云端执行）",
          "docker exec campus-emqx emqx ctl listeners",
          "# 期望：ssl:default 监听 8883",
          "",
          "# 客户端校验（在校内网关或开发机执行）",
          "mosquitto_pub -h campus.example.com -p 8883 --cafile ca.crt \\",
          "  -u gateway01 -P '<口令>' -t 'school/iot/gateway01/event' -m '{\"type\":\"heartbeat\"}'",
          "# 期望：上报成功；尝试向未授权主题发布应被拒绝"])

    step(doc, "6.2.4", "配置自动备份与监控告警",
         "云端同样会发生误删与故障；备份与告警是业务连续性的底线（架构方案要求 RPO ≤15 分钟、RTO ≤2 小时）。",
         ["编写备份脚本：每日 2:00 备份 PostgreSQL 并上传 OSS；",
          "配置 crontab 定时执行；",
          "配置云监控告警（CPU、内存、磁盘、带宽）到手机；",
          "每季度做一次恢复演练并记录。"],
         ["备份文件按时生成并可在 OSS 中看到；告警能真实收到。"],
         ["# /opt/campus/scripts/backup.sh（核心片段）",
          "#!/usr/bin/env bash",
          "set -euo pipefail",
          "TS=$(date +%F_%H%M)",
          "docker exec campus-pg pg_dump -U campus -d campus | gzip > /opt/backup/campus_$TS.sql.gz",
          "find /opt/backup -name 'campus_*.sql.gz' -mtime +30 -delete",
          "# 可选：上传 OSS（ossutil cp /opt/backup/campus_$TS.sql.gz oss://<bucket>/db/）",
          "",
          "# 定时任务",
          "crontab -e",
          "0 2 * * * /opt/campus/scripts/backup.sh >> /var/log/campus-backup.log 2>&1",
          "",
          "# 校验：",
          "ls -lh /opt/backup/ | tail -3",
          "# 恢复演练：把备份导入测试库并比对行数",
          "gunzip -c /opt/backup/campus_<时间>.sql.gz | docker exec -i campus-pg psql -U campus -d campus_test"])

    h(doc, "7.3 云服务器验收清单", 2)
    add_table(doc, ["编号", "验收项", "通过标准"],
              [["K-01", "SSH 安全加固完成", "禁用 root 与口令登录"],
               ["K-02", "时区与时间同步", "Asia/Shanghai 且 NTP 同步正常"],
               ["K-03", "安全组最小开放", "仅 22/80/443（8883 限定来源）"],
               ["K-04", "Docker 与 Compose 可用", "版本命令正常"],
               ["K-05", "依赖服务全起", "docker compose ps 全部 healthy"],
               ["K-06", "后端接口可访问", "/health 返回 ok"],
               ["K-07", "HTTPS 有效", "证书无警告且自动续期可用"],
               ["K-08", "MQTT over TLS 可用", "校内网关可 TLS 上报"],
               ["K-09", "自动备份生效", "备份文件生成且保留策略正确"],
               ["K-10", "恢复演练通过", "从备份恢复的数据与源库一致"],
               ["K-11", "监控告警可达", "手机收到阈值告警"],
               ["K-12", "日志与磁盘", "日志按天切割，磁盘余量告警可用"]],
              [1.2, 4.6, 8.4], size=9, align_center_cols=(0,))


def chapter8(doc):
    h(doc, "第 8 章 教学与机房环境（按需，个人开发不受影响）", 1, page_break=True)
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
              "三者使用的代码仓库、compose 文件与配置模板完全相同，差异只写在各自的 .env 里。机房批量部署与集中服务的完整做法见本章 8.1—8.4 节。")

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
          "New-Item -ItemType Directory -Force -Path D:\\campus\\repo, D:\\campus\\offline, D:\\campus\\tools",
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
         ["pip download -d D:\\campus\\offline\\wheels -r backend\\requirements.txt",
          "cd web-admin && pnpm fetch        # 把 pnpm store 拷到 D:\\campus\\offline\\pnpm-store",
          "# VS Code 扩展：从市场页下载 .vsix 到 D:\\campus\\offline\\vsix",
          "docker save pgvector/pgvector:pg16 redis:7-alpine -o D:\\campus\\offline\\images.tar",
          "",
          "# 校验（在断网机器上）：",
          "pip install --no-index --find-links D:\\campus\\offline\\wheels -r requirements.txt",
          "pnpm install --offline"])
    step(doc, "8.1.3", "批量安装与修复脚本",
         "机房机器多，手工装不可行；脚本化既能批量执行，也能在学生把环境弄坏后一键修复。",
         ["复用本方案配套脚本 install-base.ps1；",
          "编写 repair-env.ps1 用于环境修复；",
          "把脚本与离线包一起放在教学盘；",
          "在母盘机上试运行确认无误。"],
         ["脚本在母盘机与任意一台学生机上均可成功执行。"],
         [".\\环境工具\\scripts\\install-base.ps1 -Role client -SkipWinget",
          "",
          "# repair-env.ps1 应包含：重置 npm/pip 镜像源、重建 Python 虚拟环境、",
          "# 清理并离线重装 node_modules、重置 VS Code 设置、输出修复报告",
          "",
          "# 校验：",
          ".\\repair-env.ps1 -WhatIf"])

    h(doc, "8.2 集中开发服务器（机房内一台机器承载依赖服务）", 2)
    step(doc, "8.2.1", "在机房指定一台机器承载依赖服务",
         "若每台学生机都装数据库，会出现三个问题：维护成本高、学生改密码导致互连失败、关机后服务消失。",
         ["选一台配置较好的机器（建议 16GB 内存以上）作为开发服务器；",
          "按第 4.2 节部署 Docker 依赖服务；",
          "为学生分配独立数据库账号与 schema；",
          "把访问地址写入学生机配置文件。"],
         ["学生机能连上数据库与 API，且账号相互隔离。"],
         ["Set-Content \"$env:USERPROFILE\\.campus-dev\" @\"",
          "DEV_HOST=192.168.1.10",
          "API=http://192.168.1.10:8000",
          "WEB=http://192.168.1.10:5173",
          "@\"",
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
          "git add . && git commit -m \"feat: 本次课堂练习\" && git push",
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

    h(doc, "第 9 章 现场部署环境（校内服务器）详细配置", 1, page_break=True)
    para(doc, "现场环境是项目真正产生价值的环节，也是问题最集中的环节。与前面章节不同，现场的核心难点不在装软件，"
              "而在网络、协议与运维规范。本章按“服务器准备 → 网络与设备准备 → 部署包 → 上线验收”展开；"
              "服务器系统的安装加固与平台部署见 7.1 节，本章不重复。", size=10)

    h(doc, "9.2 网络与设备接入准备（现场最容易卡住的环节）", 2)
    step(doc, "8.2.1", "网络分区与端口放行",
         "视频流量会挤占业务网；门禁设备暴露在业务网也增加风险。按架构方案，业务网、视频网、物联网与门禁网应三网隔离。",
         ["与网络管理员共同确认 VLAN 划分与 IP 规划；",
          "建立 IP 地址台账（编号—位置—IP—MAC—责任人）；",
          "列出平台与设备互访所需端口清单并完成放行；",
          "按 1080p 单路 2—4Mbps 估算带宽并预留 30% 余量。"],
         ["设备与平台互通，业务网未受视频流量影响。"],
         ["# 本机网络校验",
          "ip a && ip route",
          "",
          "# 设备可达性校验（把 IP 换成台账中的设备地址）",
          "ping -c 3 <摄像机IP>",
          "nc -zv <门禁IP> 80",
          "nc -zv <摄像机IP> 554",
          "",
          "# 带宽实测（在校内网与设备同网段执行）",
          "curl -o /dev/null -s -w '下载速度: %{speed_download} B/s\\n' rtsp://<摄像机IP>/stream --max-time 10"])

    step(doc, "8.2.2", "设备协议确认与联调准备",
         "协议不开放是硬件对接最常见的死结。必须在采购与联调前书面确认，并准备好兜底方案。",
         ["逐类设备确认：门禁支持韦根/HTTP/开放 SDK；摄像机支持 GB/T 28181 或 ONVIF/RTSP；"
          "车辆道闸与车牌识别开放协议；传感器支持 Modbus/MQTT；消防主机开放报警输出；",
          "记录厂商技术对接人与联系方式；",
          "对不支持标准协议的设备准备开关量兜底方案；",
          "约定施工窗口，避开上课与考试时段。"],
         ["每类设备都拿到可用的协议文档或对接人；无死结设备。"],
         ["# 设备发现与协议探测",
          "# 摄像机：用 ONVIF Device Manager 扫描网段，记录 RTSP 地址",
          "ffprobe -rtsp_transport tcp -i rtsp://<用户>:<口令>@<摄像机IP>:554/Streaming/Channels/101",
          "",
          "# 门禁：确认管理口与协议",
          "nc -zv <门禁IP> 80",
          "curl -s -m 5 http://<门禁IP>/ -o /dev/null -w '%{http_code}'",
          "",
          "# 传感器：Modbus TCP 探测（端口 502）",
          "nc -zv <传感器网关IP> 502"])

    h(doc, "9.3 现场部署包与回滚方案", 2)
    add_table(doc, ["内容", "制作方式", "用途"],
              [["操作系统安装盘", "Ubuntu Server 24.04 ISO + 启动 U 盘", "服务器裸装"],
               ["离线依赖仓库", "本地 apt 镜像或 deb 包目录 + Docker 镜像 tar", "无外网环境安装"],
               ["应用交付包", "compose 文件 + 应用镜像 + .env 模板 + 初始化 SQL", "一条命令起平台"],
               ["初始化脚本", "建库建表、创建管理员、导入基础数据", "缩短现场调试时间"],
               ["配置模板", "nginx、证书、定时备份、日志切割、监控采集", "现场只改域名与口令"],
               ["验收与培训材料", "部署手册、运维手册、故障手册、三类培训课件", "验收与知识转移"],
               ["回滚方案", "上一版本镜像与数据库备份 + 回滚脚本", "升级失败 15 分钟内可退回"]],
              [2.4, 6.6, 5.2], size=9)
    step(doc, "8.3.1", "制作并验证回滚方案",
         "现场升级一旦失败，能不能快速退回去决定了故障时长。回滚方案必须演练过，而不是写在纸上。",
         ["保留上一版本的容器镜像 tag；",
          "升级前做一次数据库全量备份；",
          "编写回滚脚本（切回旧镜像 + 必要时恢复数据库）；",
          "在测试环境演练一次回滚。"],
         ["演练回滚时长 ≤15 分钟，业务恢复且数据无丢失。"],
         ["# 升级前",
          "docker compose -f docker-compose.prod.yml exec -T campus-pg pg_dump -U campus -d campus | gzip > /opt/backup/pre_upgrade_$(date +%F_%H%M).sql.gz",
          "docker tag campus/backend:latest campus/backend:rollback",
          "",
          "# 回滚（示例）",
          "docker compose -f docker-compose.prod.yml down",
          "docker tag campus/backend:rollback campus/backend:latest",
          "docker compose -f docker-compose.prod.yml up -d",
          "# 必要时恢复数据库",
          "gunzip -c /opt/backup/pre_upgrade_<时间>.sql.gz | docker exec -i campus-pg psql -U campus -d campus",
          "",
          "# 校验：",
          "curl -s http://127.0.0.1:8000/health",
          "docker compose -f docker-compose.prod.yml ps"])

    h(doc, "9.4 现场上线验收清单", 2)
    add_table(doc, ["编号", "验收项", "通过标准"],
              [["F-01", "平台服务全起", "容器全部 healthy，重启后自动恢复"],
               ["F-02", "数据库与基础数据", "组织、场所、人员、设备台账导入完整无重复"],
               ["F-03", "门禁联调", "现场刷脸/刷卡 P95 ≤300ms"],
               ["F-04", "断网离线放行", "断网 30 分钟仍可通行且记录完整补传"],
               ["F-05", "视频接入", "按点位清单逐个确认，预览延时 ≤1.5 秒"],
               ["F-06", "AI 算法达标", "按验收样本测试，准确率与误报率符合要求"],
               ["F-07", "通知通道", "短信/微信真实送达并可查回执"],
               ["F-08", "定时任务", "归寝判定、报表、备份按计划执行"],
               ["F-09", "备份与回滚演练", "RPO ≤15 分钟、RTO ≤2 小时；回滚 ≤15 分钟"],
               ["F-10", "培训与文档移交", "三类角色培训签到，手册与账号清单齐全"]],
              [1.2, 4.2, 8.6], size=9, align_center_cols=(0,))


def chapter9(doc):
    h(doc, "第 10 章 整体联调、自检与验收", 1, page_break=True)
    para(doc, "所有机器配置完成后，必须做一次端到端联调，确认“设备/模拟设备 → 平台 → 前端 → 通知”的完整链路可用，"
              "并用配套自检脚本留下可追溯的环境记录。这是进入功能开发的最后一道门。")

    h(doc, "10.1 端到端联调场景（必须逐条演示通过）", 2)
    add_table(doc, ["编号", "联调场景", "操作步骤", "通过标准"],
              [["E-01", "人员建档与门禁通行", "在平台新增一名测试人员并授权 → 用桩服务或模拟设备上报该人通行", "平台生成通行记录，人员在校状态变为在校"],
               ["E-02", "请假与离校拦截", "提交请假申请并审批通过 → 上报该人离校通行", "放行成功并记录；未请假人员离校应被拦截至事件"],
               ["E-03", "通行即考勤", "上报教职工上班与下班通行记录", "考勤自动生成签到与签退，无需二次打卡"],
               ["E-04", "AI 事件闭环", "向伪视频流播放含烟火视频 → 算法识别", "生成事件并派单，处置后状态闭环，证据留档"],
               ["E-05", "设备心跳与离线告警", "停止模拟设备上报", "平台在阈值时间内产生设备离线告警"],
               ["E-06", "通知链路", "触发未归预警规则", "站内消息立即到达；短信/微信通道在配置后送达并可查回执"],
               ["E-07", "权限与数据隔离", "用学生账号访问管理接口", "返回 403，且审计日志有记录"],
               ["E-08", "断网可用性", "断开平台与门禁网络 30 分钟", "门禁离线放行正常，恢复后记录完整补传"],
               ["E-09", "备份与恢复", "对云端或现场库做一次恢复演练", "恢复数据与源库一致，耗时满足 RTO"],
               ["E-10", "性能抽测", "对门禁鉴权接口施加并发压力", "P95 响应 ≤300ms，无失败请求"]],
              [1.2, 3.4, 5.4, 5.4], size=8.5, align_center_cols=(0,))

    h(doc, "10.2 运行环境自检脚本（check-env.py）", 2)
    para(doc, "本方案配套提供环境自检脚本，覆盖系统信息、命令行工具、依赖服务端口、Python 依赖与 GPU、工程目录五类检查，"
              "并给出通过率与未通过项清单。建议在每台机器配置完成后、以及每次重要演示前各运行一次。")
    add_code(doc, [
        "# 基本用法（在三台机器与服务器上均可运行）",
        "python 环境工具\\scripts\\check-env.py                  # 全量自检（默认 dev 角色）",
        "python 环境工具\\scripts\\check-env.py --role server      # 笔记本 1 / 现场服务器",
        "python 环境工具\\scripts\\check-env.py --role client      # 笔记本 2 / 学生机",
        "python 环境工具\\scripts\\check-env.py --role cloud       # 云服务器",
        "python 环境工具\\scripts\\check-env.py --json > env.json  # 输出 JSON，便于机房批量收集",
        "",
        "# 退出码：0 = 全部通过；1 = 存在未通过项（可用于批处理判定）",
        "",
        "# 期望输出示例（节选）",
        "  [ OK ] 操作系统        Windows-11-10.0.26100-SP0",
        "  [ OK ] Python 版本     3.12.14",
        "  [ OK ] 磁盘可用        C: 可用 228.2 GB / 共 465.6 GB；D: 可用 232.9 GB / 共 306.0 GB",
        "  [ OK ] 命令 docker     Docker version 27.x",
        "  [ OK ] 端口 5432 PostgreSQL   开放",
        "  [ OK ] CUDA 可用       是，NVIDIA GeForce RTX 3050，CUDA 12.4",
        "  合计 46 项，通过 46 项，未通过 0 项，通过率 100.0%",
    ])

    h(doc, "10.3 环境交付物清单（配置完成后归档）", 2)
    add_table(doc, ["序号", "交付物", "来源", "归档位置"],
              [["1", "各机器环境报告 env-report.txt", "install-base.ps1 自动生成", "项目文档/环境记录/"],
               ["2", "各机器自检结果 env.json", "check-env.py --json", "项目文档/环境记录/"],
               ["3", "机器信息与分工登记表", "第 2.1.1 节记录", "环境准备与选型核对表.xlsx"],
               ["4", "服务口令与密钥清单（加密保存）", "配置过程登记", "密码管理表（不入仓库）"],
               ["5", "IP 地址台账与设备清单", "现场勘察", "项目文档/环境记录/"],
               ["6", "端口放行清单", "与网络管理员确认", "项目文档/环境记录/"],
               ["7", "部署包与离线包清单", "第 7、8 章制作", "移动固态硬盘 + 云端备份"],
               ["8", "备份与回滚演练记录", "第 6、8 章演练", "项目文档/环境记录/"],
               ["9", "环境验收签字表", "附录 D", "项目文档/环境记录/"]],
              [1.0, 5.0, 4.0, 4.0], size=9, align_center_cols=(0,))

    h(doc, "10.4 环境构建完成判定", 2)
    para(doc, "同时满足以下五条，方可认定环境构建完成并进入功能开发：")
    bullet(doc, "三台电脑的通用基线 13 项校验全部通过；")
    bullet(doc, "台式机 25 项、笔记本 1 共 10 项、笔记本 2 共 7 项验收清单全部通过；")
    bullet(doc, "第 9.1 节端到端联调 10 个场景全部可演示；")
    bullet(doc, "check-env.py 在每台目标机器上通过率 100%（或未通过项均为“非本机职责”的可选组件）；")
    bullet(doc, "环境报告、自检结果、口令清单、IP 台账、演练记录全部归档。")


def appendix(doc):
    h(doc, "第 11 章 附录 A：配置文件模板", 1, page_break=True)
    h(doc, "A.1 后端 .env 模板（backend/.env.example）", 2)
    add_code(doc, [
        "# ===== 应用 =====",
        "APP_ENV=dev                      # dev / test / prod",
        "APP_NAME=smart-campus",
        "APP_PORT=8000",
        "LOG_LEVEL=INFO",
        "TZ=Asia/Shanghai",
        "",
        "# ===== 数据库（PostgreSQL 16 + pgvector）=====",
        "DB_URL=postgresql+asyncpg://campus:CHANGE_ME@localhost:5432/campus",
        "DB_POOL_SIZE=10",
        "DB_MAX_OVERFLOW=20",
        "",
        "# ===== 缓存（Redis 7）=====",
        "REDIS_URL=redis://:CHANGE_ME@localhost:6379/0",
        "",
        "# ===== 消息（EMQX 5 / MQTT）=====",
        "MQTT_HOST=localhost",
        "MQTT_PORT=1883",
        "MQTT_USERNAME=",
        "MQTT_PASSWORD=",
        "MQTT_TOPIC_PREFIX=iot",
        "",
        "# ===== 对象存储（MinIO）=====",
        "MINIO_ENDPOINT=localhost:9000",
        "MINIO_ACCESS_KEY=CHANGE_ME",
        "MINIO_SECRET_KEY=CHANGE_ME",
        "MINIO_BUCKET_EVENT=event",
        "MINIO_SECURE=false",
        "",
        "# ===== 鉴权 =====",
        "JWT_SECRET=请用 openssl rand -hex 32 生成",
        "JWT_ALGORITHM=HS256",
        "JWT_EXPIRE_MINUTES=720",
        "",
        "# ===== AI 推理（ONNX Runtime）=====",
        "AI_MODEL_DIR=/opt/campus/models",
        "AI_ONNX_PROVIDER=CUDAExecutionProvider   # 无 GPU 时改为 CPUExecutionProvider",
        "AI_DRAW_FPS=3",
        "",
        "# ===== 通知通道 =====",
        "SMS_ACCESS_KEY=",
        "SMS_SIGN_NAME=",
        "WECHAT_APPID=",
        "WECHAT_SECRET=",
    ])

    h(doc, "A.2 Nginx 生产站点配置（deploy/nginx/prod.conf）", 2)
    add_code(doc, [
        "upstream campus_api { server 127.0.0.1:8000; keepalive 32; }",
        "",
        "server {",
        "    listen 80;",
        "    server_name campus.example.com;",
        "    return 301 https://$host$request_uri;",
        "}",
        "",
        "server {",
        "    listen 443 ssl http2;",
        "    server_name campus.example.com;",
        "    ssl_certificate     /etc/letsencrypt/live/campus.example.com/fullchain.pem;",
        "    ssl_certificate_key /etc/letsencrypt/live/campus.example.com/privkey.pem;",
        "",
        "    root /opt/campus/web-admin/dist;",
        "    index index.html;",
        "    gzip on;",
        "    gzip_types text/css application/javascript application/json image/svg+xml;",
        "",
        "    # 前端静态资源（带哈希的产物长缓存）",
        "    location /assets/ { expires 30d; add_header Cache-Control \"public, immutable\"; }",
        "",
        "    # 接口反向代理",
        "    location /api/ {",
        "        proxy_pass http://campus_api/;",
        "        proxy_http_version 1.1;",
        "        proxy_set_header Host $host;",
        "        proxy_set_header X-Real-IP $remote_addr;",
        "        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
        "        proxy_read_timeout 60s;",
        "        limit_req zone=api burst=20 nodelay;",
        "    }",
        "",
        "    # 单页应用回退",
        "    location / { try_files $uri $uri/ /index.html; }",
        "}",
        "",
        "# 限流区定义（放在 http 块中）",
        "limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;",
    ])

    h(doc, "A.3 生产编排与备份脚本要点", 2)
    add_table(doc, ["文件", "要点"],
              [["deploy/docker-compose.prod.yml", "在 dev 版本基础上增加 backend 与 nginx 服务；所有服务加 healthcheck 与 restart: unless-stopped；数据卷使用命名卷；环境变量全部来自 .env；关键服务限制 CPU/内存上限"],
               ["deploy/prometheus.yml", "抓取 backend:8000/metrics 与 node_exporter；设置 scrape_interval 15s；配置告警规则文件"],
               ["scripts/backup.sh", "pg_dump 全量备份 + 压缩 + 保留 30 天 + 可选上传 OSS；执行结果写日志；失败时返回非零退出码"],
               ["scripts/init_data.py", "组织与场所建模、管理员账号、设备台账、字典与参数初始化；幂等可重复执行"],
               [".gitignore", "忽略 .env、.venv、node_modules、__pycache__、runs/、*.pt、*.onnx、数据集目录、dist/"]],
              [5.0, 9.2], size=9)

    h(doc, "第 11 章 附录 B：配套脚本（环境工具/scripts 目录）", 2)
    para(doc, "为避免手工输入遗漏，本方案配套两个脚本，可直接使用；建议先阅读再执行，脚本支持 DryRun 与角色参数。")
    add_table(doc, ["脚本", "用途", "适用机器", "用法"],
              [["install-base.ps1", "一键完成通用基线：虚拟化检查、winget 批量安装、UTF-8、镜像源、目录规范、Git 配置、Python/Node/uv、环境报告生成",
                "三台 Windows 机器", ".\\install-base.ps1 -Role dev（管理员 PowerShell）"],
               ["check-env.py", "环境自检：系统信息、命令行工具、依赖服务端口、Python 依赖与 CUDA、工程目录，输出通过率与未通过清单",
                "全部机器", "python check-env.py --role dev"]],
              [3.0, 6.6, 2.4, 4.6], size=9)

    h(doc, "11.2.1 install-base.ps1 使用说明", 2)
    add_code(doc, [
        "# 以管理员身份打开 PowerShell 7 后执行",
        "Set-ExecutionPolicy -Scope Process Bypass -Force",
        "cd F:\\职业中专\\大赛\\智慧园区创意\\环境工具\\scripts",
        "",
        ".\\install-base.ps1                    # 交互式选择机器角色",
        ".\\install-base.ps1 -Role dev          # 台式机（全量，含 Docker 与 Python 双版本）",
        ".\\install-base.ps1 -Role server       # 笔记本 1（服务宿主）",
        ".\\install-base.ps1 -Role client       # 笔记本 2（客户端）",
        ".\\install-base.ps1 -Role dev -SkipWinget     # 只做环境变量与配置，不装软件",
        ".\\install-base.ps1 -Role dev -DryRun         # 只打印将要执行的动作，不改系统",
        "",
        "# 执行完成后会生成 D:\\campus\\env-report.txt，请归档到 项目文档/环境记录/",
    ])

    h(doc, "第 11 章 附录 C：常见问题排查（FAQ）", 2)
    add_table(doc, ["现象", "可能原因", "排查与解决办法"],
              [["winget 命令不存在", "未安装应用安装程序，或 PowerShell 版本过低",
                "Microsoft Store 安装“应用安装程序”；或从 aka.ms/getwinget 下载；仍不行改用离线安装包"],
               ["WSL2 安装失败或启动报错", "BIOS 未开虚拟化；与 VMware/Hyper-V 冲突；内核过旧",
                "开启 VT-x/SVM；卸载冲突的虚拟化组件；执行 wsl --update 升级内核；必要时 wsl --shutdown 后重试"],
               ["Docker Desktop 启动后一直转圈", "WSL2 后端未就绪；内存分配不足；镜像加速配置错误",
                "确认 wsl -l -v 正常；提高 Docker 内存分配；检查 daemon.json 语法并重启 Docker"],
               ["docker pull 超时", "无镜像加速或加速地址失效",
                "使用阿里云 ACR 专属加速地址；或用第 7 章离线 tar 包 docker load 导入"],
               ["pip 安装极慢或 SSL 报错", "未配国内源；网络有代理",
                "检查 pip config list；必要时设置 HTTPS_PROXY；优先使用 uv 安装"],
               ["pnpm/npm 安装依赖失败", "源不对、锁文件与 Node 版本不匹配、node_modules 损坏",
                "确认 registry 为 npmmirror；统一 Node LTS；删除 node_modules 与 lock 后重装"],
               ["Python 中文输出乱码或报错", "编码不一致（GBK/UTF-8）",
                "设置 PYTHONUTF8=1 与 PYTHONIOENCODING=utf-8；文件统一存为 UTF-8；终端用 Windows Terminal"],
               ["torch.cuda.is_available() 返回 False", "装成了 CPU 版；驱动过旧；环境变量冲突",
                "按 pytorch.org 生成的 cu12x 命令重装；nvidia-smi 确认驱动；创建全新虚拟环境排除冲突"],
               ["训练报 CUDA out of memory", "RTX 3050 8GB 显存不足",
                "batch 8→4→2；imgsz 640→512→416；开启 AMP；关闭浏览器与占用显存的容器；减小数据集分辨率"],
               ["ONNX 推理结果与 PyTorch 不一致", "opset、输入尺寸、归一化或 BGR/RGB 顺序不一致",
                "统一 opset 17 与 640×640 输入；核对均值方差与通道顺序；用同一张图逐层比对，偏差应 ≤1e-3"],
               ["容器内服务本机访问不到", "端口未映射；服务监听 127.0.0.1；Windows 防火墙拦截",
                "检查 compose 的 ports 映射；服务改为监听 0.0.0.0；放行对应端口；用 docker logs 看启动日志"],
               ["数据库时间比北京时间少 8 小时", "容器未设时区",
                "compose 中加 TZ=Asia/Shanghai；数据库连接与 ORM 统一时区；重新创建容器生效"],
               ["EMQX 无法用默认口令登录", "EMQX 5 首次启动已生成随机口令或环境变量已设置",
                "用 docker logs campus-emqx 查看初始口令，或通过环境变量 EMQX_DASHBOARD__DEFAULT_PASSWORD 指定"],
               ["录像或截图上云后费用激增", "误将视频流或原图上传公有云",
                "立即改为仅上报事件元数据与缩略图；原图保留在校内；为 OSS 设置生命周期与流量告警"],
               ["机房学生互相看不到对方数据是对的，但看到别人数据", "共用数据库账号或未启用行级权限",
                "每人独立账号与 schema；开启行级权限校验；用权限测试用例回归"],
               ["演示现场网络不通导致无法演示", "演示环境依赖外网",
                "按 4.2.1 构建离线演示环境（本地镜像 + 静态产物 + Nginx）；准备移动热点与录屏备份"]],
              [3.0, 3.6, 7.6], size=8.5)

    h(doc, "第 11 章 附录 D：命令速查表与验收签字", 2)
    h(doc, "11.4.1 常用命令速查", 2)
    add_table(doc, ["场景", "命令"],
              [["检查虚拟化", "(Get-CimInstance Win32_Processor).VirtualizationFirmwareEnabled"],
               ["WSL 发行版状态", "wsl -l -v"],
               ["进入 WSL", "wsl -d Ubuntu-24.04"],
               ["Docker 状态与加速", "docker info | Select-String 'Server Version','Registry Mirrors'"],
               ["启动依赖服务（开发）", "docker compose -f docker-compose.dev.yml up -d"],
               ["查看容器状态", "docker compose -f docker-compose.dev.yml ps"],
               ["查看某服务日志", "docker logs -f campus-pg"],
               ["进入数据库", "docker exec -it campus-pg psql -U campus -d campus"],
               ["Redis 连通性", "docker exec campus-redis redis-cli -a <口令> ping"],
               ["MinIO 健康检查", "curl -s http://localhost:9000/minio/health/live"],
               ["启动后端", "uv run uvicorn app.main:app --reload --port 8000"],
               ["数据库迁移", "uv run alembic upgrade head"],
               ["启动前端", "pnpm dev --host"],
               ["构建前端产物", "pnpm build"],
               ["验证 GPU", "nvidia-smi; python -c \"import torch;print(torch.cuda.is_available())\""],
               ["最小训练", "yolo detect train model=yolo11n.pt data=data.yaml epochs=10 imgsz=640 batch=8 device=0 amp=True"],
               ["导出 ONNX", "yolo export model=best.pt format=onnx opset=17 dynamic=True simplify=True"],
               ["伪视频推流", "ffmpeg -re -stream_loop -1 -i sample.mp4 -c copy -f rtsp rtsp://localhost:8554/cam1"],
               ["环境自检", "python 环境工具\\scripts\\check-env.py --role dev"],
               ["云端备份", "docker exec campus-pg pg_dump -U campus -d campus | gzip > backup.sql.gz"]],
              [3.6, 10.6], size=9)

    h(doc, "11.4.2 环境验收签字表", 2)
    add_table(doc, ["环境", "责任人", "验收日期", "通过项/总项", "遗留问题", "签字"],
              [["台式机（主力开发机）", "", "", "___ / 25", "", ""],
               ["笔记本 1（服务宿主）", "", "", "___ / 10", "", ""],
               ["笔记本 2（客户端）", "", "", "___ / 7", "", ""],
               ["阿里云 ECS", "", "", "___ / 12", "", ""],
               ["学生机房", "", "", "___ / 7", "", ""],
               ["现场服务器", "", "", "___ / 10", "", ""],
               ["端到端联调场景", "", "", "___ / 10", "", ""],
               ["整体自检（check-env.py）", "", "", "___ / 46", "", ""]],
              [4.0, 2.2, 2.2, 2.2, 2.6, 1.8], size=9)
    note(doc, "本表打印后由责任人与指导教师签字，扫描件与电子版一并归档到 项目文档/环境记录/。环境构建完成的判定标准见第 9.4 节。")


if __name__ == "__main__":
    doc = new_doc()
    chapter1(doc)
    chapter2(doc)
    chapter3(doc)
    chapter4(doc)
    chapter5(doc)
    chapter6(doc)
    chapter7(doc)
    chapter8(doc)
    chapter9(doc)
    appendix(doc)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc.save(OUT)
    print("已生成:", OUT)
