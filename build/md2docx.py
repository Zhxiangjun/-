# -*- coding: utf-8 -*-
"""把子代理产出的 Markdown 文档转换为排版规范的 DOCX。"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_kit import (Document, Pt, Cm, WD_ALIGN_PARAGRAPH, _font, add_table,
                      para, note, setup, cover, h, NAVY, BLUE, GREY, DARK, HEI, SONG,
                      shade, cell_text)

JOBS = [
    dict(src=r"F:\职业中专\大赛\智慧园区创意\项目文档\02_智慧园区平台总体技术架构方案.md",
         dst=r"F:\职业中专\大赛\智慧园区创意\项目文档\02_总体技术架构方案.docx",
         title="“智园卫士”智慧校园管理平台",
         subtitle="总体技术架构方案",
         doc_kind="总 体 技 术 架 构 方 案",
         info=[("文档名称", "总体技术架构方案"),
               ("文档编号", "ZYWS-ARCH-2026-001"),
               ("版本号", "V1.0"),
               ("编制单位", "齐河县职业中等专业学校 项目组"),
               ("适用范围", "智慧校园（智慧园区）管理平台设计与实施"),
               ("编制日期", "2026 年 11 月"),
               ("密级", "内部")]),
    dict(src=r"F:\职业中专\大赛\智慧园区创意\项目文档\05_智园卫士商业计划书.md",
         dst=r"F:\职业中专\大赛\智慧园区创意\项目文档\05_商业计划书.docx",
         title="“智园卫士”智慧校园管理平台",
         subtitle="商业计划书",
         doc_kind="商 业 计 划 书",
         info=[("文档名称", "商业计划书"),
               ("文档编号", "ZYWS-BP-2026-001"),
               ("版本号", "V1.0"),
               ("编制单位", "齐河县职业中等专业学校 项目组"),
               ("用途", "项目立项、校企合作与市场推广"),
               ("编制日期", "2026 年 11 月"),
               ("密级", "商业机密（内部）")]),
]

CODE_LANGS = ("", "text", "bash", "sh", "sql", "json", "python", "yaml", "ini", "mermaid")
TICK = "`"


def clean_inline(text):
    """去掉表格/段落中的 Markdown 行内标记，避免出现 ** 与反引号残留。"""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\w)\*(?!\s)([^*\n]+?)(?<!\s)\*(?!\w)", r"\1", text)
    text = text.replace(TICK, "")
    text = text.replace("\\|", "|")
    return text.strip()


def add_code_block(doc, lines):
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    c = t.rows[0].cells[0]
    c.text = ""
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    _font(p.add_run("\n".join(lines)), name="Consolas", size=8)
    shade(c, "F7F7F9")
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_bullet(doc, text, level=0, ordered=False, marker="•"):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Cm(0.75 + level * 0.55)
    p.paragraph_format.first_line_indent = Cm(-0.55)
    _font(p.add_run(marker + " "), size=10, bold=ordered)
    # 支持行内加粗 **text**
    for seg in re.split(r"(\*\*.+?\*\*)", text):
        if seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
            _font(p.add_run(clean_inline(seg[2:-2])), size=10, bold=True)
        elif seg:
            _font(p.add_run(seg.replace(TICK, "")), size=10)


def add_para(doc, text, size=10.5):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.35
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.first_line_indent = Pt(size * 2)
    for seg in re.split(r"(\*\*.+?\*\*)", text):
        if seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
            _font(p.add_run(clean_inline(seg[2:-2])), size=size, bold=True)
        elif seg:
            _font(p.add_run(seg.replace(TICK, "")), size=size)


def add_quote(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.line_spacing = 1.3
    p.paragraph_format.space_after = Pt(4)
    _font(p.add_run(clean_inline(text)), size=9.5, color=GREY, italic=True)


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def convert(job):
    src, dst = job["src"], job["dst"]
    text = open(src, encoding="utf-8").read().replace("\r\n", "\n")
    lines = text.split("\n")
    doc = Document()
    setup(doc, os.path.basename(dst).replace(".docx", "") + " V1.0")
    cover(doc, job["title"], job["subtitle"],
          job["info"], doc_kind=job["doc_kind"])

    i = 0
    first_h1 = True
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        # 代码块
        if s.startswith("```"):
            lang = s[3:].strip()
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            add_code_block(doc, buf)
            continue
        # 表格
        if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            headers = [clean_inline(x) for x in split_row(s)]
            i += 2
            data = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row = [clean_inline(x) for x in split_row(lines[i])]
                if len(row) < len(headers):
                    row += [""] * (len(headers) - len(row))
                data.append(row[:len(headers)])
                i += 1
            n = len(headers)
            total = 15.6
            if n >= 6:
                widths = [total / n] * n
            elif n == 5:
                widths = [2.2, 3.4, 3.4, 3.3, 3.3]
            elif n == 4:
                widths = [2.6, 4.6, 4.2, 4.2]
            elif n == 3:
                widths = [3.0, 6.3, 6.3]
            elif n == 2:
                widths = [3.6, 12.0]
            else:
                widths = [total]
            add_table(doc, headers, data, widths, size=8.5,
                      align_center_cols=tuple(range(0, min(n, 3))) if n <= 4 else ())
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue
        # 标题
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            title = clean_inline(m.group(2).strip())
            if level == 1:
                if first_h1:
                    first_h1 = False
                    i += 1
                    continue
                doc.add_page_break()
                h(doc, title, 1)
            else:
                h(doc, title, min(level, 3))
            i += 1
            continue
        if re.match(r"^-{3,}$", s) or re.match(r"^\*{3,}$", s) or re.match(r"^_{3,}$", s):
            i += 1
            continue
        if s.startswith(">"):
            add_quote(doc, s.lstrip("> ").strip())
            i += 1
            continue
        m = re.match(r"^(\s*)([-*+])\s+(.*)$", ln)
        if m:
            add_bullet(doc, m.group(3).strip(), level=len(m.group(1)) // 2)
            i += 1
            continue
        m = re.match(r"^(\s*)(\d+)[.)]\s+(.*)$", ln)
        if m:
            add_bullet(doc, m.group(3).strip(), level=len(m.group(1)) // 2,
                       ordered=True, marker=m.group(2) + ".")
            i += 1
            continue
        if not s:
            i += 1
            continue
        add_para(doc, s)
        i += 1

    doc.save(dst)
    print("已生成:", dst)
    return dst


if __name__ == "__main__":
    for job in JOBS:
        convert(job)
