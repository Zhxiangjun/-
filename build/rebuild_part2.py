# -*- coding: utf-8 -*-
"""精确重组 envcfg_part2.py：
  头部           = 当前文件的第 1—580 行（imports + 旧章节 + 新 chapter3）
  extra1（演示） = 当前文件 579—689 行
  extra2（协作） = 备份文件（.bak）中 “第 6 章 外援环境二” 段落
"""
import io
import re

P = r"F:\职业中专\大赛\智慧园区创意\build\envcfg_part2.py"
BAK = r"F:\职业中专\大赛\智慧园区创意\build\envcfg_part2.py.bak"

cur = io.open(P, encoding="utf-8").read().split("\n")
bak = io.open(BAK, encoding="utf-8").read().split("\n")

# 1) 定位当前文件中 chapter3 与 chapter_extra1 的起点
def idx_of(lines, prefix):
    for i, ln in enumerate(lines):
        if ln.startswith(prefix):
            return i
    return None

i_ch3 = idx_of(cur, "def chapter3(doc):")
i_ex1 = idx_of(cur, "def chapter_extra1(doc):")
assert i_ch3 and i_ex1 and i_ch3 < i_ex1

head = cur[:i_ex1]                    # 含 imports / chapter1 / chapter2 / chapter3
ex1 = cur[i_ex1:]                     # 演示环境章节（到文件末尾）
while ex1 and ex1[-1].strip() == "":
    ex1.pop()

# 2) 从备份中提取“第 6 章 外援环境二”整段（到“第 5 章 笔记本 2”之前的函数定义）
start = None
for i, ln in enumerate(bak):
    if 'h(doc, "第 6 章 外援环境二' in ln:
        start = i
        break
assert start is not None, "备份中未找到第 6 章段落"

# 向上回退到其函数定义
d = None
for j in range(start, -1, -1):
    if bak[j].startswith("def "):
        d = j
        break
assert d is not None

# 向下找到旧笔记本 2 章节的函数定义，作为结束
e = None
for j in range(start, len(bak)):
    if bak[j].startswith("def ") and "笔记本 2" in "\n".join(bak[j:j + 4]):
        e = j
        break
if e is None:
    for j in range(start, len(bak)):
        if bak[j].startswith("def chapter5"):
            e = j
            break
assert e is not None and e > d, "未找到段落结束位置"

extra2 = bak[d:e]
while extra2 and extra2[-1].strip() == "":
    extra2.pop()

out = head + extra2 + ["", ""] + ex1 + [""]
res = "\n".join(out)
io.open(P, "w", encoding="utf-8", newline="\n").write(res)

import ast
ast.parse(res)
defs = [l for l in res.split("\n") if l.startswith("def ")]
print("重组完成，行数:", len(out))
print("函数列表:", defs)
