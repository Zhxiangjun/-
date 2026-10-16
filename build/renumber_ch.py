# -*- coding: utf-8 -*-
"""对 gen_envcfg.py 做章节重编号（单机主线版）：
   7 = 服务器环境（原 6）｜ 8 = 教学与机房环境 ｜ 9 = 现场部署环境（原 8 后半段）
   10 = 整体联调与验收（原 9）｜ 附录 → 11
"""
import io
import ast

P = r"F:\职业中专\大赛\智慧园区创意\build\gen_envcfg.py"
src = io.open(P, encoding="utf-8").read()

REPL = [
    # --- 服务器（原第 6 章 → 第 7 章）
    ('h(doc, "第 6 章 阿里云服务器（业务中枢）详细配置", 1, page_break=True)',
     'h(doc, "第 7 章 服务器环境：阿里云与校内服务器（上线阶段才需要）", 1, page_break=True)'),
    ('h(doc, "6.1 实例创建与初始化", 2)', 'h(doc, "7.1 实例创建与初始化", 2)'),
    ('h(doc, "6.2 部署业务服务", 2)', 'h(doc, "7.2 部署业务服务", 2)'),
    ('h(doc, "6.3 云服务器验收清单", 2)', 'h(doc, "7.3 云服务器验收清单", 2)'),
    # --- 现场部署（原第 8 章后半段 → 第 9 章）
    ('h(doc, "8.2 网络与设备接入准备（现场最容易卡住的环节）", 2)',
     'h(doc, "9.2 网络与设备接入准备（现场最容易卡住的环节）", 2)'),
    ('h(doc, "8.3 现场部署包与回滚方案", 2)', 'h(doc, "9.3 现场部署包与回滚方案", 2)'),
    ('h(doc, "8.4 现场上线验收清单", 2)', 'h(doc, "9.4 现场上线验收清单", 2)'),
    # --- 整体联调（原第 9 章 → 第 10 章）
    ('h(doc, "第 9 章 整体联调、自检与验收", 1, page_break=True)',
     'h(doc, "第 10 章 整体联调、自检与验收", 1, page_break=True)'),
    ('h(doc, "9.1 端到端联调场景（必须逐条演示通过）", 2)', 'h(doc, "10.1 端到端联调场景（必须逐条演示通过）", 2)'),
    ('h(doc, "9.2 运行环境自检脚本（check-env.py）", 2)', 'h(doc, "10.2 运行环境自检脚本（check-env.py）", 2)'),
    ('h(doc, "9.3 环境交付物清单（配置完成后归档）", 2)', 'h(doc, "10.3 环境交付物清单（配置完成后归档）", 2)'),
    ('h(doc, "9.4 环境构建完成判定", 2)', 'h(doc, "10.4 环境构建完成判定", 2)'),
    ('h(doc, "附录 A 配置文件模板", 1, page_break=True)', 'h(doc, "第 11 章 附录 A：配置文件模板", 1, page_break=True)'),
    ('h(doc, "附录 B 配套脚本（已在 环境工具/scripts 目录提供）", 1, page_break=True)',
     'h(doc, "第 11 章 附录 B：配套脚本（已在 环境工具/scripts 目录提供）", 1, page_break=True)'),
    ('h(doc, "附录 C 常见问题排查（FAQ）", 1, page_break=True)',
     'h(doc, "第 11 章 附录 C：常见问题排查（FAQ）", 1, page_break=True)'),
    ('h(doc, "附录 D 命令速查表与验收签字", 1, page_break=True)',
     'h(doc, "第 11 章 附录 D：命令速查表与验收签字", 1, page_break=True)'),
    ('h(doc, "B.1 install-base.ps1 使用说明", 2)', 'h(doc, "11.2.1 install-base.ps1 使用说明", 2)'),
    ('h(doc, "D.1 常用命令速查", 2)', 'h(doc, "11.4.1 常用命令速查", 2)'),
    ('h(doc, "D.2 环境验收签字表", 2)', 'h(doc, "11.4.2 环境验收签字表", 2)'),
]

missing = []
for old, new in REPL:
    if old in src:
        src = src.replace(old, new, 1)
    else:
        missing.append(old[:60])

# 第 8 章（教学与机房）已由 fix_ch8.py 写入，标题保持；此处只需确保它是第 8 章
assert 'h(doc, "第 8 章 场景衔接：教学与机房环境（按需）"' in src, "第 8 章标题缺失"

# 第 4 章内的 4.x 小节保持不动（已是主线编号）

ast.parse(src)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
print("重编号完成，未匹配条目:", missing if missing else "无")
heads = [l.strip() for l in src.split("\n") if l.strip().startswith('h(doc, "第 ')]
print("章节标题:")
for hh in heads:
    print("  ", hh[:80])
