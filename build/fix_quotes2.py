# -*- coding: utf-8 -*-
"""安全修复：仅当替换后整份文件仍能通过 AST 解析时才接受该行的引号替换。"""
import io
import ast
import re

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
BAK = PATH + ".bak"
src = io.open(BAK, encoding="utf-8").read()


def try_parse(text):
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


assert try_parse(src), "备份文件本身语法有误，请先修正"

lines = src.split("\n")
changed = 0
for i, line in enumerate(lines):
    if '"' not in line or '"""' in line:
        continue
    cjk = sum(1 for ch in line if "\u4e00" <= ch <= "\u9fff")
    if cjk < 3:
        continue
    idx = [k for k, ch in enumerate(line) if ch == '"']
    chars = list(line)
    pair = 0
    touched = False
    for k in idx:
        left = chars[k - 1] if k > 0 else ""
        right = chars[k + 1] if k + 1 < len(chars) else ""
        # 只处理「左右都是中文/中文标点」的引号，且该位置不是 Python 字符串定界符
        if not any("\u4e00" <= c <= "\u9fff" for c in left):
            continue
        if not any("\u4e00" <= c <= "\u9fff" for c in right):
            continue
        chars[k] = "\u201c" if pair % 2 == 0 else "\u201d"
        pair += 1
        touched = True
    if not touched:
        continue
    candidate = "\n".join(lines[:i] + ["".join(chars)] + lines[i + 1:])
    if try_parse(candidate):
        lines[i] = "".join(chars)
        changed += 1

res = "\n".join(lines)
ast.parse(res)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(res)
print("已修复行数:", changed, "｜语法检查通过")
