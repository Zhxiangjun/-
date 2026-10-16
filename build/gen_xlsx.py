# -*- coding: utf-8 -*-
"""生成 03_功能清单与优先级评估表.xlsx（多工作表、可核算）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_master import build, MODULES, MODULE_NAME, stage_summary, module_summary, PHASE_FACTOR

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

OUT = r"F:\职业中专\大赛\智慧园区创意\03_功能清单与优先级评估表.xlsx"

RATE = 1200          # 商业级人天综合单价（元/人天，含税）
STUDENT_CAP = 128    # 团队月度可用产能（人天/月）

NAVY = "1F3864"
BLUE = "2E5C8A"
LIGHT = "DCE6F1"
GREY = "F2F2F2"

thin = Side(style="thin", color="B0B0B0")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def style_header(ws, row=1, fill=NAVY):
    for c in ws[row]:
        if c.value is None:
            continue
        c.font = Font(name="微软雅黑", size=10, bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=fill)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER


def style_body(ws, first=2, last=None):
    last = last or ws.max_row
    for r in ws.iter_rows(min_row=first, max_row=last, max_col=ws.max_column):
        for c in r:
            c.font = Font(name="微软雅黑", size=9)
            c.border = BORDER
            c.alignment = Alignment(vertical="top", wrap_text=True)


def set_widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def title_block(ws, title, sub, ncols):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ncols)
    c = ws.cell(row=1, column=1, value=title)
    c.font = Font(name="微软雅黑", size=14, bold=True, color=NAVY)
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[1].height = 30
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=ncols)
    c = ws.cell(row=2, column=2 - 1, value=sub)
    c.font = Font(name="微软雅黑", size=9, color="808080")
    ws.row_dimensions[2].height = 16
    return 3  # 数据从第 4 行开始（表头在第 4 行）


rows = build()
stages = stage_summary(rows)
mods = module_summary(rows)

wb = Workbook()

# ============================================================
# SHEET 0 说明与汇总
# ============================================================
ws = wb.active
ws.title = "00-说明与汇总"
hdr = title_block(ws, "“智园卫士”智慧校园（智慧园区）管理平台 — 功能清单与实施评估", "版本 V1.0 ｜ 编制日期 2026 年 11 月 ｜ 密级：内部 ｜ 本表为全部交付物的功能与工期基准数据源", 6)
r = hdr + 1
info = [
    ("项目名称", "“智园卫士”智慧校园（智慧园区）管理平台"),
    ("建设主体", "齐河县职业中等专业学校（齐河职专）"),
    ("学校规模基线", "中等规模中职：3000—6000 名在校生，1—2 个校区"),
    ("功能规模", f"{len(MODULES)} 个一级模块 / {sum(1 for m in MODULES for _ in [0])} 个模块下二级功能组 / {len(rows)} 项功能"),
    ("工时口径", "人天（1 人 × 8 小时）；含开发、自测、联调、文档与返工系数（MVP×1.4，后续版本×1.25）"),
    ("总工程量", f"{sum(r['effort'] for r in rows)} 人天（商业级完整交付口径）"),
    ("人天单价假设", f"{RATE} 元/人天（商业级综合单价，含税）"),
    ("团队月度产能假设", f"{STUDENT_CAP} 人天/月（8 人团队 × 约 4 人天/周 × 4 周）"),
    ("优先级说明", "P0 必须实现（缺则系统不成立）｜P1 重要（显著提升价值）｜P2 增强（提升体验）｜P3 可选（远期）"),
    ("版本批次说明", "MVP 最小可用闭环｜V1 首个商业版本｜V2 平台化增强｜V3 智能化与生态"),
]
for k, v in info:
    ws.cell(row=r, column=1, value=k).font = Font(name="微软雅黑", size=9, bold=True, color=NAVY)
    ws.cell(row=r, column=1).fill = PatternFill("solid", fgColor=LIGHT)
    ws.cell(row=r, column=2, value=v).font = Font(name="微软雅黑", size=9)
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    r += 1

r += 1
ws.cell(row=r, column=1, value="版本批次汇总").font = Font(name="微软雅黑", size=11, bold=True, color=NAVY)
r += 1
head = ["版本批次", "功能项数", "P0", "P1", "P2", "P3", "工程量(人天)", "人力成本(元)", "周期估算(月)"]
for i, h in enumerate(head, start=1):
    ws.cell(row=r, column=i, value=h)
style_header(ws, r, BLUE)
hr = r
r += 1
STAGE_DESC = {
    "MVP": "最小可用闭环：统一身份 + 通行门禁 + 请假联动 + AI 预警 + 事件派单",
    "V1": "首个商业版本：车辆、归寝、考勤协同、驾驶舱、移动端、等保合规",
    "V2": "平台化增强：一卡通、能耗、设施运维、自定义报表、多校区适配",
    "V3": "智能化与生态：数字孪生大屏、语音助手、开放生态、低碳校园",
}
for st in ["MVP", "V1", "V2", "V3"]:
    s = stages[st]
    eff = s["effort"]
    r += 0
    ws.cell(row=r, column=1, value=st)
    ws.cell(row=r, column=2, value=s["count"])
    ws.cell(row=r, column=3, value=s["P0"])
    ws.cell(row=r, column=4, value=s["P1"])
    ws.cell(row=r, column=5, value=s["P2"])
    ws.cell(row=r, column=6, value=s["P3"])
    ws.cell(row=r, column=7, value=eff)
    ws.cell(row=r, column=8, value=eff * RATE)
    ws.cell(row=r, column=9, value=round(eff / STUDENT_CAP + 0.5, 1))
    r += 1
ws.cell(row=r, column=1, value="合计").font = Font(name="微软雅黑", size=9, bold=True)
tot = sum(s["effort"] for s in stages.values())
ws.cell(row=r, column=2, value=len(rows)).font = Font(name="微软雅黑", size=9, bold=True)
ws.cell(row=r, column=7, value=tot).font = Font(name="微软雅黑", size=9, bold=True)
ws.cell(row=r, column=8, value=tot * RATE).font = Font(name="微软雅黑", size=9, bold=True)
ws.cell(row=r, column=9, value=round(tot / STUDENT_CAP, 1)).font = Font(name="微软雅黑", size=9, bold=True)
for c in ws[r]:
    c.fill = PatternFill("solid", fgColor=LIGHT)
style_body(ws, hr + 1, r)
for rr in range(hr + 1, r + 1):
    ws.cell(row=rr, column=8).number_format = '#,##0'
set_widths(ws, [22, 12, 7, 7, 7, 7, 14, 16, 14])
ws.cell(row=r + 2, column=1, value="注：周期估算 = 工程量 ÷ 团队月度产能，未计并行度损失与假期，实际排期以《实施路线图与里程碑计划》为准。").font = Font(name="微软雅黑", size=8, color="808080")

# ============================================================
# SHEET 1 功能清单（全量）
# ============================================================
ws = wb.create_sheet("01-功能清单(全量)")
head = ["功能编号", "一级模块", "二级功能组", "功能名称", "功能描述", "优先级", "交付批次", "工时基线(人天)", "估算工程量(人天)", "人力成本(元)", "是否含硬件对接"]
ws.append(head)
style_header(ws, 1)
for idx, r_ in enumerate(rows, start=1):
    code = f"{r_['mod']}-{idx:03d}"
    hw = "是" if r_["base"] >= 15 else ("部分" if r_["base"] >= 13 else "否")
    ws.append([code, MODULE_NAME[r_["mod"]], r_["group"], r_["name"], r_["desc"],
               r_["prio"], r_["stage"], r_["base"], r_["effort"], r_["effort"] * RATE, hw])
style_body(ws, 2)
set_widths(ws, [12, 20, 16, 26, 62, 8, 10, 14, 16, 14, 14])
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:K{ws.max_row}"
for rr in range(2, ws.max_row + 1):
    ws.cell(row=rr, column=10).number_format = '#,##0'

# ============================================================
# SHEET 2 优先级矩阵
# ============================================================
ws = wb.create_sheet("02-优先级矩阵")
hdr = title_block(ws, "优先级 × 交付批次 分布矩阵", "用于判断“先做什么”：P0 优先保障，P3 视资源投入", 7)
r = hdr + 1
mat = {}
for r_ in rows:
    mat[(r_["prio"], r_["stage"])] = mat.get((r_["prio"], r_["stage"]), 0) + 1
eff = {}
for r_ in rows:
    eff[(r_["prio"], r_["stage"])] = eff.get((r_["prio"], r_["stage"]), 0) + r_["effort"]
ws.cell(row=r, column=1, value="优先级 \\ 批次")
for j, st in enumerate(["MVP", "V1", "V2", "V3"], start=2):
    ws.cell(row=r, column=j, value=st)
ws.cell(row=r, column=6, value="合计")
style_header(ws, r, BLUE)
r += 1
for p in ["P0", "P1", "P2", "P3"]:
    ws.cell(row=r, column=1, value=p)
    for j, st in enumerate(["MVP", "V1", "V2", "V3"], start=2):
        v = mat.get((p, st), 0)
        ws.cell(row=r, column=j, value=v if v else "—")
        ws.cell(row=r, column=j).alignment = Alignment(horizontal="center")
    ws.cell(row=r, column=6, value=sum(mat.get((p, st), 0) for st in ["MVP", "V1", "V2", "V3"]))
    r += 1
ws.cell(row=r, column=1, value="合计").font = Font(name="微软雅黑", size=9, bold=True)
for j, st in enumerate(["MVP", "V1", "V2", "V3"], start=2):
    ws.cell(row=r, column=j, value=sum(mat.get((p, st), 0) for p in ["P0", "P1", "P2", "P3"])).font = Font(name="微软雅黑", size=9, bold=True)
ws.cell(row=r, column=6, value=len(rows)).font = Font(name="微软雅黑", size=9, bold=True)
r += 2
ws.cell(row=r, column=1, value="按工程量（人天）").font = Font(name="微软雅黑", size=11, bold=True, color=NAVY)
r += 1
ws.cell(row=r, column=1, value="优先级 \\ 批次")
for j, st in enumerate(["MVP", "V1", "V2", "V3"], start=2):
    ws.cell(row=r, column=j, value=st)
ws.cell(row=r, column=6, value="合计")
style_header(ws, r, BLUE)
r += 1
for p in ["P0", "P1", "P2", "P3"]:
    ws.cell(row=r, column=1, value=p)
    for j, st in enumerate(["MVP", "V1", "V2", "V3"], start=2):
        ws.cell(row=r, column=j, value=eff.get((p, st), 0))
        ws.cell(row=r, column=j).alignment = Alignment(horizontal="center")
    ws.cell(row=r, column=6, value=sum(eff.get((p, st), 0) for st in ["MVP", "V1", "V2", "V3"]))
    r += 1
ws.cell(row=r, column=1, value="合计").font = Font(name="微软雅黑", size=9, bold=True)
for j, st in enumerate(["MVP", "V1", "V2", "V3"], start=2):
    ws.cell(row=r, column=j, value=sum(eff.get((p, st), 0) for p in ["P0", "P1", "P2", "P3"])).font = Font(name="微软雅黑", size=9, bold=True)
ws.cell(row=r, column=6, value=sum(eff.values())).font = Font(name="微软雅黑", size=9, bold=True)
style_body(ws, hdr + 1, r)
set_widths(ws, [20, 12, 12, 12, 12, 12])

# ============================================================
# SHEET 策略：模块汇总
# ============================================================
ws = wb.create_sheet("03-模块汇总")
head = ["模块编号", "一级模块", "模块定位", "功能项数", "MVP", "V1", "V2", "V3", "工程量(人天)", "人力成本(元)"]
ws.append(head)
style_header(ws, 1)
for mid, mname, mprio, mstage, mdesc in MODULES:
    s = mods[mid]
    st = s["stages"]
    ws.append([mid, mname, mdesc, s["count"], st.get("MVP", 0), st.get("V1", 0), st.get("V2", 0), st.get("V3", 0),
               s["effort"], s["effort"] * RATE])
ws.append(["合计", "", "", len(rows),
           sum(mods[m[0]]["stages"].get("MVP", 0) for m in MODULES),
           sum(mods[m[0]]["stages"].get("V1", 0) for m in MODULES),
           sum(mods[m[0]]["stages"].get("V2", 0) for m in MODULES),
           sum(mods[m[0]]["stages"].get("V3", 0) for m in MODULES),
           sum(mods[m[0]]["effort"] for m in MODULES),
           sum(mods[m[0]]["effort"] for m in MODULES) * RATE])
style_body(ws, 2)
for c in ws[ws.max_row]:
    c.font = Font(name="微软雅黑", size=9, bold=True)
    c.fill = PatternFill("solid", fgColor=LIGHT)
for rr in range(2, ws.max_row + 1):
    ws.cell(row=rr, column=10).number_format = '#,##0'
set_widths(ws, [10, 22, 40, 10, 8, 8, 8, 8, 14, 16])

# ============================================================
# SHEET 硬件清单
# ============================================================
ws = wb.create_sheet("04-硬件清单与预算")
hdr = title_block(ws, "硬件设备清单与投资估算（中等规模中职 · 单校区 3000—6000 人）",
                  "单价为 2026 年市场主流品牌公开报价区间中位值估算，实际采购以招标结果为准；金额单位：元（含税）；QTY 列为按阶段投放数量，可自行调整", 13)
r = hdr + 1
head = ["序号", "类别", "设备/材料名称", "推荐规格要点", "单位", "总量",
        "MVP投放", "V1投放", "V2投放", "V3投放", "参考单价(元)", "小计(元)", "MVP阶段金额(元)"]
for i, h in enumerate(head, start=1):
    ws.cell(row=r, column=i, value=h)
style_header(ws, r, NAVY)
# (类别, 名称, 规格, 单位, 总量, MVP, V1, V2, V3, 单价)
HW = [
    ("出入口与门禁", "人脸识别门禁一体机", "8 英寸屏，人脸+刷卡+二维码，韦根/网口，活体检测", "台", 45, 10, 20, 10, 5, 2600),
    ("出入口与门禁", "三辊闸/翼闸通道", "不锈钢桥式翼闸，含控制器，支持消防联动", "通道", 12, 4, 5, 2, 1, 9500),
    ("出入口与门禁", "全高转闸", "双向全高转闸，用于校门人行管控", "台", 4, 2, 2, 0, 0, 21000),
    ("出入口与门禁", "访客自助登记终端", "身份证读取+人脸采集+凭条打印+二维码发放", "台", 2, 1, 1, 0, 0, 18000),
    ("出入口与门禁", "电磁锁/电插锁及门禁控制器", "含出门按钮、门磁、UPS 后备", "套", 60, 6, 24, 22, 8, 800),
    ("车辆管理", "车牌识别一体机", "500 万像素，含补光与识别算法，识别率≥99%", "台", 6, 0, 4, 2, 0, 8500),
    ("车辆管理", "道闸（直杆/曲杆）", "快速道闸 3 秒起落，含地感线圈与防砸雷达", "台", 6, 0, 4, 2, 0, 6500),
    ("车辆管理", "车辆引导屏与余位屏", "户外 LED 双基色，含控制卡", "块", 4, 0, 0, 3, 1, 4500),
    ("视频监控", "网络枪型摄像机", "400 万像素，红外 50m，H.265，ONVIF/GB28181", "台", 180, 24, 76, 55, 25, 620),
    ("视频监控", "网络半球摄像机", "400 万像素，室内走廊与教室楼道", "台", 120, 0, 48, 60, 12, 560),
    ("视频监控", "智能球型摄像机", "800 万像素，25 倍变焦，含 AI 事件抓拍", "台", 22, 2, 8, 8, 4, 4200),
    ("视频监控", "AI 边缘计算盒子", "16 路视频分析，支持烟火/周界/聚集等算法", "台", 4, 1, 2, 1, 0, 16500),
    ("视频监控", "NVR 网络录像机", "64 路接入，16 盘位，支持 RAID5", "台", 4, 1, 2, 1, 0, 12000),
    ("视频监控", "监控级硬盘", "8TB 企业级监控硬盘（满足 30 天存储）", "块", 48, 8, 20, 16, 4, 1250),
    ("网络与传输", "核心交换机", "24 口万兆上行三层交换机", "台", 2, 1, 1, 0, 0, 18000),
    ("网络与传输", "PoE 接入交换机", "24 口千兆 PoE+，370W", "台", 26, 4, 12, 8, 2, 3200),
    ("网络与传输", "光纤与布线辅材", "室外单模光纤、桥架、网线、机柜、配线架", "批", 1, 0.3, 0.4, 0.2, 0.1, 165000),
    ("网络与传输", "无线 AP（室外/室内）", "Wi-Fi 6，室外防水型与室内吸顶型", "台", 40, 6, 18, 12, 4, 1450),
    ("物联感知", "一键报警柱", "含对讲、爆闪灯、定位上报", "台", 6, 0, 2, 3, 1, 12500),
    ("物联感知", "电子巡更点与巡更棒", "NFC 巡更点 100 个 + 巡更终端 6 套", "批", 1, 0, 0.5, 0.5, 0, 21000),
    ("物联感知", "环境传感器套装", "温湿度、CO₂、PM2.5、噪声、光照", "套", 30, 0, 0, 20, 10, 1150),
    ("物联感知", "智能电表（分项计量）", "三相/单相，支持 Modbus-TCP/485", "只", 90, 0, 0, 60, 30, 850),
    ("物联感知", "智能水表（远传）", "DN25—DN100，支持 NB-IoT/485", "只", 45, 0, 0, 30, 15, 950),
    ("物联感知", "智能水电控终端（宿舍）", "预付费水电控一体，支持远程通断", "间", 260, 0, 0, 160, 100, 480),
    ("物联感知", "消防主机联网模块", "支持主流消防主机协议对接与报警上传", "套", 1, 0, 0, 0, 1, 28000),
    ("终端与显示", "电子班牌", "21.5 英寸，考勤+信息发布+通知", "台", 60, 0, 0, 30, 30, 3400),
    ("终端与显示", "信息发布大屏（校门/大厅）", "55 英寸落地式 or 拼接屏（2×2）", "套", 4, 1, 1, 1, 1, 26000),
    ("终端与显示", "数据驾驶舱大屏", "98 英寸商用显示器 + 播控主机", "套", 1, 0, 1, 0, 0, 78000),
    ("基础设施", "应用服务器", "2U 机架式，2×银牌 CPU/128G/2×960G SSD+4×4T", "台", 2, 1, 1, 0, 0, 62000),
    ("基础设施", "AI 推理服务器", "含 GPU 加速卡（单卡 24G 显存级）×2", "台", 1, 0, 1, 0, 0, 145000),
    ("基础设施", "存储与备份设备", "视频/文件存储 48TB 可用 + 备份一体机", "套", 1, 0.5, 0.5, 0, 0, 96000),
    ("基础设施", "机柜、UPS 与机房改造", "42U 机柜、10KVA UPS、空调与动环监测", "批", 1, 0.5, 0.5, 0, 0, 88000),
]
for i, hw in enumerate(HW, start=1):
    row_i = r + i
    ws.cell(row=row_i, column=1, value=i)
    ws.cell(row=row_i, column=2, value=hw[0])
    ws.cell(row=row_i, column=3, value=hw[1])
    ws.cell(row=row_i, column=4, value=hw[2])
    ws.cell(row=row_i, column=5, value=hw[3])
    ws.cell(row=row_i, column=6, value=hw[4])
    ws.cell(row=row_i, column=7, value=hw[5])
    ws.cell(row=row_i, column=8, value=hw[6])
    ws.cell(row=row_i, column=9, value=hw[7])
    ws.cell(row=row_i, column=10, value=hw[8])
    ws.cell(row=row_i, column=11, value=hw[9])
    ws.cell(row=row_i, column=12, value=f"=ROUND(F{row_i}*K{row_i},0)")
    ws.cell(row=row_i, column=13, value=f"=ROUND(G{row_i}*K{row_i},0)")
hr = r
last = r + len(HW)
r = last + 2
ws.cell(row=r, column=3, value="硬件小计（单校区全场景基准配置）").font = Font(name="微软雅黑", size=10, bold=True)
ws.cell(row=r, column=12, value=f"=SUM(L{hr+1}:L{last})").font = Font(name="微软雅黑", size=10, bold=True)
for c in ws[r]:
    c.fill = PatternFill("solid", fgColor=LIGHT)
rows_extra = [
    ("安装施工与集成调试（按硬件 18% 计）", f"=ROUND(L{r}*0.18,0)"),
    ("硬件与集成总计（单校区全场景）", f"=L{r}+L{r+1}"),
    ("IT 基础设施小计（服务器 + GPU + 存储 + 机柜 UPS，不含摄像机闸机与土建）", "138000"),
    ("竞赛/验证版配置（1 个校门 + 6 路 AI + 1 台边缘盒子 + 复用现有网络与机房）", "240000"),
    ("双校区旗舰配置（全场景覆盖 + 冗余设备 + 数字孪生大屏）", f"=ROUND(L{r+2}*1.8,0)"),
]
for k, (label, formula) in enumerate(rows_extra, start=1):
    rr = r + k
    ws.cell(row=rr, column=3, value=label)
    ws.cell(row=rr, column=12, value=formula)
ws.cell(row=r + 2, column=3).font = Font(name="微软雅黑", size=10, bold=True)
ws.cell(row=r + 2, column=12).font = Font(name="微软雅黑", size=10, bold=True)
ws.cell(row=r + 6, column=3, value="成本口径说明（与《总体技术架构方案》对齐）：IT 基础设施（应用服务器、AI 推理服务器、存储与备份、机柜 UPS）"
                                   "约 13.8 万元，架构方案表述为“12—15 万元起”；本表“基础设施”类合计 46 万元是在此基础上"
                                   "叠加机房土建改造、冗余配置与安装调试后的完整口径。对外汇报建议按低预算口径表述："
                                   "“IT 基础设施 12—15 万元起，含机房改造与冗余约 46 万元”。").font = Font(name="微软雅黑", size=8, color="808080")
ws.cell(row=r + 5, column=3, value="按阶段投放的硬件金额（由上方 QTY 列公式汇总，可直接用于年度预算立项）").font = Font(name="微软雅黑", size=10, bold=True, color=NAVY)
phase_rows = [
    ("MVP 阶段（最小可用闭环）", "=SUM(M{0}:M{1})".format(hr + 1, last)),
    ("V1 阶段（首个商业版本）", "=SUMPRODUCT(H{0}:H{1},K{0}:K{1})".format(hr + 1, last)),
    ("V2 阶段（平台化增强）", "=SUMPRODUCT(I{0}:I{1},K{0}:K{1})".format(hr + 1, last)),
    ("V3 阶段（智能化与生态）", "=SUMPRODUCT(J{0}:J{1},K{0}:K{1})".format(hr + 1, last)),
]
for k, (label, formula) in enumerate(phase_rows, start=1):
    rr = r + 5 + k
    ws.cell(row=rr, column=3, value=label)
    ws.cell(row=rr, column=12, value=formula)
sum_row = r + 5 + len(phase_rows) + 1
ws.cell(row=sum_row, column=3, value="阶段投放合计").font = Font(name="微软雅黑", size=9, bold=True)
ws.cell(row=sum_row, column=12, value=f"=SUM(L{r+6}:L{r+5+len(phase_rows)})").font = Font(name="微软雅黑", size=9, bold=True)
style_body(ws, hr + 1, sum_row)
for rr in list(range(r, r + 6)) + list(range(r + 6, sum_row + 1)):
    ws.cell(row=rr, column=12).number_format = '#,##0'
set_widths(ws, [6, 16, 30, 46, 6, 7, 8, 8, 8, 8, 12, 16, 16])

# ============================================================
# SHEET 团队与产能
# ============================================================
ws = wb.create_sheet("05-团队与产能")
hdr = title_block(ws, "团队角色配置与产能测算", "产能口径：每人每天有效投入约 4 小时（课业并行），每周 5 个工作日", 7)
r = hdr + 1
head = ["角色", "建议人数", "核心职责", "关键技能", "人天/周·人", "月度产能(人天)", "缺口与补充建议"]
for i, h in enumerate(head, start=1):
    ws.cell(row=r, column=i, value=h)
style_header(ws, r, BLUE)
TEAM = [
    ("项目负责人 / 产品经理", 1, "需求管理、排期、对外沟通、验收汇报", "需求分析、原型设计、PPT 表达", 4, 16, "建议由指导教师担任，学生骨干任副手"),
    ("AI 算法工程师", 2, "数据采集标注、模型训练调优、边缘部署", "Python、PyTorch、YOLO、OpenCV", 4, 32, "当前最大能力缺口，需专项培训或企业导师"),
    ("后端开发工程师", 2, "业务服务、设备接入、接口与数据库", "Python/FastAPI、PostgreSQL、Redis、MQTT", 4, 32, "可由高年级学生梯队培养"),
    ("前端开发工程师", 2, "Web 管理端、驾驶舱大屏、小程序", "Vue3、TypeScript、ECharts、uni-app", 4, 32, "已有竞赛基础，能力可满足"),
    ("测试与实施工程师", 1, "功能测试、设备联调、部署交付、培训", "测试用例设计、Linux、网络基础", 4, 16, "需补充 1 名，兼设备联调"),
    ("文档与答辩", 0.5, "文档编制、演示脚本、录像与答辩", "技术写作、演讲、视频剪辑", 4, 8, "可由产品经理兼任"),
]
for i, t in enumerate(TEAM, start=1):
    for j, v in enumerate(t, start=1):
        ws.cell(row=r + i, column=j, value=v)
tr = r
r = r + len(TEAM) + 1
ws.cell(row=r, column=1, value="合计").font = Font(name="微软雅黑", size=9, bold=True)
ws.cell(row=r, column=2, value=f"=SUM(B{tr+1}:B{tr+len(TEAM)})")
ws.cell(row=r, column=6, value=f"=SUM(F{tr+1}:F{tr+len(TEAM)})")
for c in ws[r]:
    c.fill = PatternFill("solid", fgColor=LIGHT)
    c.font = Font(name="微软雅黑", size=9, bold=True)
style_body(ws, tr + 1, r)
set_widths(ws, [24, 10, 38, 34, 12, 14, 40])

# ============================================================
# SHEET 投资与预算情景
# ============================================================
ws = wb.create_sheet("06-投资与预算情景")
hdr = title_block(ws, "软件开发与实施投资估算（按建设范围分情景）",
                  f"人天单价 {RATE} 元（商业级综合单价，含税）；软件与硬件分列，便于按年度预算切分；硬件为分阶段投放口径，不含既往已有设备", 6)
r = hdr + 1
head = ["情景", "覆盖范围", "软件工程量(人天)", "软件与实施金额(元)", "硬件与集成金额(元)", "合计(元)"]
for i, h in enumerate(head, start=1):
    ws.cell(row=r, column=i, value=h)
style_header(ws, r, BLUE)
mvp = stages["MVP"]["effort"]; v1 = stages["V1"]["effort"]
v2 = stages["V2"]["effort"]; v3 = stages["V3"]["effort"]
SCEN = [
    ("情景一：竞赛/验证版", "从 31 项 MVP 功能中精选约 18 项 P0 核心（统一身份、门禁通行、请假联动、周界与烟火识别、事件派单）≈147 人天", 147, 176400, 240000),
    ("情景二：最小可用版（推荐起步）", "MVP 全批次 31 项 P0 功能（479 人天）+ MVP 阶段硬件（1 个校门 + 55 路视频 + 1 台 AI 边缘盒子）", mvp, mvp * RATE, 542000),
    ("情景三：一期建设（推荐落地）", "MVP + V1 共 75 项功能（1039 人天）+ MVP/V1 两阶段硬件（车辆、归寝、驾驶舱、移动端全部可用）", mvp + v1, (mvp + v1) * RATE, 2000000),
    ("情景四：平台化完整交付", "MVP + V1 + V2 共 113 项功能（1494 人天）+ 一卡通、能耗、设施运维全场景硬件", mvp + v1 + v2, (mvp + v1 + v2) * RATE, 2990000),
    ("情景五：三年全域（含 V3）", "全部 131 项功能与三年迭代（1705 人天）+ 双校区旗舰硬件（含数字孪生大屏、冗余设备）", mvp + v1 + v2 + v3, (mvp + v1 + v2 + v3) * RATE, 5386000),
]
for i, s in enumerate(SCEN, start=1):
    for j, v in enumerate(s, start=1):
        ws.cell(row=r + i, column=j, value=v)
sr = r
r = r + len(SCEN) + 1
style_body(ws, sr + 1, sr + len(SCEN))
for rr in range(sr + 1, sr + len(SCEN) + 1):
    ws.cell(row=rr, column=6, value=f"=D{rr}+E{rr}").number_format = '#,##0'
    ws.cell(row=rr, column=4).number_format = '#,##0'
    ws.cell(row=rr, column=5).number_format = '#,##0'
ws.cell(row=r, column=1, value="说明：情景一为竞赛冲刺所需最小投入；情景二/三为“能真正用起来”的推荐路径；情景四覆盖平台化能力；情景五为三年演进总投入。"
                               "硬件金额与“04-硬件清单与预算”工作表中的阶段投放一致。").font = Font(name="微软雅黑", size=8, color="808080")
ws.cell(row=r + 1, column=1, value="★ 低预算申报口径（建议）：优先按情景一/情景二申报，即“软件自研 + 硬件分阶段小额投放”。"
                                   "IT 基础设施一项按低值表述为“12—15 万元起”（应用服务器 + AI 推理服务器 + 存储备份 + 机柜 UPS 约 13.8 万元），"
                                   "机房土建改造与冗余配置作为可选项，待经费允许时再列入；情景四/五的完整口径仅作三年规划参考，不作为首年申报金额。"
                  ).font = Font(name="微软雅黑", size=8, bold=True, color="C00000")
set_widths(ws, [26, 60, 18, 20, 20, 18])

# ============================================================
# SHEET 里程碑
# ============================================================
ws = wb.create_sheet("07-里程碑计划")
hdr = title_block(ws, "阶段性里程碑计划（自 2026 年 12 月启动）", "起止周为相对项目启动周；交付物与验收标准详见《实施路线图与里程碑计划》", 7)
r = hdr + 1
head = ["里程碑", "阶段", "起止周", "计划时间", "关键交付物", "工程量(人天)", "验收标准（一句话）"]
for i, h in enumerate(head, start=1):
    ws.cell(row=r, column=i, value=h)
style_header(ws, r, BLUE)
MS = [
    ("M0 立项与需求冻结", "准备", "W0", "2026-12", "需求规格说明书、功能清单、项目章程、团队分工", 15, "需求与验收标准评审通过并签字确认"),
    ("M1 环境与底座打通", "MVP", "W1—W3", "2026-12—2027-01", "开发环境、数据库、统一身份、组织与场所建模", 80, "人员/组织/场所数据可维护，接口联调通过"),
    ("M2 门禁与请假闭环", "MVP", "W4—W8", "2027-01—2027-02", "门禁对接、通行策略、请假放行、通行记录", 150, "刷脸/刷卡开门 ≤300ms，无假条离校 100% 拦截"),
    ("M3 AI 预警与事件派单", "MVP", "W6—W11", "2027-02—2027-03", "视频接入、2 类 AI 算法、事件工单闭环", 150, "周界与烟火识别准确率 ≥90%，事件 100% 可闭环"),
    ("M4 MVP 发布（竞赛版）", "MVP", "W12", "2027-04", "可演示系统、数据集、演示脚本、测试报告", 84, "20 分钟现场演示零卡顿，全部 P0 功能通过内测"),
    ("M5 车辆与归寝上线", "V1", "W13—W20", "2027-04—2027-06", "车辆管理、宿舍归寝、晚归预警、家校通知", 200, "归寝统计自动化率 100%，未归预警 ≤5 分钟送达"),
    ("M6 考勤协同与驾驶舱", "V1", "W19—W26", "2027-06—2027-08", "教职工考勤、OA 审批、通知中心、数据驾驶舱", 180, "考勤月度汇总零人工干预，驾驶舱数据 T+0"),
    ("M7 V1.0 正式发布（校内推广）", "V1", "W27—W28", "2027-08", "正式版、部署包、操作手册、培训与验收", 180, "完成 3 场培训，验收测试用例通过率 ≥95%"),
    ("M8 平台化增强（V2）", "V2", "W29—W44", "2027-09—2028-02", "一卡通、能耗、设施运维、自定义报表、多校区", 455, "新增模块全部通过验收，支持 2 个校区独立运行"),
    ("M9 智能化与生态（V3）", "V3", "W45—W64", "2028-03—2028-10", "数字孪生大屏、语音助手、开放 API、低碳校园", 211, "完成外部学校试点 2 所以上并出具成效报告"),
]
for i, m in enumerate(MS, start=1):
    for j, v in enumerate(m, start=1):
        ws.cell(row=r + i, column=j, value=v)
style_body(ws, r + 1, r + len(MS))
set_widths(ws, [26, 8, 12, 20, 46, 14, 44])

wb.save(OUT)
print("已生成:", OUT)
print("功能项:", len(rows), "总人天:", sum(r['effort'] for r in rows))
