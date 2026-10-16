# -*- coding: utf-8 -*-
"""迭代修复：反复扫描整份文件，定位语法错误行，把该行里"夹在非定界符位置"的
ASCII 双引号替换为中文引号，直到整份文件通过 AST 解析。

判定：某行里的 " 若其左侧字符不是 [ ( , = : 或行首空白，则它不可能是字符串起始定界符，
      应当视为中文引号（成对交替）。字符串结束定界符由左侧是否处于"已开始"状态决定：
      这里采用简化策略——先把所有 " 视为候选，逐个替换后立刻用"单行可解析"校验，
      一旦通过就保留，否则回退。
"""
import io
import ast

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
src = io.open(PATH, encoding="utf-8").read()


def parses(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


for round_no in range(60):
    try:
        ast.parse(src)
        print(f"第 {round_no} 轮后语法通过")
        break
    except SyntaxError as e:
        lineno = e.lineno
        msg = e.msg
    lines = src.split("\n")
    line = lines[lineno - 1]
    fixed = None
    quotes = [i for i, ch in enumerate(line) if ch == '"']
    for q in quotes:
        left = line[q - 1] if q > 0 else ""
        right = line[q + 1] if q + 1 < len(line) else ""
        if not (left and "\u4e00" <= left <= "\u9fff") and not (right and "\u4e00" <= right <= "\u9fff"):
            continue
        cand = line[:q] + "\u201c" + line[q + 1:]
        trial = "\n".join(lines[:lineno - 1] + [cand] + lines[lineno:])
        if parses(trial):
            fixed = cand
            break
        cand2 = line[:q] + "\u201d" + line[q + 1:]
        trial2 = "\n".join(lines[:lineno - 1] + [cand2] + lines[lineno:])
        if parses(trial2):
            fixed = cand2
            break
    if fixed is None:
        print("无法自动修复：行", lineno, msg)
        print("内容:", repr(line))
        break
    lines[lineno - 1] = fixed
    src = "\n".join(lines)
else:
    print("达到轮次上限")

io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
