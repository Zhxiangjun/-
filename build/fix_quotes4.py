# -*- coding: utf-8 -*-
"""稳健修复：逐行词法拼接，把字符串定界符之外的 ASCII 双引号按奇偶替换为中文引号。

判定依据：在 Python 行内，字符串定界符总是紧跟在 ( , = [ { : 或行首（含缩进）之后，
而中文语境里的引号则夹在中文/中文标点之间。据此区分两者，避免破坏语法。
"""
import io
import re
import ast

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
BAK = PATH + ".bak"
src = io.open(BAK, encoding="utf-8").read()

CJK = re.compile(r"[\u3000-\u303f\u4e00-\u9fff\uff00-\uffef]")
OPENERS = set("(,=[{:")


def repair_lexical(line, active):
    """active: 当前是否处于字符串内部（跨行续接时使用）"""
    out = []
    i = 0
    n = len(line)
    # 判断行首是否为字符串起始（代码块行如  "text", 也算字符串起始）
    while i < n:
        ch = line[i]
        if not active and ch == '"' and i + 1 < n and line[i + 1] == '"':
            # 三引号：整段跳过
            j = line.find('"""', i + 3)
            if j == -1:
                out.append(line[i:])
                return "".join(out), False, 0
            out.append(line[i:j + 3])
            i = j + 3
            continue
        if not active:
            prev = line[i - 1] if i > 0 else ""
            nxt = line[i + 1] if i + 1 < n else ""
            prev_ok = (prev == "" or prev in OPENERS or prev.isspace() and line[:i].strip() == "")
            # 字符串定界符：前一个字符是开括号/逗号/等号/冒号，或位于行首缩进后
            if ch == '"' and (prev == "" or prev in OPENERS or (prev.isspace() and line[:i].strip() == "")):
                j = i + 1
                while j < n:
                    if line[j] == "\\":
                        j += 2
                        continue
                    if line[j] == '"':
                        break
                    j += 1
                out.append(line[i:j + 1])
                i = j + 1
                continue
            if ch == "'":
                j = i + 1
                while j < n:
                    if line[j] == "\\":
                        j += 2
                        continue
                    if line[j] == "'":
                        break
                    j += 1
                out.append(line[i:j + 1])
                i = j + 1
                continue
        out.append(ch)
        i += 1
    return "".join(out), active, 0


CODE_CHARS = set("()[]{}:,=.;#\\") | {"'"}


def fix_line(line):
    """判定 Python 字符串定界符与中文语境引号：

    定界符 = 紧邻 Python 代码字符（含 , ) : = 等）或行首/行尾的引号；
    中文引号 = 左右两侧均为中文或中文标点（右邻允许英文逗号）的引号。
    """
    chars = list(line)
    pair = 0
    n = len(chars)
    for i, ch in enumerate(chars):
        if ch != '"':
            continue
        prev = chars[i - 1] if i > 0 else ""
        nxt = chars[i + 1] if i + 1 < n else ""
        is_delim = (prev == "" or nxt == "" or prev in CODE_CHARS or nxt in CODE_CHARS)
        if is_delim:
            continue
        left_cjk = bool(prev and CJK.match(prev))
        right_cjk = bool(nxt and (CJK.match(nxt) or nxt == ","))
        if left_cjk and right_cjk:
            chars[i] = "\u201c" if pair % 2 == 0 else "\u201d"
            pair += 1
    return "".join(chars), pair


lines = src.split("\n")
changed = 0
for idx, line in enumerate(lines):
    if '"' not in line or '"""' in line:
        continue
    new, cnt = fix_line(line)
    if cnt:
        lines[idx] = new
        changed += 1

res = "\n".join(lines)
try:
    ast.parse(res)
    io.open(PATH, "w", encoding="utf-8", newline="\n").write(res)
    print("修复行数:", changed, "｜AST 解析通过")
except SyntaxError as e:
    io.open(PATH + ".step2", "w", encoding="utf-8", newline="\n").write(res)
    print("仍失败：行", e.lineno, e.msg, "→ 已写入 .step2")
    print(repr(res.split("\n")[e.lineno - 1]))
