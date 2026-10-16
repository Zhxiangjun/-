# -*- coding: utf-8 -*-
"""最终方案：以「整份文件能否通过 AST 解析」为唯一判据搜索。

做法：从左到右扫描所有中文语境候选引号，为每一个尝试两种替换
（先 " → "，不行再 " → "），只要替换后"首个语法错误行号"变大就接受，
直到整份文件解析通过。
"""
import io
import ast

PATH = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
BAK = PATH + ".bak"
src = io.open(BAK, encoding="utf-8").read()
CJK = lambda c: bool(c) and ("\u3000" <= c <= "\u303f" or "\u4e00" <= c <= "\u9fff" or "\uff00" <= c <= "\uffef")


def err_line(text):
    """返回 (是否通过, 首个错误行号)。"""
    try:
        ast.parse(text)
        return True, 10 ** 9
    except SyntaxError as e:
        return False, e.lineno or 0


ok, best = err_line(src)
print("初始：", "通过" if ok else f"首个错误行 {best}")

lines = src.split("\n")
guard = 0
while not ok and guard < 400:
    guard += 1
    # 找到当前首个错误行，在该行内寻找候选引号
    # 只允许修改「错误行及其之前的行」，避免污染已经合法的后文
    progress = False
    for lineno in range(1, min(best, len(lines)) + 1):
        line = lines[lineno - 1]
        if '"' not in line:
            continue
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
                o2, b2 = err_line(trial)
                if o2 or b2 > best:
                    lines[lineno - 1] = cand
                    src = trial
                    ok, best = o2, b2
                    progress = True
                    break
            if progress:
                break
        if progress:
            break
    if not progress:
        print("无可用改进，停止于行", best)
        print("内容:", repr(lines[best - 1]) if 0 < best <= len(lines) else "?")
        break

print("最终：", "AST 解析通过" if ok else f"仍有错误，行 {best}")
io.open(PATH, "w", encoding="utf-8", newline="\n").write(src)
