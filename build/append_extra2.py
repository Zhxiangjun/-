# -*- coding: utf-8 -*-
"""为 envcfg_part2.py 追加“外援环境二：协作同学/学生电脑”章节（chapter_extra2）。"""
import io

P = r"F:\职业中专\大赛\智慧园区创意\build\envcfg_part2.py"

BLOCK = '''

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
          "git config --global user.name \\"对方姓名\\"",
          "git config --global user.email \\"对方邮箱\\"",
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
'''

src = io.open(P, encoding="utf-8").read()
if "def chapter_extra2" in src:
    print("已存在 chapter_extra2，跳过")
else:
    src = src.rstrip("\n") + "\n" + BLOCK
    io.open(P, "w", encoding="utf-8", newline="\n").write(src)
    import ast
    ast.parse(src)
    print("已追加 chapter_extra2，语法通过")
    print("函数列表:", [l for l in src.split("\n") if l.startswith("def ")])
