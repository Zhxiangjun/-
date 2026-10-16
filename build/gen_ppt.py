# -*- coding: utf-8 -*-
"""生成 06_项目汇报PPT.pptx（答辩/评审口径）"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from feature_master import build, MODULES, stage_summary
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION, XL_TICK_MARK

OUT = r"F:\职业中专\大赛\智慧园区创意\06_项目汇报PPT.pptx"

rows = build()
st = stage_summary(rows)

NAVY = RGBColor(0x14, 0x2A, 0x4C)
BLUE = RGBColor(0x1E, 0x5C, 0x9E)
LBLUE = RGBColor(0xE8, 0xF0, 0xF9)
ORANGE = RGBColor(0xE8, 0x7A, 0x1E)
GRAY = RGBColor(0x55, 0x5F, 0x6D)
LGRAY = RGBColor(0xF2, 0xF4, 0xF7)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HEI = "微软雅黑"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
SW, SH = 13.333, 7.5


def slide():
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(s, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, lw=1):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    return sh


def text(s, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    """runs: list of (text, size, bold, color) 或 list of 段落（每个段落是 runs 列表）"""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    paras = runs if isinstance(runs[0], list) else [runs]
    for i, pruns in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        if isinstance(pruns, str):
            pruns = [(pruns, 14, False, GRAY)]
        for j, item in enumerate(pruns):
            t, sz, bold, color = (list(item) + [False, GRAY])[:4] if isinstance(item, tuple) else (item, 14, False, GRAY)
            r = p.add_run()
            r.text = t
            r.font.size = Pt(sz)
            r.font.bold = bold
            r.font.color.rgb = color
            r.font.name = HEI
            r.font._rPr.set('lang', 'zh-CN')
    return tb


def header(s, idx, title, sub=""):
    rect(s, 0, 0, SW, 0.95, fill=NAVY)
    rect(s, 0, 0.95, SW, 0.06, fill=ORANGE)
    text(s, 0.55, 0.14, 11.0, 0.7, [[(f"{idx:02d}  ", 22, True, ORANGE), (title, 22, True, WHITE)]],
         anchor=MSO_ANCHOR.MIDDLE)
    if sub:
        text(s, 0.6, 1.12, 12.2, 0.4, [(sub, 11.5, False, GRAY)])


def footer(s, page):
    text(s, 0.6, SH - 0.45, 9.0, 0.3, [("“智园卫士”智慧校园管理平台 ｜ 齐河县职业中专", 9, False, RGBColor(0x99, 0x9F, 0xA8))])
    text(s, 11.6, SH - 0.45, 1.2, 0.3, [(str(page), 9.5, True, GRAY)], align=PP_ALIGN.RIGHT)


def cards(s, items, y=1.75, h=4.6, gap=0.25, x0=0.6, total=12.13):
    n = len(items)
    w = (total - gap * (n - 1)) / n
    for i, (title, lines) in enumerate(items):
        x = x0 + i * (w + gap)
        rect(s, x, y, w, h, fill=LGRAY)
        rect(s, x, y, w, 0.55, fill=BLUE)
        text(s, x + 0.12, y + 0.06, w - 0.24, 0.45, [(title, 13, True, WHITE)],
             align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        body = []
        for ln in lines:
            body.append([("▪ ", 10.5, True, ORANGE), (ln, 10.5, False, RGBColor(0x33, 0x38, 0x40))])
        if body:
            text(s, x + 0.14, y + 0.72, w - 0.28, h - 0.85, body, spacing=1.22)


def table(s, x, y, w, h, headers, data, col_ratios=None, fs=10, hfs=10.5):
    shp = s.shapes.add_table(len(data) + 1, len(headers), Inches(x), Inches(y), Inches(w), Inches(h))
    tb = shp.table
    if col_ratios:
        tot = sum(col_ratios)
        for i, r in enumerate(col_ratios):
            tb.columns[i].width = Emu(int(Inches(w) * r / tot))
    for j, htxt in enumerate(headers):
        c = tb.cell(0, j)
        c.text = ""
        p = c.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = htxt
        r.font.size = Pt(hfs); r.font.bold = True; r.font.color.rgb = WHITE; r.font.name = HEI
        c.fill.solid(); c.fill.fore_color.rgb = NAVY
        c.vertical_anchor = MSO_ANCHOR.MIDDLE
        c.margin_left = c.margin_right = Emu(0)
    for i, row in enumerate(data, start=1):
        for j, v in enumerate(row):
            c = tb.cell(i, j)
            c.text = ""
            p = c.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if j == len(headers) - 1 else PP_ALIGN.CENTER
            r = p.add_run(); r.text = str(v)
            r.font.size = Pt(fs); r.font.color.rgb = RGBColor(0x33, 0x38, 0x40); r.font.name = HEI
            c.fill.solid(); c.fill.fore_color.rgb = WHITE if i % 2 else LGRAY
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
            c.margin_left = c.margin_right = Emu(0)
    return tb


# ============================================================
# 原生可编辑图表
# ============================================================
def _style_chart(chart, fs=11, legend=True, legend_pos=XL_LEGEND_POSITION.TOP):
    chart.font.size = Pt(fs)
    chart.font.name = HEI
    chart.has_title = False
    if legend:
        chart.has_legend = True
        chart.legend.position = legend_pos
        chart.legend.include_in_layout = False
    else:
        chart.has_legend = False


def add_stage_chart(s, x, y, w, h):
    keys = ["MVP", "V1", "V2", "V3"]
    cd = CategoryChartData()
    cd.categories = [f"MVP 最小可用\n{st['MVP']['count']} 项 / {st['MVP']['effort']} 人天",
                     f"V1.0 首个商业版\n{st['V1']['count']} 项 / {st['V1']['effort']} 人天",
                     f"V2.0 平台化\n{st['V2']['count']} 项 / {st['V2']['effort']} 人天",
                     f"V3.0 智能化\n{st['V3']['count']} 项 / {st['V3']['effort']} 人天"]
    cd.add_series("工程量（人天）", tuple(st[k]["effort"] for k in keys))
    gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    _style_chart(ch, fs=11, legend=False)
    ch.plots[0].gap_width = 110
    ser = ch.series[0]
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = BLUE
    ser.has_data_labels = True
    dl = ser.data_labels
    dl.font.size = Pt(12); dl.font.bold = True; dl.font.name = HEI
    dl.font.color.rgb = NAVY
    dl.position = XL_LABEL_POSITION.OUTSIDE_END
    va = ch.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xDD, 0xDD)
    va.major_gridlines.format.line.width = Pt(0.5)
    va.tick_labels.font.size = Pt(10)
    ch.category_axis.tick_labels.font.size = Pt(10.5)
    return ch


def _add_secondary_axis(chart):
    """把第 2 个系列移到次坐标轴（python-pptx 原生不支持，直接操作 XML）。"""
    from pptx.oxml.ns import qn as _qn
    from copy import deepcopy
    from lxml import etree
    plotArea = chart._chartSpace.find(_qn('c:chart')).find(_qn('c:plotArea'))
    barChart = plotArea.find(_qn('c:barChart'))
    layout = barChart.find(_qn('c:layout'))
    if layout is not None:
        barChart.remove(layout)
    ser1 = barChart.findall(_qn('c:ser'))[1]
    axId = [int(e.get('val')) for e in barChart.findall(_qn('c:axId'))]
    barChart.remove(ser1)
    barChart.remove(barChart.find(_qn('c:gapWidth')))
    overlap = barChart.find(_qn('c:overlap'))
    if overlap is not None:
        barChart.remove(overlap)
    # 主轴只留第 1 系列
    for tag in ('c:gapWidth', 'c:overlap'):
        el = etree.SubElement(barChart, _qn(tag))
        el.set('val', '80' if tag == 'c:gapWidth' else '-10')
    barChart2 = deepcopy(barChart)
    for s_ in barChart2.findall(_qn('c:ser')):
        barChart2.remove(s_)
    # 次轴需要新的 axId（取主轴最大值 +1、+2）
    new_x, new_y = max(axId) + 1, max(axId) + 2
    for e in barChart2.findall(_qn('c:axId')):
        e.set('val', str(new_x if e.get('val') == str(axId[0]) else new_y))
    ser1_axids = [deepcopy(e) for e in barChart.findall(_qn('c:axId'))]
    if not ser1_axids:
        ser1_axids = [etree.SubElement(ser1, _qn('c:axId')), etree.SubElement(ser1, _qn('c:axId'))]
    ser1_axids[0].set('val', str(new_x))
    ser1_axids[1].set('val', str(new_y))
    for e in ser1_axids:
        ser1.append(e)
    barChart2.append(ser1)
    plotArea.append(barChart2)
    # 新增次坐标轴定义
    catAx = plotArea.find(_qn('c:catAx'))
    valAx = plotArea.find(_qn('c:valAx'))
    new_catAx = deepcopy(catAx)
    new_valAx = deepcopy(valAx)
    for ax, ids in ((new_catAx, (new_x, new_y)), (new_valAx, (new_y, new_x))):
        for e in ax.findall(_qn('c:axId')):
            e.set('val', str(ids[0]))
        for tag in ('c:crossAx',):
            e = ax.find(_qn(tag))
            if e is not None:
                e.set('val', str(ids[1]))
        d = ax.find(_qn('c:delete'))
        if d is not None:
            d.set('val', '0')
        # 删掉次轴上的标题与网格线，保持画面干净
        for tag in ('c:majorGridlines', 'c:title'):
            el = ax.find(_qn(tag))
            if el is not None:
                ax.remove(el)
    ma = new_valAx.find(_qn('c:majorGridlines'))
    if ma is not None:
        new_valAx.remove(ma)
    plotArea.append(new_catAx)
    plotArea.append(new_valAx)


def add_budget_chart(s, x, y, w, h):
    cd = CategoryChartData()
    cd.categories = ["软件与实施\n（MVP+V1）", "MVP 阶段\n硬件", "V1 阶段\n硬件", "V2+V3 阶段\n硬件"]
    cd.add_series("金额（万元）", (round((st["MVP"]["effort"] + st["V1"]["effort"]) * 1200 / 10000, 1),
                                    54.2, 119.8, 125.2))
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    _style_chart(ch, fs=10, legend=False)
    ch.plots[0].gap_width = 60
    ser = ch.series[0]
    ser.has_data_labels = True
    ser.data_labels.font.size = Pt(11)
    ser.data_labels.font.bold = True
    ser.data_labels.font.name = HEI
    ser.data_labels.number_format = '0.0"万"'
    ser.data_labels.number_format_is_linked = False
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = BLUE
    ch.value_axis.has_major_gridlines = True
    ch.value_axis.major_gridlines.format.line.color.rgb = RGBColor(0xDD, 0xDD, 0xDD)
    # 逐点着色，突出软件与 MVP 硬件
    from pptx.oxml.ns import qn as _qn
    colors = ["1E5C9E", "2E86C1", "E87A1E", "F0B27A"]
    for idx, c in enumerate(colors):
        pt = ser.points[idx]
        pt.format.fill.solid(); pt.format.fill.fore_color.rgb = RGBColor.from_string(c)
    return ch


def add_module_chart(s, x, y, w, h):
    items = sorted([(m[1], len([r for r in rows if r["mod"] == m[0]])) for m in MODULES],
                   key=lambda t: t[1])
    cd = CategoryChartData()
    cd.categories = [t[0] for t in items]
    cd.add_series("功能项数（项）", tuple(t[1] for t in items))
    gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(x), Inches(y), Inches(w), Inches(h), cd)
    ch = gf.chart
    _style_chart(ch, fs=10, legend=False)
    ch.plots[0].gap_width = 40
    ser = ch.series[0]
    ser.has_data_labels = True
    ser.data_labels.font.size = Pt(10); ser.data_labels.font.bold = True; ser.data_labels.font.name = HEI
    ser.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    ser.format.fill.solid(); ser.format.fill.fore_color.rgb = BLUE
    ch.category_axis.tick_labels.font.size = Pt(10)
    ch.value_axis.has_major_gridlines = False
    return ch

# ============================================================
# S1 封面
# ============================================================
s = slide()
rect(s, 0, 0, SW, SH, fill=NAVY)
rect(s, 0, 3.05, SW, 0.07, fill=ORANGE)
rect(s, 8.9, 0, 4.44, SH, fill=RGBColor(0x1B, 0x38, 0x60))
text(s, 0.9, 1.25, 11.5, 0.5, [("世界职业院校技能大赛 · 人工智能赛道（中职组）参赛项目", 14, False, RGBColor(0x9E, 0xC5, 0xE8))])
text(s, 0.9, 1.85, 11.5, 1.2, [("“智园卫士”", 48, True, WHITE)])
text(s, 0.9, 3.35, 11.5, 0.6, [("智慧校园（智慧园区）管理平台", 26, True, RGBColor(0x9E, 0xC5, 0xE8))])
text(s, 0.9, 4.15, 11.0, 1.4,
     [[("一句话定位：", 14, True, ORANGE), ("以 AI 视觉为亮点、以业务闭环为核心的校园智慧园区平台", 14, False, WHITE)],
      [("建设主体：", 14, True, ORANGE), ("齐河县职业中等专业学校 ｜ 中等规模中职 3000—6000 人 ｜ 1—2 个校区", 14, False, WHITE)],
      [("项目性质：", 14, True, ORANGE), ("真实校园落地 + 参赛演示 + 可对外复制交付的商业级产品", 14, False, WHITE)]],
     spacing=1.5)
text(s, 0.9, 6.35, 11.5, 0.5, [("2026 年 11 月 ｜ 项目组", 12, False, RGBColor(0x8A, 0x9B, 0xB0))])

# ============================================================
# S2 目录
# ============================================================
s = slide()
header(s, 0, "汇报提纲", "汇报时长约 20 分钟：问题与定位 4 分钟 ｜ 方案与功能 8 分钟 ｜ 技术亮点 4 分钟 ｜ 规划与合作 4 分钟")
ITEMS = [
    ("01", "我们看到的真问题", "校园管理仍靠人海战术，数据不通、留痕困难"),
    ("02", "项目定位与差异化", "不做设备堆叠，做业务闭环与数据打通"),
    ("03", "平台功能架构", "12 个模块、131 项功能，覆盖校园管理全场景"),
    ("04", "四大核心业务闭环", "通行即考勤、请假即放行、预警即派单、归寝有预警"),
    ("05", "AI 视觉技术亮点", "周界、烟火、聚集、打架等场景的识别与误报抑制"),
    ("06", "技术架构与实现路径", "端—边—云三层架构，断网可用、私有化部署"),
    ("07", "实施路线与里程碑", "四个批次、十个里程碑，每批都有可用成果"),
    ("08", "投资预算与效益分析", "分阶段小额投入，安全与效率双收益"),
    ("09", "安全合规与隐私保护", "人脸最小必要，提供替代方案，数据不出校园网"),
    ("10", "团队优势与预期成果", "竞赛成绩、落地成效与可复制方法论"),
]
for i, (no, title, desc) in enumerate(ITEMS):
    col, row = i % 2, i // 2
    x = 0.75 + col * 6.25
    y = 1.7 + row * 1.06
    rect(s, x, y, 5.85, 0.92, fill=LGRAY)
    rect(s, x, y, 0.72, 0.92, fill=BLUE)
    text(s, x, y + 0.12, 0.72, 0.7, [(no, 19, True, WHITE)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.9, y + 0.12, 4.8, 0.72,
         [[(title, 13.5, True, NAVY)], [(desc, 10, False, GRAY)]], spacing=1.15)
footer(s, 2)

# ============================================================
# S3 痛点
# ============================================================
s = slide()
header(s, 1, "我们看到的真问题", "校园规模 3000 人以上，管理手段却仍停留在“纸笔 + 对讲机 + 人盯屏幕”")
cards(s, [
    ("数据不通", ["监控、门禁、一卡通各自独立，形成数据孤岛", "人员信息在不同系统重复录入，口径不一", "统计报表靠人工汇总，耗时且易出错"]),
    ("管理靠人", ["学生请假靠纸质假条，无法核实离校去向", "宿舍查寝逐间点名，每晚耗时 60—90 分钟", "外来人员纸笔登记，事后几乎无法追溯"]),
    ("安防被动", ["报警靠人盯屏幕，发现滞后、容易漏看", "事发后翻录像查证，平均耗时长", "无处置记录，责任链条不清晰"]),
    ("投入受限", ["学校预算有限，无法一次性全面改造", "既有设备品牌杂、协议不通，难以整合", "缺少年轻技术力量持续运维"]),
], y=1.75, h=3.0)
rect(s, 0.6, 5.05, 12.13, 1.75, fill=LBLUE)
text(s, 0.95, 5.2, 11.5, 1.45,
     [[("结论：", 13, True, ORANGE), ("学校缺的不是更多的硬件，而是一套“把数据和业务串起来”的平台。", 13, True, NAVY)],
      [("", 8, False, WHITE)],
      [("我们的判断：", 12, True, BLUE), ("人员出入、车辆通行、宿舍归寝、安防应急这四条主线一旦打通，学校 80% 的日常安全管理痛点就能被数据化解决。", 12, False, RGBColor(0x33, 0x38, 0x40))]],
     spacing=1.3)
footer(s, 3)

# ============================================================
# S4 定位
# ============================================================
s = slide()
header(s, 2, "项目定位与差异化", "不是硬件集成项目，而是一套以 AI 视觉为亮点的校园管理平台")
text(s, 0.6, 1.5, 12.1, 0.5, [("一句话定位：让学校知道“谁在不在校、车能不能进、人有没有事、责任在谁”。", 15, True, NAVY)])
table(s, 0.6, 2.15, 12.13, 3.5,
      ["对比维度", "常见做法（硬件堆叠）", "“智园卫士”做法（业务闭环）"],
      [["建设思路", "买设备、装系统，各管一段", "先梳理业务，再决定需要什么数据与设备"],
       ["人员管理", "门禁只管开门", "通行记录自动成为考勤与在校状态依据"],
       ["学生请假", "纸质假条，离校无核验", "审批通过自动下发离校放行，返校自动销假"],
       ["异常处置", "报警弹出，处置靠电话催", "事件自动派单到责任人，超时自动升级，全程留痕"],
       ["数据价值", "数据留在各自系统里", "统一指标口径，驾驶舱 T+0，迎检一键生成"],
       ["成本控制", "一次性大额投入", "分四批投放，软件先行、硬件复用，可小步快跑"]],
      col_ratios=[1.1, 2.0, 2.4], fs=11.5, hfs=12)
text(s, 0.6, 6.0, 12.1, 0.9,
     [[("三大差异化优势：", 12.5, True, ORANGE)],
      [("① 业务闭环而非设备堆叠　② AI 算法自主可控、可按本校场景定制　③ 低成本、易交付、可私有化、可复制到同类学校", 12, False, RGBColor(0x33, 0x38, 0x40))]],
     spacing=1.3)
footer(s, 4)

# ============================================================
# S5 功能架构
# ============================================================
s = slide()
header(s, 3, "平台功能架构：12 个模块、131 项功能", "以统一身份与场所为底座，四条业务主线 + 平台与安全两大支撑")
MODC = [
    ("M01", "人员与组织管理", "统一身份、组织绑定、场所建模"),
    ("M02", "通行与门禁管理", "策略引擎、闸机鉴权、访客管理"),
    ("M03", "车辆管理", "车牌识别、授权放行、违规处置"),
    ("M04", "宿舍归寝管理", "床位台账、归寝统计、未归预警"),
    ("M05", "安防监控与应急", "视频接入、AI 算法、事件闭环"),
    ("M06", "教学与办公协同", "考勤、审批、通知、值班"),
    ("M07", "生活服务与一卡通", "消费、充值、水电控、预约"),
    ("M08", "能源与设施管理", "能耗监测、报修、预防性维护"),
    ("M09", "数据与决策分析", "数据中台、驾驶舱、报表上报"),
    ("M10", "安全与合规", "权限、审计、隐私合规、容灾"),
    ("M11", "移动端与智能交互", "小程序、家长端、自助终端"),
    ("M12", "平台与技术底座", "IoT 接入、规则引擎、工作流"),
]
mk = {m[0]: m for m in MODULES}
for i, (mid, name, desc) in enumerate(MODC):
    col, row = i % 4, i // 4
    x = 0.6 + col * 3.09
    y = 1.6 + row * 1.72
    n = len([r for r in rows if r["mod"] == mid])
    base_fill = BLUE if row < 2 else (ORANGE if row == 2 else GRAY)
    rect(s, x, y, 2.9, 1.55, fill=LGRAY)
    rect(s, x, y, 2.9, 0.42, fill=base_fill)
    text(s, x + 0.1, y + 0.02, 2.7, 0.38, [(f"{mid} {name}", 11, True, WHITE)], anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.12, y + 0.5, 2.66, 1.0,
         [[(desc, 9.5, False, RGBColor(0x33, 0x38, 0x40))],
          [(f"{n} 项功能", 10, True, ORANGE)]], spacing=1.15)
text(s, 0.6, 6.85, 12.1, 0.4, [("每条业务主线都以“可验收的业务动作”为落点：通行即考勤、请假即放行、预警即派单、归寝有预警。", 11.5, True, NAVY)])
footer(s, 5)

# ============================================================
# S6 核心闭环
# ============================================================
s = slide()
header(s, 4, "四大核心业务闭环", "这是本项目区别于普通硬件集成方案的关键，也是评委最容易看懂的亮点")
cards(s, [
    ("闭环一 · 通行即考勤", ["教职工刷脸进校 → 自动判定签到", "离校记录 → 自动判定签退", "异常自动生成待办 → 移动端申诉审批", "月度考勤自动汇总，零人工干预"]),
    ("闭环二 · 请假即放行", ["学生在小程序提交请假 → 班主任审批", "审批通过自动下发校门放行权限", "无假条离校 100% 拦截并通知班主任", "返校刷脸自动销假，超期自动提醒"]),
    ("闭环三 · 预警即派单", ["AI 识别异常 → 多帧确认抑制误报", "自动派单到区域责任人（含截图定位）", "3 分钟未接单自动升级上一级", "处置结果留痕归档，闭环率 100%"]),
    ("闭环四 · 归寝有预警", ["宿舍门禁数据自动核对归寝情况", "未归 → 宿管 → 班主任 → 学生科逐级通知", "同步推送家长端，责任可追溯", "请假在校外者自动免于判定，避免误报"]),
], y=1.7, h=4.05)
rect(s, 0.6, 5.95, 12.13, 0.85, fill=LBLUE)
text(s, 0.9, 6.05, 11.6, 0.65,
     [[("价值：", 12, True, ORANGE), ("把安全管理从事后追溯变成事中发现；把管理责任从“口头交代”变成“系统留痕”。", 12, True, NAVY)]],
     anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
footer(s, 6)

# ============================================================
# S7 AI 亮点
# ============================================================
s = slide()
header(s, 5, "AI 视觉技术亮点", "算法自主训练、按本校场景定制，并用工程手段把误报压到可接受水平")
cards(s, [
    ("识别场景", ["周界入侵与翻越：围墙、天台、危化品库", "烟火识别：宿舍、食堂、仓库早期预警", "人员聚集：门口、楼道、食堂密度预警", "打架与跌倒：操场、楼道异常行为", "消防通道占用：违规停车自动抓拍"]),
    ("工程手段", ["多帧确认：连续命中才生成事件，杜绝单帧误报", "区域过滤：屏蔽树枝晃动、车辆灯光等干扰源", "抑制窗口：同区域同类事件 5 分钟内只报一次", "分级策略：按置信度分为提示、告警、紧急"]),
    ("训练与评测", ["自建本校场景数据集，含夜间、逆光、雨雪样本", "YOLO 系列模型迁移学习，边缘设备量化部署", "独立测试集评测，训练与测试样本严格隔离", "设定误报红线（如烟火 ≤2 次/路·天）并持续迭代"]),
], y=1.7, h=4.2)
table(s, 0.6, 6.1, 12.13, 0.85,
      ["算法场景", "准确率目标", "召回率目标", "误报控制"],
      [["周界入侵 / 烟火识别 / 消防通道占用", "≥92% / ≥90% / ≥93%", "≥90% / ≥95% / —", "≤3 / ≤2 / ≤2 次每路每天"]],
      col_ratios=[2.2, 1.6, 1.4, 1.4], fs=11.5, hfs=11.5)
footer(s, 7)

# ============================================================
# S8 技术架构
# ============================================================
s = slide()
header(s, 6, "技术架构与实现路径", "端—边—云三层架构：硬件尽量简单，能力尽量放在软件与算法上")
LAYERS = [
    ("展现层", "管理端 Web（Vue3）｜ 驾驶舱大屏 ｜ 微信小程序（教职工/学生/家长）｜ 自助终端与信息发布", BLUE),
    ("应用层", "人员与组织 ｜ 通行门禁 ｜ 车辆 ｜ 宿舍归寝 ｜ 安防与事件 ｜ 协同办公 ｜ 生活服务 ｜ 能源设施 ｜ 数据分析", ORANGE),
    ("平台层", "统一身份与权限 ｜ 规则引擎 ｜ 工作流引擎 ｜ 通知中心 ｜ 数据中台 ｜ IoT 设备接入 ｜ 视频网关", RGBColor(0x1A, 0xBC, 0x9C)),
    ("边缘层", "AI 边缘计算盒子：视频推理（15FPS/路）｜ 断网本地放行 ｜ 告警本地上报 ｜ 数据缓存补传", RGBColor(0x7D, 0x3C, 0x98)),
    ("感知层", "门禁一体机与闸机 ｜ 车牌识别与道闸 ｜ 网络摄像机与 NVR ｜ 访客机 ｜ 传感器与智能水电表 ｜ 报警柱", GRAY),
]
y = 1.62
for name, desc, color in LAYERS:
    rect(s, 0.6, y, 1.5, 0.88, fill=color)
    text(s, 0.6, y, 1.5, 0.88, [(name, 13, True, WHITE)], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    rect(s, 2.2, y, 10.53, 0.88, fill=LGRAY)
    text(s, 2.42, y + 0.06, 10.1, 0.78, [(desc, 11, False, RGBColor(0x33, 0x38, 0x40))], anchor=MSO_ANCHOR.MIDDLE, spacing=1.15)
    y += 0.98
text(s, 0.6, y + 0.05, 12.1, 0.7,
     [[("技术选型：", 11.5, True, ORANGE), ("Python/FastAPI + Vue3 + PostgreSQL + Redis + EMQX + MinIO + ONNX Runtime；竞赛版与商业版同一代码基线，按配置切换。", 11.5, False, RGBColor(0x33, 0x38, 0x40))],
      [("可靠性设计：", 11.5, True, ORANGE), ("断网时门禁按本地白名单继续放行，恢复后自动补传；AI 分析异常不影响通行业务。", 11.5, False, RGBColor(0x33, 0x38, 0x40))]],
     spacing=1.25)
footer(s, 8)

# ============================================================
# S9 实施路线
# ============================================================
s = slide()
header(s, 7, "实施路线与里程碑", "四个批次、十个里程碑：每一批结束都有可用成果，不做“半成品资产”")
add_stage_chart(s, 0.6, 1.5, 12.13, 3.4)
table(s, 0.6, 5.05, 12.13, 1.85,
      ["批次 / 里程碑", "时间", "功能项 / 工程量 / 人力成本", "关键成果与验收标准"],
      [["MVP（M1—M4）", "2026-12 — 2027-04", f"{st['MVP']['count']} 项 / {st['MVP']['effort']} 人天 / {st['MVP']['effort']*1200/10000:.1f} 万",
        "跑通“身份—通行—请假—预警—派单”，20 分钟演示零故障，支撑参赛"],
       ["V1.0（M5—M7）", "2027-04 — 2027-08", f"{st['V1']['count']} 项 / {st['V1']['effort']} 人天 / {st['V1']['effort']*1200/10000:.1f} 万",
        "车辆、归寝、考勤协同、驾驶舱、移动端上线，验收用例通过率 ≥95%"],
       ["V2.0（M8）", "2027-09 — 2028-02", f"{st['V2']['count']} 项 / {st['V2']['effort']} 人天 / {st['V2']['effort']*1200/10000:.1f} 万",
        "一卡通、能耗、设施运维、多校区适配，具备对外交付能力"],
       ["V3.0（M9）", "2028-03 — 2028-10", f"{st['V3']['count']} 项 / {st['V3']['effort']} 人天 / {st['V3']['effort']*1200/10000:.1f} 万",
        "数字孪生、语音助手、开放生态，完成 2 所以上外部学校试点"]],
      col_ratios=[1.25, 1.35, 1.85, 3.3], fs=10, hfs=10.5)
footer(s, 9)

# ============================================================
# S10 预算
# ============================================================
s = slide()
header(s, 8, "投资预算与效益分析", "分阶段小额投放：软件先行、硬件复用，先小后大、见效再扩")
add_budget_chart(s, 0.5, 1.6, 6.15, 3.5)
table(s, 6.8, 1.7, 5.95, 2.9,
      ["投资方案", "建设范围", "合计（含税）"],
      [["方案一 竞赛版", "MVP 核心功能子集 + 最小硬件", "41.6 万元"],
       ["方案二 起步版（推荐）", "MVP 全批次 + MVP 阶段硬件", "111.7 万元"],
       ["方案三 一期建设（推荐）", "MVP + V1.0 + 两阶段硬件", "298.7 万元"],
       ["方案四 完整平台", "MVP + V1 + V2 + 全场景硬件", "434.4 万元"]],
      col_ratios=[1.5, 2.1, 1.2], fs=10, hfs=10.5)
rect(s, 6.8, 4.8, 5.95, 2.05, fill=LBLUE)
text(s, 7.0, 4.92, 5.6, 1.85,
     [[("效益（年度估算）：", 11.5, True, ORANGE)],
      [("▪ 归寝点名：节约约 240 小时/年　▪ 考勤统计：约 120 小时/年", 10.5, False, RGBColor(0x33, 0x38, 0x40))],
      [("▪ 访客登记：3000 人次/年节约约 150 小时", 10.5, False, RGBColor(0x33, 0x38, 0x40))],
      [("▪ 迎检与上报：约 20 人日/年", 10.5, False, RGBColor(0x33, 0x38, 0x40))],
      [("▪ 安全事件响应从“事后追溯”变为“事中处置”", 10.5, False, RGBColor(0x33, 0x38, 0x40))],
      [("▪ 能耗异常实时发现，节能 3%—5%", 10.5, False, RGBColor(0x33, 0x38, 0x40))]], spacing=1.15)
footer(s, 10)

# ============================================================
# S11 合规
# ============================================================
s = slide()
header(s, 9, "安全合规与隐私保护", "技术方案必须先过“合规关”：人脸是敏感个人信息，不能想采就采")
cards(s, [
    ("合规原则", ["最小必要：只采集业务必需的信息", "告知同意：采集前告知用途，未成年人取得监护人同意", "提供替代：必须支持刷卡、二维码等非人脸方式", "可撤回：支持撤回同意与账号注销"]),
    ("技术保护", ["人脸模板加密存储，不出校园网、不上公有云", "传输 TLS 加密，敏感字段脱敏展示", "RBAC + 数据行级权限，最小授权", "导出、查询、删除等操作全部审计留痕"]),
    ("管理保障", ["宿舍房间内不部署任何视频采集设备", "涉学生安全事件仅对有权人员可见", "数据保留有期限，到期自动清理并留痕", "明确安全责任人，制定事件响应流程"]),
], y=1.75, h=3.4)
rect(s, 0.6, 5.4, 12.13, 1.35, fill=LBLUE)
text(s, 0.95, 5.55, 11.5, 1.05,
     [[("我们的态度：", 12.5, True, ORANGE), ("技术能力越强，越要克制。我们把“合规”写进需求规格说明书（M10 模块 + 8.3 节非功能需求），而不是等出了问题再补。", 12, True, NAVY)],
      [("同时按等保 2.0 三级要求进行安全设计与加固，视频与通行数据只服务于学校管理。", 11.5, False, RGBColor(0x33, 0x38, 0x40))]],
     spacing=1.3)
footer(s, 11)

# ============================================================
# S12 团队
# ============================================================
s = slide()
header(s, 10, "团队优势与预期成果", "学校竞赛底蕴 + 真实场景 + 可复制的产品化路径")
text(s, 0.6, 1.5, 6.0, 0.4, [("团队与资源优势", 15, True, NAVY)])
cards(s, [
    ("团队配置（8—9 人）", ["项目负责人 1 人：需求、排期、对外沟通", "AI 算法 2 人：数据集、模型训练与部署", "后端 2 人：业务服务、设备接入、接口", "前端 2 人：管理端、驾驶舱、小程序", "测试实施 1 人：测试、联调、部署培训"]),
    ("学校既有优势", ["计算机类专业为省级特色化专业群", "教师团队具备国家级、省级竞赛指导经验", "已开设人工智能技术与应用、数据技术应用专业", "有移动应用开发、程序设计类赛项办赛与获奖经验"]),
    ("预期成果", ["竞赛：完整参赛材料与可演示系统，力争优异成绩", "落地：本校正式上线，形成可量化的安全与效率成效", "推广：2 所以上同类学校试点并出具成效报告", "沉淀：需求、设计、测试、实施全套标准化文档"]),
], y=1.95, h=4.0)
rect(s, 0.6, 6.1, 12.13, 0.75, fill=NAVY)
text(s, 0.9, 6.2, 11.6, 0.55,
     [[("我们需要学校的支持：", 11.5, True, ORANGE), ("试点区域与设备安装条件 ｜ 学籍/教务/人事数据接口 ｜ 分阶段经费保障 ｜ 业务部门参与验收", 11.5, False, WHITE)]],
     anchor=MSO_ANCHOR.MIDDLE)
footer(s, 12)

# ============================================================
# S13 结束
# ============================================================
s = slide()
rect(s, 0, 0, SW, SH, fill=NAVY)
rect(s, 0, 3.3, SW, 0.07, fill=ORANGE)
text(s, 0.9, 2.0, 11.5, 1.0, [("把校园安全与管理，交给数据", 40, True, WHITE)], align=PP_ALIGN.CENTER)
text(s, 0.9, 3.6, 11.5, 0.6, [("“智园卫士”智慧校园管理平台", 20, True, RGBColor(0x9E, 0xC5, 0xE8))], align=PP_ALIGN.CENTER)
text(s, 0.9, 4.4, 11.5, 0.5, [("感谢聆听，敬请各位专家批评指正", 15, False, RGBColor(0xC8, 0xD6, 0xE5))], align=PP_ALIGN.CENTER)
text(s, 0.9, 6.3, 11.5, 0.5, [("齐河县职业中等专业学校 ｜ 项目组 ｜ 2026 年 11 月", 11.5, False, RGBColor(0x8A, 0x9B, 0xB0))], align=PP_ALIGN.CENTER)

prs.save(OUT)
print("已生成:", OUT, "共", len(prs.slides.__iter__.__self__._sldIdLst), "页")
