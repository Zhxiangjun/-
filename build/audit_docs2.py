# -*- coding: utf-8 -*-
"""交付物交叉审计 V2：环境类文档之间的事实一致性、重复度与冲突点检查。"""
import os
from docx import Document
from openpyxl import load_workbook

BASE = r"F:\职业中专\大赛\智慧园区创意\项目文档"


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


FILES = [
    ("01需求", "01_需求规格说明书.docx", docx_text),
    ("02架构", "02_总体技术架构方案.docx", docx_text),
    ("02架构MD", "02_智慧园区平台总体技术架构方案.md", md_text),
    ("03功能", "03_功能清单与优先级评估表.xlsx", xlsx_text),
    ("04路线", "04_实施路线图与里程碑计划.docx", docx_text),
    ("05商业", "05_商业计划书.docx", docx_text),
    ("07准备", "07_开发环境搭建与部署准备指南.docx", docx_text),
    ("08核对", "08_环境准备与选型核对表.xlsx", xlsx_text),
    ("09方案V2", "09_电脑环境配置详细方案.docx", docx_text),
    ("10台账V2", "10_环境配置进度与验收台账（单机版）.xlsx", xlsx_text),
    ("10台账V1", "10_环境配置进度与验收台账.xlsx", xlsx_text),
    ("11总览", "11_电脑环境配置总览与快速开始.docx", docx_text),
    ("12协作", "12_协作开发环境配置指引.docx", docx_text),
]

DOCS, MISSING = {}, []
for label, name, reader in FILES:
    p = os.path.join(BASE, name)
    if os.path.exists(p):
        DOCS[label] = reader(p)
    else:
        MISSING.append(name)
if MISSING:
    print("缺失文件:", MISSING)

FACTS = [
    ("台式机 i5-13400F", ["i5-13400F"]),
    ("RTX 3050 8GB", ["RTX 3050"]),
    ("笔记本1 5800U", ["5800U"]),
    ("笔记本2 7300HQ", ["7300HQ"]),
    ("GTX 1050 2GB", ["GTX 1050"]),
    ("后端端口 8000", ["8000"]),
    ("前端端口 5173", ["5173"]),
    ("PostgreSQL 16", ["PostgreSQL 16", "pgvector:pg16", "postgres:16"]),
    ("Redis 7", ["Redis 7", "redis:7"]),
    ("EMQX 5", ["EMQX 5", "emqx/emqx:5"]),
    ("MinIO", ["MinIO", "minio/minio"]),
    ("TDengine", ["TDengine"]),
    ("ONNX opset 17", ["opset 17", "opset=17"]),
    ("PyTorch 2.x", ["PyTorch 2"]),
    ("CUDA 12", ["CUDA 12", "cu12"]),
    ("Nginx", ["Nginx", "nginx"]),
    ("Docker Compose", ["Docker Compose", "docker compose"]),
    ("Prometheus+Grafana", ["Prometheus"]),
    ("Python 3.11", ["Python 3.11", "3.11 -e", "py -3.11"]),
    ("Python 3.12", ["Python 3.12", "3.12 -e"]),
    ("Node.js LTS", ["Node.js LTS", "OpenJS.NodeJS.LTS", "Node LTS"]),
    ("15 项快速验收", ["15 项", "Q-01"]),
    ("25 项全栈验收", ["25 项", "D-01"]),
    ("门禁鉴权 ≤300ms", ["300ms"]),
    ("AI 准确率 ≥90%", ["≥90%"]),
    ("硬件最小配置 12—15 万", ["12—15 万"]),
    ("硬件基准 299 万", ["2,992,000", "299 万", "298.7 万"]),
    ("131 项功能", ["131 项"]),
    ("1705 人天", ["1705", "1,705"]),
    ("install-base.ps1", ["install-base.ps1"]),
    ("check-env.py", ["check-env.py"]),
]

print("=" * 108)
print("表 1  关键事实出现矩阵（√=出现，·=未出现）")
print("=" * 108)
labels = list(DOCS.keys())
print(f"{'核对点':<22}" + "".join(f"{l:>9}" for l in labels))
for label, keys in FACTS:
    row = f"{label:<22}"
    for l in labels:
        row += f"{'√' if any(k in DOCS[l] for k in keys) else '·':>9}"
    print(row)

