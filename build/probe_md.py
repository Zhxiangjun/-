# -*- coding: utf-8 -*-
import re

paths = [r"F:\职业中专\大赛\智慧园区创意\02_智慧园区平台总体技术架构方案.md",
         r"F:\职业中专\大赛\智慧园区创意\05_智园卫士商业计划书.md"]
TICK = "`"
for p in paths:
    t = open(p, encoding="utf-8").read()
    lines = [l for l in t.split("\n") if l.strip().startswith("|")]
    star = sum(l.count("**") for l in lines)
    tick = sum(l.count(TICK) for l in lines)
    print(p.split("\\")[-1])
    print("  表格行数", len(lines), "表格内 ** 个数", star, "表格内反引号个数", tick)
    print("  全文 ** 总数", t.count("**"), " 反引号总数", t.count(TICK))
    print("  含标记的表格示例:")
    for l in lines:
        if "**" in l or TICK in l:
            print("   ", l[:120])
            break
