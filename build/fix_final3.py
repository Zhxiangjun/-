# -*- coding: utf-8 -*-
"""幂等修复：逐行做「引号在 Python 定界符与非定界符之间」的最小改动搜索。

对每个"首个语法错误行"的窗口（该行与上一行），穷举以下候选：
  - 把行首（缩进后）的中文引号改回 ASCII
  - 对行内每个引号字符做单点替换（" ↔ “ ↔ ”）
  - 对行内两个引号做组合替换（覆盖 "…" 与 “…” 的互转）
以「首个错误行号后移」为接受条件。
"""
import io
import ast
import itertools

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
src = io.open(PATH, encoding="utf-8").read()
MARKS = ['"', "\u201c", "\u201d"]


def first_err(t):
    try:
        ast.parse(t)
        return 10 ** 9
    except SyntaxError as e:
        return e.lineno or 0


def candidates(line):
    seen = set()
    stripped_pos = len(line) - len(line.lstrip())
    if stripped_pos < len(line) and line[stripped_pos] in "\u201c\u201d":
        c = line[:stripped_pos] + '"' + line[stripped_pos + 1:]
        seen.add(c)
        yield c
    positions = [k for k, ch in enumerate(line) if ch in MARKS]
    # 单点
    for k in positions:
        for m in MARKS:
            if line[k] == m:
                continue
            c = line[:k] + m + line[k + 1:]
            if c not in seen:
                seen.add(c)
                yield c
    # 两两组合（限制在长度 400 以内的行，避免组合爆炸）
    if len(positions) <= 12:
        for k1, k2 in itertools.combinations(positions, 2):
            for m1 in MARKS:
                for m2 in MARKS:
                    if line[k1] == m1 and line[k2] == m2:
                        continue
                    c = line[:k1] + m1 + line[k1 + 1:k2] + m2 + line[k2 + 1:]
                    if c not in seen:
                        seen.add(c)
                        yield c


for step in range(300):
    cur = first_err(src)
    if cur == 10 ** 9:
        print("AST 解析通过，修复步数:", step)
        break
    lines = src.split("\n")
    accepted = False
    for lineno in (cur, cur - 1):
        if not (1 <= lineno <= len(lines)):
            continue
        line = lines[lineno - 1]
        for cand in candidates(line):
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
        if cur - 1 >= 1:
            print("上一行：", repr(lines[cur - 2]))
        break

io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
try:
    ast.parse(src)
    print("最终：AST 解析通过 ✓")
except SyntaxError as e:
    print("最终：仍有错误，行", e.lineno, e.msg)
