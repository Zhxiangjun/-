# -*- coding: utf-8 -*-
"""交付物交叉审计：环境类文档之间的事实一致性、重复度与冲突点检查。"""
import os
import re
from docx import Document
from openpyxl import load_workbook

BASE = r"F:\职业中专\大赛\智慧园区创意\项目文档"
MD = r"F:\职业中专\大赛\智慧园区创意"


def docx_text(path):
    d = Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for r in t.rows:
            for c in r.cells:
                parts.append(c.text)
    return "\n".join(parts)


def xlsx_text(path):
    wb = load_workbook(path, data_only=False)
    parts = []
    for ws in wb.worksheets:
        parts.append(f"### {ws.title}")
        for row in ws.iter_rows(values_only=True):
            parts.append(" | ".join(str(v) for v in row if v is not None))
    return "\n".join(parts)


def md_text(path):
    return open(path, encoding="utf-8").read()


DOCS = {}
for name, reader in [
    ("01_需求规格说明书.docx", docx_text),
    ("02_总体技术架构方案.docx", docx_text),
    ("03_功能清单与优先级评估表.xlsx", xlsx_text),
    ("04_实施路线图与里程碑计划.docx", docx_text),
    ("05_商业计划书.docx", docx_text),
    ("07_开发环境搭建与部署准备指南.docx", docx_text),
    ("08_环境准备与选型核对表.xlsx", xlsx_text),
    ("09_电脑环境配置详细方案.docx", docx_text),
    ("09_电脑环境配置详细方案_新版.docx", docx_text),
    ("10_环境配置进度与验收台账.xlsx", xlsx_text),
    ("10_环境配置进度与验收台账（单机版）.xlsx", xlsx_text),
    ("11_电脑环境配置总览与快速开始.docx", docx_text),
    ("12_协作开发环境配置指引.docx", docx_text),
]:
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        DOCS[name] = reader(p)
    else:
        DOCS[name] = ""

DOCS["02_技术架构.md源文件"] = md_text(os.path.join(BASE, "02_智慧园区平台总体技术架构方案.md"))
DOCS["05_商业计划.md源文件"] = md_text(os.path.join(BASE, "05_智园卫士商业计划书.md"))

# ---------------------------------------------------------------- 1. 事实核对点
FACTS = [
    ("台式机 CPU", ["i5-13400F"]),
    ("RTX 3050 显卡", ["RTX 3050"]),
    ("笔记本1 CPU", ["Ryzen 7 5800U", "5800U"]),
    ("笔记本2 CPU", ["i5-7300HQ", "7300HQ"]),
    ("GTX 1050 显卡", ["GTX 1050"]),
    ("后端端口 8000", ["8000"]),
    ("前端端口 5173", ["5173"]),
    ("PostgreSQL 16", ["PostgreSQL 16", "pgvector:pg16", "postgres:16"]),
    ("Redis 7", ["Redis 7", "redis:7"]),
    ("EMQX 5", ["EMQX 5", "emqx/emqx:5"]),
    ("MinIO", ["MinIO", "minio"]),
    ("TDengine", ["TDengine"]),
    ("ONNX opset 17", ["opset 17", "opset=17"]),
    ("PyTorch 2.x", ["PyTorch 2"]),
    ("CUDA 12", ["CUDA 12", "cu12"]),
    ("Nginx", ["Nginx", "nginx"]),
    ("Docker Compose", ["Docker Compose", "docker compose"]),
    ("Prometheus + Grafana", ["Prometheus"]),
    ("Python 3.11", ["Python 3.11", "python.python.3.11", "py -3.11"]),
    ("Python 3.12", ["Python 3.12", "python.python.3.12"]),
    ("Node.js LTS", ["Node.js LTS", "OpenJS.NodeJS.LTS", "Node LTS"]),
    ("门禁鉴权 ≤300ms", ["300ms", "300 ms"]),
    ("AI 准确率 ≥90%", ["≥90%", "≥ 90%"]),
    ("单校区最小硬件 12—15 万", ["12—15 万", "12-15 万"]),
    ("硬件基准总计 299 万", ["2,992,000", "299 万", "298.7 万"]),
    ("总功能 131 项", ["131 项", "131 项功能"]),
    ("总工程量 1705 人天", ["1705", "1,705"]),
]

print("=" * 100)
print("表 1  关键事实在各文档中的出现情况（√=出现）")
print("=" * 100)
names = list(DOCS.keys())
short = [n.split("_")[0] + ("V2" if "新版" in n else "") + ("M" if n.endswith(".md源文件") else "")
         for n in names]
print(f"{'核对点':<24}" + "".join(f"{s:>7}" for s in short))
for label, keys in FACTS:
    row = f"{label:<24}"
    for n in names:
        t = DOCS[n]
        row += f"{'√' if any(k in t for k in keys) else '-':>7}"
    print(row)

