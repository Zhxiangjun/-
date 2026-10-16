# -*- coding: utf-8 -*-
"""最终修复（稳健版）：
每个循环取「首个错误行」及相邻行，按优先级尝试最小改动：
  1) 行首缩进后的 “ 改回 ASCII "（修复误替换的定界符）
  2) 行内 " 与 “ ” 的单个字符替换（两方向都试）
以「首个错误行号后移」为接受条件，循环至通过。
"""
import io
import ast
import itertools

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
src = io.open(PATH, encoding="utf-8").read()


def first_err(t):
    try:
        ast.parse(t)
        return 10 ** 9
    except SyntaxError as e:
        return e.lineno or 0


def variants(line):
    """按优先级产出候选行。"""
    # 1) 行首（缩进后）的中文引号 → ASCII
    stripped_pos = len(line) - len(line.lstrip())
    if stripped_pos < len(line) and line[stripped_pos] in "\u201c\u201d":
        yield line[:stripped_pos] + '"' + line[stripped_pos + 1:]
    # 2) 单个字符替换：ASCII ↔ 中文引号
    for k, ch in enumerate(line):
        if ch == '"':
            yield line[:k] + "\u201c" + line[k + 1:]
            yield line[:k] + "\u201d" + line[k + 1:]
        elif ch in "\u201c\u201d":
            yield line[:k] + '"' + line[k + 1:]


for step in range(400):
    cur = first_err(src)
    if cur == 10 ** 9:
        print("AST 解析通过，修复步数:", step)
        break
    lines = src.split("\n")
    pool = range(max(1, cur - 2), min(len(lines), cur + 2) + 1)
    accepted = False
    for lineno in pool:
        line = lines[lineno - 1]
        for cand in variants(line):
            trial = "\n".join(lines[:lineno - 1] + [cand] + lines[lineno:])
            if first_err(trial) > cur:
                lines[lineno - 1] = cand
                src = trial
                accepted = True
                break
        if accepted:
            break
    if not accepted:
        print("卡在第", cur, "行：", repr(lines[cur - 1]))
        break

io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
try:
    ast.parse(src)
    print("最终：AST 解析通过 ✓")
except SyntaxError as e:
    print("最终：仍有错误，行", e.lineno, e.msg)
