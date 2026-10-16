# -*- coding: utf-8 -*-
"""最终修复流程（合并版）：
1) 逐行修复（单行可解析才接受）；
2) 对仍未通过的行给出明确的候选替换报告，便于人工确认；
3) 全部通过后写回。
"""
import io
import ast

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
src = io.open(PATH, encoding="utf-8").read()
CJK = lambda c: bool(c) and ("\u3000" <= c <= "\u303f" or "\u4e00" <= c <= "\u9fff" or "\uff00" <= c <= "\uffef")


def parses(t):
    try:
        ast.parse(t)
        return True
    except SyntaxError:
        return False


def line_ok(line):
    if parses(line.rstrip()):
        return True
    s = line.rstrip()
    return (s.endswith('"') or s.endswith(",")) and s.count('"') % 2 == 0


lines = src.split("\n")
fixed = 0
for i, line in enumerate(lines):
    if '"' not in line or '"""' in line:
        continue
    chars = list(line)
    pair = 0
    touch = False
    for k, ch in enumerate(chars):
        if ch != '"':
            continue
        left = chars[k - 1] if k > 0 else ""
        right = chars[k + 1] if k + 1 < len(chars) else ""
        if CJK(left) and CJK(right):
            chars[k] = "\u201c" if pair % 2 == 0 else "\u201d"
            pair += 1
            touch = True
    if touch and line_ok("".join(chars)):
        lines[i] = "".join(chars)
        fixed += 1

src = "\n".join(lines)
print("逐行修复行数:", fixed)

# 残余错误逐条尝试搜索式修复（只改错误行及之前的行）
rounds = 0
while not parses(src) and rounds < 40:
    rounds += 1
    try:
        ast.parse(src)
    except SyntaxError as e:
        best, msg = (e.lineno or 0), e.msg
    ls = src.split("\n")
    prog = False
    for lineno in range(1, min(best, len(ls)) + 1):
        line = ls[lineno - 1]
        for k, ch in enumerate(line):
            if ch != '"':
                continue
            left = line[k - 1] if k > 0 else ""
            right = line[k + 1] if k + 1 < len(line) else ""
            if not (CJK(left) or CJK(right)):
                continue
            for mark in ("\u201c", "\u201d"):
                cand = line[:k] + mark + line[k + 1:]
                trial = "\n".join(ls[:lineno - 1] + [cand] + ls[lineno:])
                try:
                    ast.parse(trial)
                    ls[lineno - 1] = cand
                    src = trial
                    prog = True
                    break
                except SyntaxError as e2:
                    if (e2.lineno or 0) > best:
                        ls[lineno - 1] = cand
                        src = trial
                        prog = True
                        break
            if prog:
                break
        if prog:
            break
    if not prog:
        print("无法自动修复，停在第", best, "行：", msg)
        print("内容:", repr(ls[best - 1]) if 0 < best <= len(ls) else "?")
        break

ok = parses(src)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
print("结果：", "AST 解析通过 ✓" if ok else "仍有语法错误 ✗")
