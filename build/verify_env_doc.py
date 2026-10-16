# -*- coding: utf-8 -*-
"""校验生成的文档内容是否被引号替换破坏：抽查关键句子与代码块完整性。"""
import io
from docx import Document

p = r"F:\职业中专\大赛\智慧园区创意\07_开发环境搭建与部署准备指南.docx"
d = Document(p)
texts = [x.text for x in d.paragraphs]
for t in d.tables:
    for r in t.rows:
        for c in r.cells:
            texts.append(c.text)
full = "\n".join(texts)

MUST = [
    "RTX 3050", "计算能力 8.6", "GTX 1050 2GB", "Ryzen 7 5800U", "i5-7300HQ",
    "registry-mirrors", "容器镜像服务", "pypi.tuna.tsinghua.edu.cn", "registry.npmmirror.com",
    "wsl --install -d Ubuntu-24.04", "docker compose -f docker-compose.dev.yml up -d",
    "torch.cuda.is_available()", "yolo detect train", "nvidia-smi",
    "客户端集群", "一次训练、多端推理", "我这里能跑", "数据损坏",
    "install-baseline.ps1", "check-env.py", "MediaMTX", "MQTTX", "Apifox", "DBeaver",
    "VLAN 规划", "IP 地址台账", "来电自启", "RPO ≤15 分钟",
]
print("文件段落数:", len(texts))
miss = [m for m in MUST if m not in full]
print("必含内容缺失:", miss if miss else "无（全部命中）")

# 检查是否有明显被破坏的行：连续出现两个中文引号且中间为空
import re
bad = re.findall(r"“”|‘’", full)
print("异常空引号:", len(bad))

# 输出包含代码块的行数（Consolas 字体）
code_cells = 0
for t in d.tables:
    for r in t.rows:
        for c in r.cells:
            for para in c.paragraphs:
                for run in para.runs:
                    if run.font.name == "Consolas" and run.text.strip():
                        code_cells += 1
print("代码块段落数:", code_cells)

# 抽样打印几个关键句子（前 120 字）
for key in ["计算能力 8.6", "客户端集群", "一次训练、多端推理"]:
    for t in texts:
        if key in t:
            print("样例 →", t[:150].replace("\n", " "))
            break
