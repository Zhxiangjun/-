# -*- coding: utf-8 -*-
"""把 gen_env.py 中文文本中的 ASCII 双引号就地替换为中文引号。

规则：仅处理「位于字符串字面量内部」的引号，且该行中文（CJK）字符数 ≥ 3，
      且该行包含代码块行前缀（"    " 与 "）时不处理。
"""
import io
import re

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
src = io.open(PATH, encoding="utf-8").read()
out_lines = []
changed = 0
for line in src.split("\n"):
    stripped = line.strip()
    is_code_item = re.match(r'^\s*["\']', line) and re.search(r'",\s*$', line) and line.startswith('    ')
    cjk = sum(1 for ch in line if "\u4e00" <= ch <= "\u9fff")
    if is_code_item or cjk < 3 or '"' not in line or '"""' in line or "'''" in line:
        out_lines.append(line)
        continue
    # 保护行首缩进与代码中的小段
    chars = list(line)
    # 找出所有引号位置，成对替换为 “ ”
    idx = [i for i, ch in enumerate(chars) if ch == '"']
    if len(idx) >= 2:
        # 只替换落在中文语境中的引号（前后存在中日韩字符或中文字符）
        new = list(chars)
        pair = 0
        for i in idx:
            left = new[i - 1] if i > 0 else ""
            right = new[i + 1] if i + 1 < len(new) else ""
            # 排除 Python 自身的字符串定界符：左侧紧邻中文字符、",
            # 或右侧是明显的代码结构（) , : 等）时不动
            if any("\u4e00" <= c <= "\u9fff" for c in left):
                continue
            if right in "),:]." and not any("\u4e00" <= c <= "\u9fff" for c in right):
                continue
            ctx = any("\u4e00" <= c <= "\u9fff" for c in (left, right))
            if not ctx:
                continue
            new[i] = "\u201c" if pair % 2 == 0 else "\u201d"
            pair += 1
        if pair > 0:
            changed += 1
            out_lines.append("".join(new))
            continue
    out_lines.append(line)

res = "\n".join(out_lines)
io.open(PATH, "w", encoding="utf-8", newline="\n").write(res)
print("修改行数:", changed)