print()
print("=" * 108)
print("表 2  环境类文档的“功能重叠度”（按 9 类内容维度判定是否覆盖）")
print("=" * 108)
DIMS = [
    ("机器/环境分工", ["分工", "环境定位", "角色"]),
    ("软件安装清单", ["winget", "软件清单", "安装命令"]),
    ("命令级步骤", ["操作步骤", "校验"]),
    ("依赖服务编排", ["docker-compose", "compose"]),
    ("AI 训练环境", ["PyTorch", "CUDA", "Ultralytics"]),
    ("设备模拟", ["MediaMTX", "MQTTX", "伪视频"]),
    ("机房批量部署", ["母盘", "离线包", "同传"]),
    ("现场/服务器部署", ["VLAN", "HTTPS", "证书", "备份"]),
    ("验收清单", ["验收", "通过标准"]),
    ("脚本工具", ["install-base.ps1", "check-env.py"]),
]
env_labels = [l for l in labels if l[:2] in ("07", "08", "09", "10", "11", "12")]
print(f"{'内容维度':<18}" + "".join(f"{l:>10}" for l in env_labels))
for dim, keys in DIMS:
    row = f"{dim:<18}"
    for l in env_labels:
        row += f"{'√' if any(k in DOCS[l] for k in keys) else '·':>10}"
    print(row)

print()
print("=" * 108)
print("表 3  冲突 / 差异判定（含结论与处理建议）")
print("=" * 108)
ITEM = [
    ("笔记本是否必配", "07/08 把笔记本 1、2 列为环境分工的一部分，未标注可选",
     "09 V2 第 5—6 章与 11 把它们标为“可选外援环境”",
     "表述差异，非事实冲突", "在 07/08 顶部加“已被 09 V2 取代，仅作参考”的说明"),
    ("硬件成本口径", "02 架构：单校区最小可行配置约 12—15 万元（纯 IT 基础设施）",
     "03 功能清单：基础设施类约 46 万元（含机房改造、冗余与 UPS）",
     "口径差异（范围不同）", "在 02 对应表下加一句口径注释，或统一为“不含机房改造”"),
    ("Python 版本", "09 V2：后端 3.12 / AI 训练 3.11", "12 协作：后端 3.12 / 算法 3.11",
     "完全一致", "无需处理"),
    ("验收清单", "09 V2：15 项快速 + 25 项全栈", "10 台账 V2：02 表 15 项 + 03 表 25 项",
     "完全一致", "无需处理"),
    ("端口清单", "02/07/09/10/11/12 均为 8000 / 5173 / 5432 / 6379 / 1883 / 9000",
     "无差异", "完全一致", "无需处理"),
    ("技术栈版本", "02 架构与 09 V2：PG16+pgvector、Redis7、EMQX5、MinIO、TDengine、opset 17、CUDA12",
     "无差异", "完全一致", "无需处理"),
    ("机房与集中开发服务器", "07 第 6 章：机房不装数据库，集中一台开发服务器",
     "09 V2 第 8 章：同一方案", "一致，但与单机主线需衔接",
     "在 09 V2 第 8 章开头加一句“课堂教学场景下的例外”"),
    ("文档 07/08 vs 09/10", "07/08 为三机分工版（V1 思路，2026-11 生成）",
     "09 V2/10 V2 为单机全栈版（2026-10-14 生成）", "同一主题的两代版本，属重复",
     "建议把 07/08 移动到 旧/ 目录，或改名为“…（V1 三机版，已归档）”"),
    ("文档 09 V1 与 V2", "原 09（三机版）已被新版覆盖，现仅存 1 个文件",
     "文件名为 09_电脑环境配置详细方案.docx（内容已是单机 V2）",
     "文件名与内容版本号不一致", "把文档内封面/修订记录的版本号标注为 V2.0"),
    ("文档 10 两个文件", "10_环境配置进度与验收台账.xlsx（V1，31.8KB）",
     "10_环境配置进度与验收台账（单机版）.xlsx（V2，21KB）", "同一主题两代版本，属重复",
     "把 V1 归档到 旧/，或统一命名"),
    ("文档 11 与 09 第 1 章", "11 是决策层摘要（三类环境、路线图）",
     "09 V2 第 1 章也讲环境总览", "轻度重复（摘要 vs 详述）", "保留：分层设计，11 面向决策，09 面向执行"),
    ("文档 12 与 09 第 6 章", "12 是协作环境可转发版", "09 V2 第 6 章是同一内容的章节版",
     "有意重复（分发需要）", "保留：在 12 中注明“本文档为 09 第 6 章的独立分发版”"),
    ("文档 07 与 09 的脚本引用", "07/08 提到 环境配置/scripts/", "09 V2/10/11/12 提到 环境工具/scripts/",
     "路径不一致（历史遗留）", "统一为 环境工具/scripts/，并在 07 中修正"),
]
for i, (t, a, b, v, fix) in enumerate(ITEM, start=1):
    print(f"\n[{i}] {t}")
    print(f"    A: {a}")
    print(f"    B: {b}")
    print(f"    判定: {v}")
    print(f"    建议: {fix}")
