# -*- coding: utf-8 -*-
"""借助 tokenize 定位问题：给出当前文件所有"语法错误行"，并列出其后若干行，便于一次性人工修正。"""
import io
import ast

p = r"F:\职业中专\大赛\智慧园区创意\build\gen_env.py"
s = io.open(p, encoding="utf-8").read()
lines = s.split("\n")
bad = []
for i, line in enumerate(lines, start=1):
    st = line.strip()
    if not st or st.startswith("#"):
        continue
    # 只检查"看起来像完整语句"的行：以 ) 或 , 或 ] 结尾且引号数为奇数
    if st.count('"') % 2 == 1 and ('doc, "' in line or '["' in line or '"' in line):
        bad.append(i)
print("引号数为奇数的可疑行数:", len(bad))
print("行号:", bad[:60])
try:
    ast.parse(s)
    print("AST 通过")
except SyntaxError as e:
    print("首个错误行:", e.lineno, e.msg)
