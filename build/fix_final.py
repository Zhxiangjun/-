# -*- coding: utf-8 -*-
"""迭代修复：每次只改“当前首个错误行”，用单行 AST 校验决定替换位置，循环直到通过。

替换策略（针对错误行）：
  对该行每一个处于中文语境的 ASCII 双引号，尝试替换为 “ 或 ”，
  选择使「该行替换后可单独解析」或「首个错误行号后移」的那个。
"""
import io
import ast
import sys

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
src = io.open(PATH, encoding="utf-8").read()
CJK = lambda c: bool(c) and ("\u3000" <= c <= "\u303f" or "\u4e00" <= c <= "\u9fff" or "\uff00" <= c <= "\uffef")


def first_err(t):
    try:
        ast.parse(t)
        return 10 ** 9
    except SyntaxError as e:
        return e.lineno or 0


for step in range(200):
    cur = first_err(src)
    if cur == 10 ** 9:
        print("AST 解析通过，修复步数:", step)
        break
    lines = src.split("\n")
    lo = max(1, cur - 3)
    hi = min(len(lines), cur + 1)
    improved = False
    for lineno in range(lo, hi + 1):
        line = lines[lineno - 1]
        for k, ch in enumerate(line):
            if ch != '"':
                continue
            left = line[k - 1] if k > 0 else ""
            right = line[k + 1] if k + 1 < len(line) else ""
            if not (CJK(left) or CJK(right)):
                continue
            for mark in ("\u201c", "\u201d"):
                cand = line[:k] + mark + line[k + 1:]
                trial = "\n".join(lines[:lineno - 1] + [cand] + lines[lineno:])
                if first_err(trial) > cur:
                    lines[lineno - 1] = cand
                    src = trial
                    improved = True
                    break
            if improved:
                break
        if improved:
            break
    if not improved:
        print("无法继续改进，卡在第", cur, "行")
        print("内容:", repr(lines[cur - 1]))
        break

io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
try:
    ast.parse(src)
    print("最终结果：AST 解析通过 ✓")
except SyntaxError as e:
    print("最终结果：仍有错误，行", e.lineno, e.msg)