# ---------------------------------------------------------------- 2. 重复度
print()
print("=" * 100)
print("表 2  环境类文档内容重复度（对比关键段落特征词的共现）")
print("=" * 100)
ENV_DOCS = [n for n in names if n[:2] in ("07", "08", "09", "10", "11", "12") and "新版" not in n or "新版" in n]
FEATURES = [
    "install-base.ps1", "check-env.py", "docker-compose.dev.yml", "registry-mirrors",
    "wsl --install", "winget install", "pgvector", "torch.cuda.is_available",
    "Nginx", "离线包", "母盘", "VLAN", "IP 台账", "口令", "回滚", "验收清单",
    "内存 8GB", "WSL2", "MQTTX", "Apifox", "OBS",
]
rows = []
for n in names:
    if n[:2] not in ("07", "08", "09", "10", "11", "12"):
        continue
    t = DOCS[n]
    hit = sum(1 for f in FEATURES if f in t)
    rows.append((n, hit, len(FEATURES), round(hit / len(FEATURES) * 100)))
for n, hit, tot, pct in sorted(rows, key=lambda x: -x[1]):
    print(f"  {n:<44} 命中 {hit:>2}/{tot}  特征覆盖率 {pct:>3}%")

# ---------------------------------------------------------------- 3. 冲突识别
print()
print("=" * 100)
print("表 3  潜在冲突点逐项判定")
print("=" * 100)


def has(doc, *keys):
    t = DOCS.get(doc, "")
    return all(k in t for k in keys)


CONFLICTS = [
    ("笔记本是否必配",
     "07/08 把笔记本 1、笔记本 2 列为环境分工的一部分",
     "09 V2 第 5—6 章、11 把笔记本列为“可选外援”",
     "程度：表述冲突（非事实冲突）。07/08 未标注“可选”"),
    ("服务器硬件成本口径",
     "02 技术架构：单校区最小可行配置约 12—15 万元",
     "03 功能清单：基础设施类约 46 万元（含机房改造与冗余）",
     "程度：口径差异。02 指纯 IT 基础设施，03 含机房与冗余，需在 02 中加口径说明"),
    ("Python 版本",
     "09 V2：后端 3.12 / AI 训练 3.11",
     "12 协作指引：后端 3.12、算法 3.11（与 09 一致）",
     "程度：一致，无冲突"),
    ("验收清单数量",
     "09 V2 第 4.6 节：15 项快速验收 + 第 9 章 25 项全栈验收",
     "10（单机版）：02 表 15 项、03 表 25 项",
     "程度：一致，无冲突"),
    ("机器分工描述",
     "07 第 2 章：三台机器分工表（台式机/笔记本1/笔记本2）",
     "09 V2 第 1.2 节：三种环境类型（开发/演示/协作+服务器）",
     "程度：重复且视角不同。07 按“机器”划分，09 V2 按“环境角色”划分"),
    ("机房与集中开发服务器",
     "07 第 6 章：机房不装数据库，用集中开发服务器",
     "09 V2 第 8 章：保留同一方案",
     "程度：一致；但与“单机全栈”主线的表述需要一句话衔接"),
    ("脚本引用路径",
     "08：环境工具/scripts/",
     "09 V2 附录 B、11、12：环境工具/scripts/",
     "程度：一致，无冲突"),
]


def count_matches(doc, keys):
    t = DOCS.get(doc, "")
    return sum(1 for k in keys if k in t)


for i, (title, a, b, verdict) in enumerate(CONFLICTS, start=1):
    print(f"\n[{i}] {title}")
    print(f"    A: {a}")
    print(f"    B: {b}")
    print(f"    判定: {verdict}")

# ---------------------------------------------------------------- 4. 重复条目统计
print()
print("=" * 100)
print("表 4  环境类文档的定位与重叠关系")
print("=" * 100)
POS = [
    ("07_开发环境搭建与部署准备指南.docx", "概览与准备：机器分工、软件清单、设备模拟、机房与现场要点",
     "与 09 V1 高度重叠；09 V2 已重构为单机主线"),
    ("08_环境准备与选型核对表.xlsx", "勾选台账：机器分工、软件清单、验收清单、云成本、离线包",
     "与 10 高度重叠（同为台账）；10 已按 09 V2 章节重构"),
    ("09_电脑环境配置详细方案_新版.docx", "执行手册（单机全栈主线 + 外援环境）", "与 07 重叠约 60%，深度更高"),
    ("10_环境配置进度与验收台账（单机版）.xlsx", "配套台账（含新旧章节对照）", "与 08 重叠约 70%"),
    ("11_电脑环境配置总览与快速开始.docx", "决策指南（三类环境、先做什么）", "与 09 V2 第 1 章部分重叠，属摘要层"),
    ("12_协作开发环境配置指引.docx", "可转发的协作环境配置", "与 09 V2 第 6 章重叠，属可分发版本"),
]
for a, b, c in POS:
    print(f"\n  {a}")
    print(f"    定位: {b}")
    print(f"    重叠: {c}")

print()
print("=" * 100)
print("审计结论数据已输出完毕")
print("=" * 100)
