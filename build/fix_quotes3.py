# -*- coding: utf-8 -*-
"""最终修复：先把源文件解析成 token，定位每个字符串字面量，
只把字面量内部的 ASCII 双引号换成中文引号，再原样重组输出。"""
import io
import re
import tokenize
import ast

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
BAK = PATH + ".bak"

src = io.open(BAK, encoding="utf-8").read()
toks = list(tokenize.generate_tokens(io.StringIO(src).readline))

edits = []  # (start_offset, end_offset, new_text)
offsets = []
pos = 0
for line in src.split("\n"):
    offsets.append(pos)
    pos += len(line) + 1


def to_offset(row, col):
    return offsets[row - 1] + col


count = 0
for tok in toks:
    if tok.type != tokenize.STRING:
        continue
    text = tok.string
    if len(text) < 2:
        continue
    prefix = ""
    body = text
    m = re.match(r"^([A-Za-z]*)('''|\"\"\"|'|\")", text)
    if not m:
        continue
    prefix = m.group(1)
    quote = m.group(2)
    inner = text[len(prefix) + len(quote):-len(quote)]
    if '"' not in inner:
        continue
    cjk = sum(1 for ch in inner if "\u4e00" <= ch <= "\u9fff")
    if cjk < 2:
        continue
    # 成对替换内部 ASCII 引号
    out, pair = [], 0
    for ch in inner:
        if ch == '"':
            out.append("\u201c" if pair % 2 == 0 else "\u201d")
            pair += 1
        else:
            out.append(ch)
    if pair == 0:
        continue
    new_text = prefix + quote + "".join(out) + quote
    start = to_offset(tok.start[0], tok.start[1])
    end = to_offset(tok.end[0], tok.end[1])
    edits.append((start, end, new_text))
    count += 1

for start, end, new in sorted(edits, reverse=True):
    src = src[:start] + new + src[end:]

# 对未能解析成 token 的残余行做最后处理
try:
    ast.parse(src)
    ok = True
except SyntaxError as e:
    ok = False
    print("仍存在语法错误：行", e.lineno, e.msg)

if ok:
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
    print("已修复字符串字面量数:", count, "｜AST 解析通过")
else:
    io.open(PATH + ".step", "w", encoding="utf-8", newline="\n").write(src)
    print("已输出中间文件待人工检查:", PATH + ".step", "｜修复字面量数:", count)
