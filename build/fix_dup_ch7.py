# -*- coding: utf-8 -*-
"""收尾修正：
   1) 删除重复的旧 chapter7（学生机房章节，内容已并入第 8 章）
   2) 为第 9 章（现场部署）补上章标题
   3) 把第 8 章内的“原第 7 章内容”表述改为正式引用
"""
import io
import ast
import re

P = r"F:\职业中专\大赛\智慧园区创意\build\gen_envcfg.py"
src = io.open(P, encoding="utf-8").read()
lines = src.split("\n")

# ---------- 1) 删除 chapter7 整个函数 ----------
start = None
for i, l in enumerate(lines):
    if l.startswith("def chapter7(doc):"):
        start = i
        break
assert start is not None, "未找到 chapter7"
end = None
for j in range(start + 1, len(lines)):
    if lines[j].startswith("def chapter8(doc):"):
        end = j
        break
assert end is not None, "未找到 chapter8 起始"
del lines[start:end]
src = "\n".join(lines)
print("已删除重复的 chapter7，行数:", len(lines))

# ---------- 2) 第 9 章章标题 ----------
if 'h(doc, "第 9 章 现场部署环境（校内服务器）详细配置", 1, page_break=True)' not in src:
    anchor = '    h(doc, "9.2 网络与设备接入准备（现场最容易卡住的环节）", 2)'
    assert anchor in src, "未找到 9.2 锚点"
    src = src.replace(
        anchor,
        '    h(doc, "第 9 章 现场部署环境（校内服务器）详细配置", 1, page_break=True)\n'
        '    para(doc, "现场环境是项目真正产生价值的环节，也是问题最集中的环节。与前面章节不同，现场的核心难点不在装软件，"\n'
        '              "而在网络、协议与运维规范。本章按“服务器准备 → 网络与设备准备 → 部署包 → 上线验收”展开；"\n'
        '              "服务器系统的安装加固与平台部署见 7.1 节，本章不重复。", size=10)\n\n'
        + anchor,
        1)
    print("已补第 9 章章标题与引言")

# ---------- 3) 表述修正 ----------
src = src.replace("以下为教学与机房场景下的具体做法（原第 7 章内容）。现场部署环境的配置见第 9 章。",
                  "以下为教学与机房场景下的具体做法；现场部署环境的配置见第 9 章。")
src = src.replace("三者使用的代码仓库、compose 文件与配置模板完全相同，差异只写在各自的 .env 里。",
                  "三者使用的代码仓库、compose 文件与配置模板完全相同，差异只写在各自的 .env 里。"
                  "机房批量部署与集中服务的完整做法见本章 8.1—8.4 节。")

ast.parse(src)
io.open(P, "w", encoding="utf-8", newline="\n").write(src)
heads = [l.strip() for l in src.split("\n") if l.strip().startswith('h(doc, "第 ')]
print("最终章节标题:")
for hh in heads:
    print("  ", hh[:78])
print("函数列表:", [l for l in src.split("\n") if l.startswith("def ")])
