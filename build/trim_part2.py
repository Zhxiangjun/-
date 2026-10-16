# -*- coding: utf-8 -*-
"""裁掉 envcfg_part2.py 中已废弃的旧版笔记本章节（保留新编排的 5、6 章）。"""
import io
import re

P = r"F:\职业中专\大赛\智慧园区创意\build\envcfg_part2.py"
src = io.open(P, encoding="utf-8").read()
lines = src.split("\n")

# 找到“旧笔记本 1 章节”的起始行：第一次出现 chapter5.3 之前、且属于旧的 4.1 节标题
start = None
for i, ln in enumerate(lines):
    if ln.startswith('    h(doc, "4.1 基础配置（复用第 2 章 + 本机特有设置）"'):
        start = i
        break
assert start is not None, "未找到旧章节起点"

# 向上回退到该函数定义行（def chapter_extra1/def chapter4 等）
def_idx = None
for j in range(start, -1, -1):
    if lines[j].startswith("def ") and "doc" in lines[j]:
        def_idx = j
        break
assert def_idx is not None, "未找到函数定义"
print("裁剪起点行号:", def_idx + 1, "→", lines[def_idx])

new_lines = lines[:def_idx]
while new_lines and new_lines[-1].strip() == "":
    new_lines.pop()
new_lines.append("")
res = "\n".join(new_lines)
io.open(P, "w", encoding="utf-8", newline="\n").write(res)
print("裁剪后行数:", len(new_lines))
