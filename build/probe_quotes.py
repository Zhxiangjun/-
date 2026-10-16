# -*- coding: utf-8 -*-
"""找出 gen_env.py 中出现在中文文本里的 ASCII 双引号（会导致 Python 语法错误）。"""
import re

p = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
for i, line in enumerate(open(p, encoding="utf-8"), start=1):
    # 去掉代码块列表里的行（以 " 或 ' 开头的字符串元素）也一并检查
    if any("\u4e00" <= ch <= "\u9fff" for ch in line) and '"' in line:
        # 统计引号数量是否为偶数
        n = line.count('"')
        print(f"{i:>4} q={n} {line.rstrip()[:150]}")
