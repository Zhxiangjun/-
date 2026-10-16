# -*- coding: utf-8 -*-
"""逐行修复：每行单独做 AST 校验，通过才接受替换（不受其他坏行影响）。"""
import io
import ast

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
BAK = PATH + ".bak"
src = io.open(BAK, encoding="utf-8").read()


def line_ok(line):
    """单行语法校验：作为表达式或赋值语句解析，或退化到括号平衡检查。"""
    stripped = line.rstrip()
    try:
        ast.parse(stripped)
        return True
    except SyntaxError:
        pass
    # 跨行续接的行（以 " 结尾）无法单独解析，用引号计数判定
    if stripped.endswith('"' ) or stripped.endswith(','):
        # 该行以字符串续接结尾，要求替换后引号数为偶数
        if stripped.count('"') % 2 == 0:
            return True
    try:
        ast.parse(stripped.lstrip())
        return True
    except SyntaxError:
        return False


lines = src.split("\n")
changed = 0
for i, line in enumerate(lines):
    if '"' not in line or '"""' in line:
        continue
    cjk = sum(1 for ch in line if "\u4e00" <= ch <= "\u9fff")
    if cjk < 3:
        continue
    chars = list(line)
    pair = 0
    touched = False
    for k, ch in enumerate(chars):
        if ch != '"':
            continue
        left = chars[k - 1] if k > 0 else ""
        right = chars[k + 1] if k + 1 < len(chars) else ""
        if not any("\u4e00" <= c <= "\u9fff" for c in left):
            continue
        if not any("\u4e00" <= c <= "\u9fff" for c in right):
            continue
        chars[k] = "\u201c" if pair % 2 == 0 else "\u201d"
        pair += 1
        touched = True
    if not touched:
        continue
    cand = "".join(chars)
    if line_ok(cand):
        lines[i] = cand
        changed += 1

res = "\n".join(lines)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(res)
try:
    ast.parse(res)
    print("修复行数:", changed, "｜整文件 AST 通过")
except SyntaxError as e:
    print("修复行数:", changed, "｜整文件仍有错误：行", e.lineno, e.msg)
    print("内容:", repr(res.split("\n")[e.lineno - 1]))
