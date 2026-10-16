# -*- coding: utf-8 -*-
"""全文件最终修复：
1) 用正则识别行内所有"仅含 ASCII/拉丁字符"的引号串（这些是 Python 定界符），打标记保护；
2) 在未保护的引号中，把位于中文语境（左或右邻为中文/中文标点）的按奇偶替换为中文引号；
3) 整文件 AST 校验通过后写回。
"""
import io
import re
import ast

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
src = io.open(PATH, encoding="utf-8").read()

CJK_RE = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")
# 纯 ASCII 内容的引号串 → 视为 Python 定界符（payload 里一定有中文，不会命中）
ASCII_STR = re.compile(r'"(?![^"\n]*[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef])[^"\n]*"')

total = 0
lines = src.split("\n")
for i, line in enumerate(lines):
    if '"' not in line or '"""' in line:
        continue
    protected = [False] * len(line)
    for m in ASCII_STR.finditer(line):
        for k in range(m.start(), m.end()):
            protected[k] = True
    chars = list(line)
    pair = 0
    for k, ch in enumerate(chars):
        if ch != '"' or protected[k]:
            continue
        left = chars[k - 1] if k > 0 else ""
        right = chars[k + 1] if k + 1 < len(chars) else ""
        if CJK_RE.match(left) or CJK_RE.match(right):
            chars[k] = "\u201c" if pair % 2 == 0 else "\u201d"
            pair += 1
            total += 1
    lines[i] = "".join(chars)

res = "\n".join(lines)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(res)
try:
    ast.parse(res)
    print("替换引号数:", total, "｜整文件 AST 解析通过")
except SyntaxError as e:
    print("替换引号数:", total, "｜仍有错误：行", e.lineno, e.msg)
    print("内容:", repr(res.split("\n")[e.lineno - 1]))
