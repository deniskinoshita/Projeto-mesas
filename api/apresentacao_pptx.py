"""
Gerador de Apresentação PPTX — Braúna Investimentos
Identidade visual premium, gráficos nativos python-pptx, 16 slides máx.
"""
import io, math, datetime
from pptx import Presentation
from pptx.util import Pt, Cm, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.chart.data import ChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.oxml.ns import qn
from lxml import etree

# ── Paleta ────────────────────────────────────────────────────────────────────
C_BG    = RGBColor(0x07, 0x1E, 0x17)
C_CARD  = RGBColor(0x0A, 0x2A, 0x1E)
C_CARD2 = RGBColor(0x0F, 0x35, 0x25)
C_CARD3 = RGBColor(0x12, 0x3A, 0x28)
C_GOLD  = RGBColor(0xC9, 0xA9, 0x6E)
C_GOLD2 = RGBColor(0xD4, 0xB4, 0x83)
C_GREEN = RGBColor(0x5D, 0xCA, 0xA5)
C_RED   = RGBColor(0xFF, 0x6B, 0x6B)
C_AMBER = RGBColor(0xF0, 0xA8, 0x30)
C_BLUE  = RGBColor(0x7D, 0xCF, 0xEF)
C_PURP  = RGBColor(0xB0, 0x8F, 0xCF)
C_WHITE = RGBColor(0xF0, 0xF0, 0xF0)
C_LGRAY = RGBColor(0x88, 0x88, 0x80)
C_GRAY  = RGBColor(0x2A, 0x5A, 0x40)
C_DGRAY = RGBColor(0x18, 0x3F, 0x2D)

CLS_COR = {
    "pos_fixado":    C_GOLD,
    "inflacao":      C_AMBER,
    "pre_fixado":    RGBColor(0xF0, 0x78, 0x50),
    "acoes":         C_GREEN,
    "fiis":          C_BLUE,
    "multimercado":  C_PURP,
    "alternativos":  RGBColor(0x4E, 0xC9, 0xB0),
    "internacional": RGBColor(0x5B, 0x9B, 0xD5),
    "criptomoedas":  C_LGRAY,
}
CLS_LABEL = {
    "pos_fixado":    "Pós Fixado",
    "inflacao":      "Inflação",
    "pre_fixado":    "Pré Fixado",
    "acoes":         "Ações",
    "fiis":          "FIIs",
    "multimercado":  "Multimercado",
    "alternativos":  "Alternativos",
    "internacional": "Internacional",
    "criptomoedas":  "Criptomoedas",
}
CATS = ["pos_fixado","inflacao","pre_fixado","acoes","fiis","multimercado","alternativos","internacional","criptomoedas"]

SW     = Cm(33.87)
SH     = Cm(19.05)
MARGIN = Cm(0.7)

# ── Primitivas ────────────────────────────────────────────────────────────────
def add_rect(slide, x, y, w, h, fill, border=None, bw=0.4, alpha=None):
    shp = slide.shapes.add_shape(1, x, y, w, h)
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if border:
        shp.line.color.rgb = border
        shp.line.width = Pt(bw)
    else:
        shp.line.fill.background()
    return shp

def add_text(slide, text, x, y, w, h, size=11, bold=False, color=C_WHITE,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txb = slide.shapes.add_textbox(x, y, w, h)
    tf  = txb.text_frame
    tf.word_wrap = wrap
    p   = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = str(text)
    run.font.size  = Pt(size)
    run.font.bold  = bold
    run.font.color.rgb = color
    run.font.italic = italic
    return txb

def bg(slide):
    add_rect(slide, 0, 0, SW, SH, C_BG)

def gold_line(slide, y=None, x=0, w=None, thickness=Cm(0.065)):
    """Thin horizontal gold accent line."""
    if y is None:
        y = 0
    if w is None:
        w = SW
    add_rect(slide, x, y, w, thickness, C_GOLD)

def header(slide, titulo, sub=""):
    gold_line(slide, y=0)
    add_text(slide, "✦  BRAÚNA INVESTIMENTOS", MARGIN, Cm(0.12), Cm(14), Cm(0.6),
             size=7, bold=True, color=C_GOLD)
    add_text(slide, titulo, MARGIN, Cm(0.82), Cm(28), Cm(1.3),
             size=20, bold=True, color=C_WHITE)
    if sub:
        add_text(slide, sub, MARGIN, Cm(2.15), Cm(28), Cm(0.65),
                 size=9.5, color=C_LGRAY)
    gold_line(slide, y=Cm(2.85), thickness=Cm(0.04))

def footer(slide, nome, data):
    add_rect(slide, 0, SH - Cm(0.58), SW, Cm(0.58), C_CARD2)
    gold_line(slide, y=SH - Cm(0.58), thickness=Cm(0.03))
    add_text(slide, f"✦  Braúna Investimentos  ·  {nome}", MARGIN, SH - Cm(0.52),
             Cm(16), Cm(0.45), size=8, color=C_LGRAY)
    add_text(slide, data, SW - Cm(5), SH - Cm(0.52),
             Cm(4.5), Cm(0.45), size=8, color=C_LGRAY, align=PP_ALIGN.RIGHT)

def fmt(v):
    try:
        v = float(v)
        if v >= 1_000_000: return f"R$ {v/1_000_000:.2f}M"
        if v >= 1_000:     return f"R$ {v/1_000:.0f}K"
        return f"R$ {v:.0f}"
    except Exception:
        return "—"

def pct_cor(v):
    try:
        return C_GREEN if float(v) >= 0 else C_RED
    except Exception:
        return C_LGRAY

def add_caixa_texto(slide, texto, y, cor_borda=None, cor_bg=None, tamanho=9.5):
    bg_c = cor_bg or C_CARD
    bord = cor_borda or C_GRAY
    gold_line(slide, y=y, thickness=Cm(0.06))
    box_h = Cm(1.8)
    add_rect(slide, MARGIN, y + Cm(0.06), SW - Cm(1.4), box_h, bg_c, bord, 0.3)
    add_text(slide, texto, MARGIN + Cm(0.4), y + Cm(0.25),
             SW - Cm(2.2), box_h - Cm(0.3), size=tamanho, color=C_WHITE, wrap=True)

def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])

# ── Chart helpers ─────────────────────────────────────────────────────────────
def _rgb_hex(rgb: RGBColor) -> str:
    return f"{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"

def _set_series_color(series, rgb: RGBColor):
    """Set solid fill color on a chart series via XML."""
    try:
        spPr = series.format.fill._element
        # solidFill
        solidFill = etree.SubElement(spPr, qn("a:solidFill"))
        srgbClr   = etree.SubElement(solidFill, qn("a:srgbClr"))
        srgbClr.set("val", _rgb_hex(rgb))
    except Exception:
        pass

def _style_chart_plot_area(chart, bg_rgb: RGBColor = C_BG):
    """Dark background for chart plot area."""
    try:
        plotArea = chart._element.find(qn("c:plotArea"))
        if plotArea is None:
            return
        spPr = plotArea.find(qn("c:spPr"))
        if spPr is None:
            spPr = etree.SubElement(plotArea, qn("c:spPr"))
        solidFill = etree.SubElement(spPr, qn("a:solidFill"))
        srgbClr   = etree.SubElement(solidFill, qn("a:srgbClr"))
        srgbClr.set("val", _rgb_hex(bg_rgb))
        # remove border
        ln = etree.SubElement(spPr, qn("a:ln"))
        etree.SubElement(ln, qn("a:noFill"))
    except Exception:
        pass

def _style_chart_bg(chart, bg_rgb: RGBColor = C_BG):
    """Dark background for whole chart frame."""
    try:
        chartSpace = chart._element
        spPr = chartSpace.find(qn("c:spPr"))
        if spPr is None:
            spPr = etree.SubElement(chartSpace, qn("c:spPr"))
        solidFill = etree.SubElement(spPr, qn("a:solidFill"))
        srgbClr   = etree.SubElement(solidFill, qn("a:srgbClr"))
        srgbClr.set("val", _rgb_hex(bg_rgb))
        ln = etree.SubElement(spPr, qn("a:ln"))
        etree.SubElement(ln, qn("a:noFill"))
    except Exception:
        pass

def _hide_gridlines(chart):
    try:
        for axis_tag in [qn("c:valAx"), qn("c:catAx")]:
            for ax in chart._element.iter(axis_tag):
                mj = ax.find(qn("c:majorGridlines"))
                if mj is not None:
                    ax.remove(mj)
    except Exception:
        pass

def _set_axis_label_color(chart, rgb: RGBColor):
    """Set tick label font color on all axes."""
    try:
        for axis_tag in [qn("c:valAx"), qn("c:catAx")]:
            for ax in chart._element.iter(axis_tag):
                txPr = ax.find(qn("c:txPr"))
                if txPr is None:
                    txPr = etree.SubElement(ax, qn("c:txPr"))
                for r in txPr.iter(qn("a:solidFill")):
                    for s in list(r):
                        r.remove(s)
                    srgbClr = etree.SubElement(r, qn("a:srgbClr"))
                    srgbClr.set("val", _rgb_hex(rgb))
                    return
                # create from scratch
                bodyPr = etree.SubElement(txPr, qn("a:bodyPr"))
                lstStyle = etree.SubElement(txPr, qn("a:lstStyle"))
                p = etree.SubElement(txPr, qn("a:p"))
                pPr = etree.SubElement(p, qn("a:pPr"))
                defRPr = etree.SubElement(pPr, qn("a:defRPr"))
                solidFill = etree.SubElement(defRPr, qn("a:solidFill"))
                srgbClr = etree.SubElement(solidFill, qn("a:srgbClr"))
                srgbClr.set("val", _rgb_hex(rgb))
    except Exception:
        pass

# ── SLIDE 1: CAPA ─────────────────────────────────────────────────────────────
def s_capa(prs, d):
    sl = new_slide(prs)
    bg(sl)
    # Vertical gold stripe
    add_rect(sl, 0, 0, Cm(0.12), SH, C_GOLD)
    add_rect(sl, 0, 0, Cm(1.3), SH, C_CARD)

    add_text(sl, "✦  BRAÚNA INVESTIMENTOS", Cm(1.7), Cm(1.8), Cm(18), Cm(0.8),
             size=10, bold=True, color=C_GOLD)
    gold_line(sl, y=Cm(2.7), x=Cm(1.7), w=Cm(22), thickness=Cm(0.04))
    add_text(sl, "APRESENTAÇÃO\nDE REUNIÃO", Cm(1.7), Cm(3.2), Cm(28), Cm(3.8),
             size=30, bold=True, color=C_WHITE)

    gold_line(sl, y=Cm(7.3), x=Cm(1.7), w=Cm(22), thickness=Cm(0.07))

    nome     = d.get("nome_cliente", "Cliente")
    pat      = d.get("patrimonio", 0)
    data_r   = d.get("data_ref", "")
    perfil_r = str(d.get("perfil", "")).lower()
    perfil   = perfil_r.capitalize()
    assessor = d.get("assessor", "")

    add_text(sl, nome, Cm(1.7), Cm(7.6), Cm(26), Cm(1.6), size=24, color=C_GOLD)
    add_text(sl, f"Patrimônio: {fmt(pat)}   ·   Data: {data_r}", Cm(1.7), Cm(9.5),
             Cm(26), Cm(0.7), size=11, color=C_LGRAY)
    add_text(sl, f"Perfil: {perfil}   ·   Assessor: {assessor}", Cm(1.7), Cm(10.3),
             Cm(26), Cm(0.7), size=10, color=C_LGRAY)

    _PERFIL_COR = {"conservadora": C_BLUE, "moderada": C_GOLD,
                   "arrojada": C_GREEN, "agressiva": C_RED}
    cor_perfil = _PERFIL_COR.get(perfil_r, C_LGRAY)
    add_rect(sl, Cm(1.7), Cm(11.4), Cm(4.5), Cm(0.65), cor_perfil)
    add_text(sl, f"PERFIL  {perfil.upper()}", Cm(1.85), Cm(11.48), Cm(4.2), Cm(0.5),
             size=9, bold=True, color=C_BG)

    objetivo = d.get("objetivo", "")
    if objetivo:
        add_rect(sl, Cm(6.5), Cm(11.4), Cm(10), Cm(0.65), C_CARD2, C_GRAY, 0.3)
        add_text(sl, f"🎯  Objetivo: {objetivo}", Cm(6.75), Cm(11.48), Cm(9.7), Cm(0.5),
                 size=9, color=C_WHITE)

    descr = (f"Esta apresentação consolida a análise completa da carteira de {nome}, "
             f"cobrindo cenário macro, performance, desvios e próximos passos.")
    add_rect(sl, Cm(1.7), Cm(12.3), SW - Cm(2.5), Cm(1.4), C_CARD, C_GRAY, 0.3)
    add_text(sl, descr, Cm(2.0), Cm(12.45), SW - Cm(3.1), Cm(1.1),
             size=10, color=C_LGRAY, wrap=True)

    add_rect(sl, 0, SH - Cm(1.5), SW, Cm(1.5), C_CARD)
    gold_line(sl, y=SH - Cm(1.5), thickness=Cm(0.04))
    add_rect(sl, Cm(1.7), SH - Cm(1.35), Cm(0.04), Cm(1.0), C_GOLD)
    add_text(sl, assessor, Cm(1.95), SH - Cm(1.3), Cm(14), Cm(0.6),
             size=11, bold=True, color=C_GOLD)
    add_text(sl, "Assessor de Investimentos — Braúna Investimentos", Cm(1.95), SH - Cm(0.72),
             Cm(16), Cm(0.5), size=8.5, color=C_LGRAY)
    add_text(sl, "Documento confidencial · Uso exclusivo do cliente",
             SW - Cm(14), SH - Cm(0.72), Cm(13), Cm(0.5), size=7.5, color=C_GRAY, align=PP_ALIGN.RIGHT)

# ── SLIDE 2: AGENDA ───────────────────────────────────────────────────────────
def s_agenda(prs, d, agenda_items):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "AGENDA DA REUNIÃO",
           f"Apresentação — {d.get('nome_cliente','')} · {d.get('data_ref','')}")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    nome   = d.get("nome_cliente", "")
    perfil = str(d.get("perfil", "")).capitalize()
    pat    = fmt(d.get("patrimonio", 0))
    data_r = d.get("data_ref", "")

    add_rect(sl, MARGIN, Cm(2.9), SW - Cm(1.4), Cm(0.06), C_GOLD)
    add_rect(sl, MARGIN, Cm(2.96), SW - Cm(1.4), Cm(0.7), C_CARD2, C_GRAY, 0.3)
    add_text(sl,
             f"Reunião de revisão de carteira  ·  {nome}  ·  Perfil {perfil}  ·  Patrimônio {pat}  ·  Ref. {data_r}",
             MARGIN + Cm(0.4), Cm(3.03), SW - Cm(2.2), Cm(0.56),
             size=10, color=C_GOLD, bold=True)

    _SUBS = {
        "Cenário Global":       "Panorama macro internacional — Fed, BCE, China",
        "Brasil & HP":          "Selic, IPCA, juro real e posicionamento Levante",
        "Patrimônio":           "Evolução do patrimônio e rentabilidade comparativa",
        "Composição":           "Distribuição atual por classe de ativo",
        "Carteira vs. Modelo":  "Aderência ao perfil — classes dentro/fora do modelo",
        "Desvios":              "Classes fora do modelo e recomendação de ajuste",
        "Calls & Oportunidades":"Calls da equipe + operações estruturadas",
        "Renda Variável":       "Ações e FIIs na carteira",
        "Modelo de Servir":     "Score dos 6 pilares de relacionamento",
        "Sugestões":            "Produtos recomendados pelo Head de Produtos",
        "Cross Sell":           "Soluções Braúna ainda não ativadas",
        "Resumo Executivo":     "Síntese dos principais indicadores da reunião",
        "Próximos Passos":      "Encaminhamentos acordados com prazos",
    }

    col_w = (SW - Cm(2)) / 2 - Cm(0.3)
    cx1, cx2 = MARGIN, MARGIN + col_w + Cm(0.6)
    mid = math.ceil(len(agenda_items) / 2)

    for col, (cx, items) in enumerate([(cx1, agenda_items[:mid]), (cx2, agenda_items[mid:])]):
        for i, (num, lbl, sub) in enumerate(items):
            ry = Cm(3.9) + i * Cm(1.88)
            add_rect(sl, cx, ry, col_w, Cm(1.76), C_CARD, C_GRAY, 0.3)
            add_rect(sl, cx, ry, Cm(1.3), Cm(1.76), C_GOLD)
            add_text(sl, str(num), cx, ry + Cm(0.38), Cm(1.3), Cm(0.95),
                     size=14, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
            add_text(sl, lbl, cx + Cm(1.5), ry + Cm(0.15), col_w - Cm(1.7), Cm(0.7),
                     size=12, bold=True, color=C_WHITE)
            sub_det = _SUBS.get(lbl, sub)
            add_text(sl, sub_det, cx + Cm(1.5), ry + Cm(0.9), col_w - Cm(1.7), Cm(0.65),
                     size=8.5, color=C_LGRAY)

# ── SLIDE 3: CENÁRIO GLOBAL ───────────────────────────────────────────────────
def s_cenario_global(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "CENÁRIO GLOBAL", "Panorama macroeconômico internacional — Levante Asset")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    cenario    = d.get("cenario_macro", {})
    global_txt = cenario.get("global", "Informação não disponível.")
    vieses     = cenario.get("vieses", {})
    sinais     = cenario.get("sinais", [])

    VCOR = {"positivo": C_GREEN, "neutro": C_AMBER, "negativo": C_RED}
    VIC  = {"positivo": "▲ Positivo", "neutro": "→ Neutro", "negativo": "▼ Negativo"}

    # Bloco narrativo
    add_rect(sl, MARGIN, Cm(3.0), SW - Cm(1.4), Cm(0.06), C_GOLD)
    add_rect(sl, MARGIN, Cm(3.06), SW - Cm(1.4), Cm(2.7), C_CARD, C_GRAY, 0.3)
    add_text(sl, "🌍  ANÁLISE MACROECONÔMICA GLOBAL", MARGIN + Cm(0.4), Cm(3.22),
             Cm(22), Cm(0.5), size=8, bold=True, color=C_GOLD)
    add_text(sl, global_txt, MARGIN + Cm(0.4), Cm(3.82),
             SW - Cm(2.2), Cm(1.8), size=11, color=C_WHITE, wrap=True)

    # 3 cards regionais
    regioes = [
        ("🇺🇸  Estados Unidos", "Fed mantém postura restritiva. Mercado de trabalho resiliente sustenta consumo.", "cautela"),
        ("🇪🇺  Europa / BCE",   "BCE inicia cortes graduais. Atividade fraca na Alemanha pressiona zona do euro.", "neutro"),
        ("🇨🇳  Ásia / China",   "China retoma crescimento moderado. Estímulos fiscais suportam demanda interna.",   "positivo"),
    ]
    VCOR2 = {"positivo": C_GREEN, "cautela": C_AMBER, "neutro": C_LGRAY}
    VIC2  = {"positivo": "▲ Positivo", "cautela": "→ Cautela", "neutro": "→ Neutro"}
    rw = (SW - Cm(1.4)) / 3 - Cm(0.2)
    for i, (reg, desc, sent) in enumerate(regioes):
        rx  = MARGIN + i * (rw + Cm(0.2))
        cor = VCOR2.get(sent, C_LGRAY)
        add_rect(sl, rx, Cm(6.0), rw, Cm(2.1), C_CARD2, cor, 0.4)
        add_rect(sl, rx, Cm(6.0), rw, Cm(0.15), cor)
        add_text(sl, reg, rx + Cm(0.3), Cm(6.22), rw - Cm(0.6), Cm(0.55),
                 size=10, bold=True, color=C_WHITE)
        add_text(sl, VIC2.get(sent, "→"), rx + Cm(0.3), Cm(6.82), rw - Cm(0.6), Cm(0.45),
                 size=9, bold=True, color=cor)
        add_text(sl, desc, rx + Cm(0.3), Cm(7.32), rw - Cm(0.6), Cm(0.65),
                 size=8.5, color=C_LGRAY, wrap=True)

    # Sinais de mercado
    if sinais:
        add_text(sl, "📡  SINAIS DE MERCADO", MARGIN, Cm(8.3), SW, Cm(0.5),
                 size=8, bold=True, color=C_LGRAY)
        bx = MARGIN; by = Cm(8.9)
        for sinal in sinais[:8]:
            lbl = str(sinal).strip()
            sw_badge = Cm(len(lbl) * 0.22 + 0.8)
            add_rect(sl, bx, by, sw_badge, Cm(0.55), C_CARD2, C_GRAY, 0.3)
            add_text(sl, lbl, bx + Cm(0.25), by + Cm(0.07),
                     sw_badge - Cm(0.4), Cm(0.42), size=8, color=C_LGRAY)
            bx += sw_badge + Cm(0.2)
            if bx > SW - Cm(3):
                bx = MARGIN; by += Cm(0.7)
        vieses_y = by + Cm(0.8)
    else:
        vieses_y = Cm(8.9)

    # ── Heatmap de vieses ────────────────────────────────────────────────────
    add_text(sl, "🌡  VIESES POR CLASSE DE ATIVO — POSICIONAMENTO HP", MARGIN,
             vieses_y - Cm(0.55), SW - Cm(1.4), Cm(0.5), size=8, bold=True, color=C_GOLD)

    items   = list(vieses.items())
    n       = max(len(items), 1)
    vw      = (SW - Cm(1.4)) / n - Cm(0.18)
    vcard_h = SH - vieses_y - Cm(0.75)
    VBG     = {"positivo": RGBColor(0x0A, 0x35, 0x22),
               "neutro":   RGBColor(0x2A, 0x22, 0x08),
               "negativo": RGBColor(0x35, 0x0A, 0x0A)}

    for i, (cls, v) in enumerate(items):
        vx  = MARGIN + i * (vw + Cm(0.18))
        cor = VCOR.get(v, C_LGRAY)
        bg_v = VBG.get(v, C_CARD)
        add_rect(sl, vx, vieses_y, vw, vcard_h, bg_v, cor, 0.5)
        add_rect(sl, vx, vieses_y, vw, Cm(0.18), cor)
        add_text(sl, CLS_LABEL.get(cls, cls), vx + Cm(0.2),
                 vieses_y + Cm(0.32), vw - Cm(0.4), Cm(0.65),
                 size=9, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        add_text(sl, VIC.get(v, "→"), vx + Cm(0.2), vieses_y + Cm(1.05),
                 vw - Cm(0.4), Cm(0.6), size=9, bold=True, color=cor,
                 align=PP_ALIGN.CENTER)

# ── SLIDE 4: CENÁRIO BRASIL & HP ─────────────────────────────────────────────
def s_cenario_brasil(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "BRASIL & POSICIONAMENTO", "Visão Head de Produtos — Levante Asset")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    cenario    = d.get("cenario_macro", {})
    selic      = cenario.get("selic_meta")
    ipca       = cenario.get("ipca_12m")
    brasil_txt = cenario.get("brasil", "")
    pos_txt    = cenario.get("posicionamento", "")
    vieses     = cenario.get("vieses", {})
    VCOR       = {"positivo": C_GREEN, "neutro": C_AMBER, "negativo": C_RED}
    VIC        = {"positivo": "▲", "neutro": "→", "negativo": "▼"}

    juro_real = round(float(selic) - float(ipca), 2) if selic and ipca else None

    metricas_br = [
        ("📊  SELIC META",  f"{float(selic):.2f}%"     if selic     else "—", C_GOLD),
        ("📈  IPCA 12M",    f"{float(ipca):.2f}%"      if ipca      else "—",
         C_AMBER if ipca and float(ipca) > 5 else C_GREEN),
        ("⚖️  JURO REAL",   f"{juro_real:.2f}%"        if juro_real else "—",
         C_GREEN if juro_real and juro_real > 6 else C_AMBER),
        ("📉  SPREAD REAL", f"+{max(0,(juro_real or 0)-6):.2f}%p acima NTN-B" if juro_real else "—", C_LGRAY),
    ]
    mw = (SW - Cm(1.4)) / 4 - Cm(0.25)
    for i, (lbl, val, cor) in enumerate(metricas_br):
        mx = MARGIN + i * (mw + Cm(0.25))
        add_rect(sl, mx, Cm(3.0), mw, Cm(2.0), C_CARD, cor, 0.5)
        add_rect(sl, mx, Cm(3.0), mw, Cm(0.15), cor)
        add_text(sl, lbl, mx + Cm(0.3), Cm(3.22), mw - Cm(0.6), Cm(0.5), size=8, color=C_LGRAY)
        add_text(sl, val, mx + Cm(0.3), Cm(3.8),  mw - Cm(0.6), Cm(0.95), size=16, bold=True, color=cor)

    col_w = (SW - Cm(2)) / 2 - Cm(0.3)
    cx1, cx2 = MARGIN, MARGIN + col_w + Cm(0.6)
    y0 = Cm(5.3)

    # Coluna esquerda: CENÁRIO BRASIL
    add_rect(sl, cx1, y0, col_w, Cm(0.6), C_DGRAY, C_GRAY, 0.3)
    add_rect(sl, cx1, y0, Cm(0.18), Cm(0.6), C_LGRAY)
    add_text(sl, "🇧🇷  CENÁRIO BRASIL", cx1 + Cm(0.4), y0 + Cm(0.1),
             col_w - Cm(0.6), Cm(0.45), size=10, bold=True, color=C_WHITE)
    add_rect(sl, cx1, y0 + Cm(0.6), col_w, Cm(5.5), C_CARD, C_GRAY, 0.3)
    add_text(sl, brasil_txt,
             cx1 + Cm(0.4), y0 + Cm(0.85), col_w - Cm(0.8), Cm(3.5),
             size=11, color=C_WHITE, wrap=True)
    add_rect(sl, cx1 + Cm(0.3), y0 + Cm(4.55), col_w - Cm(0.6), Cm(0.04), C_GRAY)
    add_text(sl, "INDICADORES CHAVE", cx1 + Cm(0.3), y0 + Cm(4.65),
             col_w - Cm(0.6), Cm(0.4), size=7.5, bold=True, color=C_LGRAY)
    kpis = []
    if selic:     kpis.append(f"Selic: {float(selic):.2f}%")
    if ipca:      kpis.append(f"IPCA 12M: {float(ipca):.2f}%")
    if juro_real: kpis.append(f"Juro real: {juro_real:.2f}%")
    kpis += ["Risco fiscal: elevado", "Câmbio: volatilidade moderada"]
    for j, kpi in enumerate(kpis[:4]):
        kx = cx1 + Cm(0.3) + (j % 2) * ((col_w - Cm(0.6)) / 2)
        ky = y0 + Cm(5.15) + (j // 2) * Cm(0.55)
        add_rect(sl, kx, ky, (col_w - Cm(0.8)) / 2, Cm(0.48), C_CARD2, C_GRAY, 0.3)
        add_text(sl, kpi, kx + Cm(0.2), ky + Cm(0.06),
                 (col_w - Cm(0.8)) / 2 - Cm(0.3), Cm(0.38), size=8.5, color=C_LGRAY)

    # Coluna direita: POSICIONAMENTO HP
    add_rect(sl, cx2, y0, col_w, Cm(0.6), C_CARD2, C_GOLD, 0.4)
    add_rect(sl, cx2, y0, col_w, Cm(0.15), C_GOLD)
    add_text(sl, "★  POSICIONAMENTO HEAD DE PRODUTOS", cx2 + Cm(0.3), y0 + Cm(0.12),
             col_w - Cm(0.5), Cm(0.45), size=10, bold=True, color=C_GOLD)
    add_rect(sl, cx2, y0 + Cm(0.6), col_w, Cm(3.0), C_CARD2, C_GOLD, 0.3)
    add_text(sl, pos_txt,
             cx2 + Cm(0.4), y0 + Cm(0.85), col_w - Cm(0.8), Cm(2.65),
             size=11, color=C_WHITE, wrap=True)

    add_rect(sl, cx2, y0 + Cm(3.6), col_w, Cm(0.5), C_DGRAY, C_GOLD, 0.3)
    add_text(sl, "VIÉS POR CLASSE DE ATIVO", cx2 + Cm(0.3), y0 + Cm(3.68),
             col_w - Cm(0.5), Cm(0.38), size=8, bold=True, color=C_GOLD)

    items_v = [(c, v) for c, v in vieses.items() if c in CATS]
    if items_v:
        row_h_v = Cm(0.72)
        for j, (cls, v) in enumerate(items_v):
            ry  = y0 + Cm(4.15) + j * row_h_v
            cor = VCOR.get(v, C_LGRAY)
            add_rect(sl, cx2, ry, col_w, row_h_v - Cm(0.05), C_CARD if j % 2 == 0 else C_CARD3)
            add_rect(sl, cx2, ry, Cm(0.2), row_h_v - Cm(0.05), cor)
            add_text(sl, CLS_LABEL.get(cls, cls), cx2 + Cm(0.4), ry + Cm(0.1),
                     col_w - Cm(2.2), Cm(0.52), size=10, color=C_WHITE)
            add_text(sl, f"{VIC.get(v,'→')} {v.capitalize()}",
                     cx2 + col_w - Cm(2.0), ry + Cm(0.1), Cm(1.8), Cm(0.52),
                     size=10, bold=True, color=cor, align=PP_ALIGN.RIGHT)

    vieses_pos = [CLS_LABEL.get(c, c) for c, v in vieses.items() if v == "positivo"]
    vieses_neg = [CLS_LABEL.get(c, c) for c, v in vieses.items() if v == "negativo"]
    partes = []
    if vieses_pos: partes.append(f"Favorecidas: {', '.join(vieses_pos)}")
    if vieses_neg: partes.append(f"Cautela: {', '.join(vieses_neg)}")
    if juro_real:
        if juro_real > 7:
            partes.append(f"Juro real de {juro_real:.1f}% sustenta renda fixa")
        elif juro_real < 5:
            partes.append("Juro real baixo favorece ativos de risco")
    if partes:
        impl = "Implicação para a carteira: " + " · ".join(partes) + "."
        add_caixa_texto(sl, impl, SH - Cm(2.8), cor_borda=C_GOLD, cor_bg=C_CARD2)

# ── SLIDE 5: PATRIMÔNIO & RENTABILIDADE (com gráfico de barras nativo) ────────
def s_patrimonio(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "PATRIMÔNIO & RENTABILIDADE", "Evolução e desempenho da carteira")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    pat  = d.get("patrimonio", 0)
    rent = d.get("rent", {})
    pr   = rent.get("portfolio", {}) if isinstance(rent, dict) else {}
    cr   = rent.get("cdi", {})       if isinstance(rent, dict) else {}

    # Cards de métricas
    metricas = [
        ("💰  PATRIMÔNIO TOTAL",  fmt(pat),                   C_GOLD),
        ("📅  RENTAB. MÊS",      f"{pr.get('1m',pr.get('mes',0)):.2f}%",  pct_cor(pr.get('1m',pr.get('mes',0)))),
        ("📆  RENTAB. ANO",      f"{pr.get('ano',0):.2f}%",  pct_cor(pr.get('ano',0))),
        ("📊  RENTAB. 12M",      f"{pr.get('12m',0):.2f}%",  pct_cor(pr.get('12m',0))),
    ]
    mw = (SW - Cm(1.4)) / 4 - Cm(0.25)
    for i, (lbl, val, cor) in enumerate(metricas):
        mx = MARGIN + i * (mw + Cm(0.25))
        add_rect(sl, mx, Cm(3.1), mw, Cm(2.0), C_CARD, cor, 0.5)
        add_rect(sl, mx, Cm(3.1), mw, Cm(0.12), cor)
        add_text(sl, lbl, mx + Cm(0.3), Cm(3.35), mw - Cm(0.6), Cm(0.55), size=7.5, color=C_LGRAY)
        add_text(sl, val,  mx + Cm(0.3), Cm(3.95), mw - Cm(0.6), Cm(0.9),  size=17, bold=True, color=cor)

    # ── Bar chart: Carteira vs CDI ───────────────────────────────────────────
    _p1m  = pr.get("1m",  pr.get("mes",  0.0))
    _p3m  = pr.get("3m",  0.0)
    _p6m  = pr.get("6m",  0.0)
    _p12m = pr.get("12m", 0.0)
    _c1m  = cr.get("1m",  cr.get("mes",  0.0))
    _c3m  = cr.get("3m",  0.0)
    _c6m  = cr.get("6m",  0.0)
    _c12m = cr.get("12m", 0.0)

    chart_data = ChartData()
    chart_data.categories = ["1M", "3M", "6M", "12M"]
    chart_data.add_series("Carteira", (_p1m, _p3m, _p6m, _p12m))
    chart_data.add_series("CDI",      (_c1m, _c3m, _c6m, _c12m))

    cx = MARGIN
    cy = Cm(5.3)
    cw = SW - Cm(1.4)
    ch = Cm(7.2)
    chart_frame = sl.shapes.add_chart(
        XL_CHART_TYPE.COLUMN_CLUSTERED, cx, cy, cw, ch, chart_data)
    chart = chart_frame.chart
    chart.has_legend = True
    chart.has_title  = False

    _style_chart_bg(chart, C_BG)
    _style_chart_plot_area(chart, C_CARD)
    _hide_gridlines(chart)

    # Color series
    try:
        chart.series[0].format.fill.solid()
        chart.series[0].format.fill.fore_color.rgb = C_GREEN
        chart.series[1].format.fill.solid()
        chart.series[1].format.fill.fore_color.rgb = C_GOLD
    except Exception:
        pass

    # Legend color
    try:
        legend = chart.legend
        legend.position = 3  # bottom
        legend.include_in_layout = False
    except Exception:
        pass

    _set_axis_label_color(chart, C_LGRAY)

    # Linha separadora
    add_rect(sl, MARGIN, Cm(12.65), SW - Cm(1.4), Cm(0.04), C_GRAY)

    # % CDI badges
    pairs = [("1M", _p1m, _c1m), ("3M", _p3m, _c3m), ("6M", _p6m, _c6m), ("12M", _p12m, _c12m)]
    bw2 = (SW - Cm(1.4)) / 4 - Cm(0.25)
    for i, (lbl, pv, cv) in enumerate(pairs):
        bx2 = MARGIN + i * (bw2 + Cm(0.25))
        pct = round(pv / cv * 100, 0) if cv else 0
        cor = C_GREEN if pct >= 100 else (C_AMBER if pct >= 80 else C_RED)
        add_rect(sl, bx2, Cm(12.75), bw2, Cm(1.3), C_CARD, cor, 0.4)
        add_text(sl, f"{lbl}  {pct:.0f}% CDI", bx2 + Cm(0.3), Cm(12.85),
                 bw2 - Cm(0.5), Cm(0.55), size=9, bold=True, color=cor)
        add_text(sl, f"Carteira {pv:.2f}%  ·  CDI {cv:.2f}%",
                 bx2 + Cm(0.3), Cm(13.45), bw2 - Cm(0.5), Cm(0.45), size=8, color=C_LGRAY)

    # Narrativa
    c12 = _c12m or 1
    pct_12 = round(_p12m / c12 * 100, 0)
    q_cdi  = ("expressivamente acima" if pct_12 >= 110
               else ("acima" if pct_12 >= 90
               else ("próximo" if pct_12 >= 75 else "abaixo")))
    nome = d.get("nome_cliente", "O cliente")
    narrativa = (
        f"{nome} encerrou o período com patrimônio de {fmt(pat)}, rentabilidade de "
        f"{_p12m:.2f}% em 12 meses — equivalente a {pct_12:.0f}% do CDI, desempenho {q_cdi} do referencial. "
        f"{'Bom alinhamento com a estratégia definida.' if pct_12 >= 80 else 'Resultado merece atenção e revisão da estratégia.'}"
    ) if pat else "Sem dados de rentabilidade disponíveis."
    add_caixa_texto(sl, narrativa, Cm(14.2),
                    cor_borda=C_GREEN if pct_12 >= 80 else C_AMBER,
                    cor_bg=C_CARD2)

# ── SLIDE 6: COMPOSIÇÃO (com Donut chart nativo) ──────────────────────────────
def s_composicao(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "COMPOSIÇÃO DA CARTEIRA", "Alocação atual por classe de ativo")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    comp = d.get("composicao", {})
    pat  = d.get("patrimonio", 0)

    cats_com_valor = [(c, comp.get(c, 0)) for c in CATS if comp.get(c, 0) > 0]
    if not cats_com_valor:
        add_text(sl, "Sem dados de composição disponíveis.", MARGIN, Cm(5), SW - Cm(1.4), Cm(1.5),
                 size=14, color=C_LGRAY, align=PP_ALIGN.CENTER)
        return

    # Donut chart (esquerda)
    chart_data = ChartData()
    chart_data.categories = [CLS_LABEL.get(c, c) for c, _ in cats_com_valor]
    chart_data.add_series("Alocação", tuple(v for _, v in cats_com_valor))

    chart_frame = sl.shapes.add_chart(
        XL_CHART_TYPE.DOUGHNUT,
        MARGIN, Cm(3.1), Cm(14.5), Cm(12.5), chart_data)
    chart = chart_frame.chart
    chart.has_legend  = False
    chart.has_title   = False

    _style_chart_bg(chart, C_BG)
    _style_chart_plot_area(chart, C_BG)

    # Color each point
    try:
        series = chart.series[0]
        for i, (cat, _) in enumerate(cats_com_valor):
            pt = series.points[i]
            pt.format.fill.solid()
            pt.format.fill.fore_color.rgb = CLS_COR.get(cat, C_LGRAY)
    except Exception:
        pass

    # Tabela à direita
    table_x = Cm(15.5)
    table_w = SW - Cm(16.2)
    top_y   = Cm(3.1)

    # Cabeçalhos
    add_text(sl, "CLASSE",        table_x,           top_y, Cm(5),   Cm(0.5), size=8, bold=True, color=C_LGRAY)
    add_text(sl, "% CART.",       table_x + Cm(5.2), top_y, Cm(2.2), Cm(0.5), size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.RIGHT)
    add_text(sl, "R$ ALOCADO",    table_x + Cm(7.6), top_y, Cm(4.0), Cm(0.5), size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.RIGHT)

    row_h = Cm(0.92)
    for i, (cat, v) in enumerate(cats_com_valor):
        ry   = top_y + Cm(0.65) + i * row_h
        fundo = C_CARD if i % 2 == 0 else C_CARD3
        cor  = CLS_COR.get(cat, C_LGRAY)
        add_rect(sl, table_x, ry, table_w, row_h - Cm(0.05), fundo)
        add_rect(sl, table_x, ry, Cm(0.18), row_h - Cm(0.05), cor)
        add_text(sl, CLS_LABEL.get(cat, cat), table_x + Cm(0.35), ry + Cm(0.2),
                 Cm(4.8), Cm(0.6), size=10.5, color=C_WHITE)
        add_text(sl, f"{v:.1f}%", table_x + Cm(5.2), ry + Cm(0.2),
                 Cm(2.2), Cm(0.6), size=10.5, bold=True, color=cor, align=PP_ALIGN.RIGHT)
        val_r = fmt(pat * v / 100) if pat else "—"
        add_text(sl, val_r, table_x + Cm(7.6), ry + Cm(0.2),
                 Cm(4.0), Cm(0.6), size=10, color=C_LGRAY, align=PP_ALIGN.RIGHT)

    # Narrativa
    n_classes = len(cats_com_valor)
    principal_cat, principal_v = cats_com_valor[0]
    div = ("bem diversificada" if n_classes >= 5
           else ("moderadamente diversificada" if n_classes >= 3 else "concentrada"))
    narr = (f"A carteira está {div}, em {n_classes} classes. "
            f"Maior exposição: {CLS_LABEL.get(principal_cat,principal_cat)} ({principal_v:.1f}%"
            f"{f', {fmt(pat*principal_v/100)}' if pat else ''}).")
    add_caixa_texto(sl, narr, SH - Cm(2.5), cor_borda=C_GOLD, cor_bg=C_CARD2)

# ── SLIDE 7: CARTEIRA vs MODELO (com Horizontal Bar chart nativo) ─────────────
def s_vs_modelo(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "CARTEIRA vs. MODELO", "Comparativo entre alocação atual e perfil de investidor")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    comp   = d.get("composicao", {})
    modelo = d.get("modelo_hp", {})

    cats_visiveis = [c for c in CATS if comp.get(c, 0) > 0 or modelo.get(c, 0) > 0]

    # Horizontal bar chart (esquerda)
    if cats_visiveis:
        chart_data = ChartData()
        chart_data.categories = [CLS_LABEL.get(c, c) for c in cats_visiveis]
        chart_data.add_series("Atual",  tuple(comp.get(c, 0) for c in cats_visiveis))
        chart_data.add_series("Modelo", tuple(modelo.get(c, 0) for c in cats_visiveis))

        chart_frame = sl.shapes.add_chart(
            XL_CHART_TYPE.BAR_CLUSTERED,
            MARGIN, Cm(3.1), Cm(18.5), Cm(12.5), chart_data)
        chart = chart_frame.chart
        chart.has_legend  = True
        chart.has_title   = False

        _style_chart_bg(chart, C_BG)
        _style_chart_plot_area(chart, C_CARD)
        _hide_gridlines(chart)

        try:
            chart.series[0].format.fill.solid()
            chart.series[0].format.fill.fore_color.rgb = C_GREEN
            chart.series[1].format.fill.solid()
            chart.series[1].format.fill.fore_color.rgb = C_GOLD
        except Exception:
            pass

        _set_axis_label_color(chart, C_LGRAY)

    # Tabela resumida à direita
    tx = Cm(19.5)
    tw = SW - Cm(20.2)
    top_y = Cm(3.1)

    hdrs = ["CLASSE", "ATUAL", "MODELO", "STATUS"]
    ws   = [Cm(4.0), Cm(1.8), Cm(1.8), Cm(2.0)]
    xs   = [tx]
    for w in ws[:-1]:
        xs.append(xs[-1] + w)

    for i, h in enumerate(hdrs):
        add_text(sl, h, xs[i], top_y, ws[i], Cm(0.5),
                 size=8, bold=True, color=C_LGRAY,
                 align=PP_ALIGN.LEFT if i == 0 else PP_ALIGN.CENTER)

    row_h = Cm(0.88)
    for i, cat in enumerate(cats_visiveis):
        atual = comp.get(cat, 0)
        mod   = modelo.get(cat, 0)
        dev   = round(atual - mod, 1)
        ry    = top_y + Cm(0.65) + i * row_h
        cor   = CLS_COR.get(cat, C_LGRAY)
        add_rect(sl, tx, ry, tw, row_h - Cm(0.05), C_CARD if i % 2 == 0 else C_CARD3)
        add_rect(sl, tx, ry, Cm(0.18), row_h - Cm(0.05), cor)
        add_text(sl, CLS_LABEL.get(cat, cat), xs[0] + Cm(0.3), ry + Cm(0.18),
                 ws[0] - Cm(0.4), Cm(0.55), size=9.5, color=C_WHITE)
        add_text(sl, f"{atual:.1f}%", xs[1], ry + Cm(0.18),
                 ws[1], Cm(0.55), size=9.5, color=C_WHITE, align=PP_ALIGN.CENTER)
        add_text(sl, f"{mod:.1f}%", xs[2], ry + Cm(0.18),
                 ws[2], Cm(0.55), size=9.5, color=C_GOLD, align=PP_ALIGN.CENTER)
        sit     = "✓" if abs(dev) <= 3 else ("▼" if dev < 0 else "▲")
        cor_sit = C_GREEN if abs(dev) <= 3 else (C_RED if abs(dev) > 5 else C_AMBER)
        add_text(sl, sit, xs[3], ry + Cm(0.18),
                 ws[3], Cm(0.55), size=10, bold=abs(dev) > 3, color=cor_sit,
                 align=PP_ALIGN.CENTER)

    n_ok     = sum(1 for c in cats_visiveis if abs(comp.get(c,0) - modelo.get(c,0)) <= 3)
    n_fora   = len(cats_visiveis) - n_ok
    narr_vs  = (f"De {len(cats_visiveis)} classes, {n_ok} estão dentro do modelo e {n_fora} "
                f"{'está' if n_fora == 1 else 'estão'} fora. "
                f"{'Carteira bem alinhada ao perfil.' if n_fora == 0 else 'Ajustes recomendados para classes fora do modelo.'}")
    add_caixa_texto(sl, narr_vs, SH - Cm(2.5),
                    cor_borda=C_AMBER if n_fora > 0 else C_GREEN, cor_bg=C_CARD2)

# ── SLIDE 8: DESVIOS ─────────────────────────────────────────────────────────
def s_desvios(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "DESVIOS DA CARTEIRA", "O que precisa ser ajustado para atingir o modelo")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    desvios = d.get("desvios", [])
    pat     = d.get("patrimonio", 0)

    exc  = [x for x in desvios if x.get("desvio_pp", x.get("desvio", 0)) > 0]
    def_ = [x for x in desvios if x.get("desvio_pp", x.get("desvio", 0)) < 0]

    if not desvios:
        add_rect(sl, MARGIN, Cm(4.0), SW - Cm(1.4), Cm(4.0), C_CARD, C_GREEN, 0.5)
        add_text(sl, "✅  Carteira dentro do modelo", MARGIN + Cm(1), Cm(5.5),
                 SW - Cm(3), Cm(1.5), size=18, bold=True, color=C_GREEN, align=PP_ALIGN.CENTER)
        add_text(sl, "Nenhum desvio significativo identificado. Carteira alinhada ao perfil.",
                 MARGIN + Cm(1), Cm(7.0), SW - Cm(3), Cm(0.8),
                 size=11, color=C_LGRAY, align=PP_ALIGN.CENTER)
        return

    col_w = (SW - Cm(2)) / 2 - Cm(0.3)
    cx1, cx2 = MARGIN, MARGIN + col_w + Cm(0.6)
    row_h = Cm(1.55)

    add_text(sl, "🔽  REDUZIR / RESGATAR", cx1, Cm(3.1), col_w, Cm(0.55),
             size=9, bold=True, color=C_RED)
    add_text(sl, "🔼  AUMENTAR / APORTAR", cx2, Cm(3.1), col_w, Cm(0.55),
             size=9, bold=True, color=C_GREEN)

    for col, items, cor in [(cx1, exc, C_RED), (cx2, def_, C_GREEN)]:
        for i, dev in enumerate(items[:7]):
            ry    = Cm(3.75) + i * row_h
            cat   = dev.get("classe", dev.get("cls",""))
            desp  = abs(dev.get("desvio_pp", dev.get("desvio", 0)))
            atual = dev.get("atual", 0)
            mod   = dev.get("modelo", dev.get("alvo", 0))
            val   = pat * desp / 100 if pat else 0
            add_rect(sl, col, ry, col_w, row_h - Cm(0.1), C_CARD, cor, 0.3)
            add_rect(sl, col, ry, Cm(0.18), row_h - Cm(0.1), cor)
            add_text(sl, CLS_LABEL.get(cat, cat), col + Cm(0.4), ry + Cm(0.12),
                     col_w - Cm(2.8), Cm(0.65), size=11, bold=True, color=C_WHITE)
            add_text(sl, f"{desp:.1f}%", col + col_w - Cm(1.6), ry + Cm(0.12),
                     Cm(1.4), Cm(0.65), size=11, bold=True, color=cor, align=PP_ALIGN.RIGHT)
            add_text(sl, f"Atual {atual:.1f}%  →  Modelo {mod:.1f}%  ·  {fmt(val) if val else '—'}",
                     col + Cm(0.4), ry + Cm(0.85), col_w - Cm(0.6), Cm(0.5),
                     size=8.5, color=C_LGRAY)

    if exc or def_:
        maior_exc = (f"{CLS_LABEL.get(exc[0].get('classe', exc[0].get('cls','')), '')} "
                     f"(+{abs(exc[0].get('desvio_pp', exc[0].get('desvio',0))):.1f}%)") if exc else None
        maior_def = (f"{CLS_LABEL.get(def_[0].get('classe', def_[0].get('cls','')), '')} "
                     f"(-{abs(def_[0].get('desvio_pp', def_[0].get('desvio',0))):.1f}%)") if def_ else None
        partes = []
        if maior_exc: partes.append(f"Maior excesso: {maior_exc} — resgatar parcialmente")
        if maior_def: partes.append(f"Maior sub-alocação: {maior_def} — aportar")
        n_total = len(exc) + len(def_)
        narr = ". ".join(partes) + f". Total: {n_total} ajuste{'s' if n_total > 1 else ''} necessário{'s' if n_total > 1 else ''}."
        add_caixa_texto(sl, narr, SH - Cm(2.7), cor_borda=C_AMBER, cor_bg=C_CARD2)

# ── SLIDE 9: CALLS & OPORTUNIDADES (novo) ────────────────────────────────────
def s_calls(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "CALLS & OPORTUNIDADES", "Recomendações da equipe + operações estruturadas")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    calls       = d.get("calls", [])
    estruturadas = d.get("estruturadas", [])

    # ── Calls (esquerda) ──────────────────────────────────────────────────────
    col_w = (SW - Cm(2)) / 2 - Cm(0.3)
    cx1, cx2 = MARGIN, MARGIN + col_w + Cm(0.6)

    add_rect(sl, cx1, Cm(3.1), col_w, Cm(0.55), C_CARD2, C_GREEN, 0.4)
    add_rect(sl, cx1, Cm(3.1), col_w, Cm(0.12), C_GREEN)
    add_text(sl, "📈  CALLS DA EQUIPE", cx1 + Cm(0.3), Cm(3.2), col_w - Cm(0.5), Cm(0.4),
             size=9.5, bold=True, color=C_GREEN)

    TIPO_COR  = {"buy": C_GREEN, "sell": C_RED, "hold": C_AMBER, "neutro": C_LGRAY}
    TIPO_ICON = {"buy": "▲  COMPRAR", "sell": "▼  VENDER", "hold": "→  MANTER", "neutro": "—"}

    if calls:
        row_h = Cm(1.55)
        for i, c in enumerate(calls[:6]):
            ry   = Cm(3.75) + i * row_h
            tipo = str(c.get("tipo", "")).lower()
            cor  = TIPO_COR.get(tipo, C_LGRAY)
            add_rect(sl, cx1, ry, col_w, row_h - Cm(0.1), C_CARD, cor, 0.4)
            add_rect(sl, cx1, ry, Cm(0.18), row_h - Cm(0.1), cor)
            add_text(sl, c.get("ativo", "—"), cx1 + Cm(0.4), ry + Cm(0.12),
                     col_w - Cm(3.5), Cm(0.65), size=12, bold=True, color=C_WHITE)
            add_text(sl, TIPO_ICON.get(tipo, tipo.upper()),
                     cx1 + col_w - Cm(3.2), ry + Cm(0.12), Cm(3.0), Cm(0.65),
                     size=9, bold=True, color=cor, align=PP_ALIGN.RIGHT)
            data_c = c.get("data", "")
            add_text(sl, data_c, cx1 + Cm(0.4), ry + Cm(0.85),
                     col_w - Cm(0.6), Cm(0.45), size=8, color=C_LGRAY)
    else:
        add_rect(sl, cx1, Cm(3.75), col_w, Cm(3.0), C_CARD, C_GRAY, 0.3)
        add_text(sl, "Sem calls publicados no momento", cx1 + Cm(0.4), Cm(5.0),
                 col_w - Cm(0.8), Cm(0.7), size=10, color=C_LGRAY, align=PP_ALIGN.CENTER)

    # ── Estruturadas (direita) ────────────────────────────────────────────────
    add_rect(sl, cx2, Cm(3.1), col_w, Cm(0.55), C_CARD2, C_PURP, 0.4)
    add_rect(sl, cx2, Cm(3.1), col_w, Cm(0.12), C_PURP)
    add_text(sl, "🏗️  OPERAÇÕES ESTRUTURADAS", cx2 + Cm(0.3), Cm(3.2),
             col_w - Cm(0.5), Cm(0.4), size=9.5, bold=True, color=C_PURP)

    TIPO_ESTR_COR = {
        "coe":   C_PURP,
        "cri":   C_BLUE,
        "cra":   C_GREEN,
        "debenture": C_AMBER,
        "fundo": C_GOLD,
    }

    if estruturadas:
        row_h = Cm(2.0)
        for i, e in enumerate(estruturadas[:5]):
            ry    = Cm(3.75) + i * row_h
            tipo  = str(e.get("tipo", "")).lower()
            cor   = TIPO_ESTR_COR.get(tipo, C_PURP)
            add_rect(sl, cx2, ry, col_w, row_h - Cm(0.1), C_CARD, cor, 0.4)
            add_rect(sl, cx2, ry, Cm(0.18), row_h - Cm(0.1), cor)
            add_text(sl, e.get("ativo", "—"), cx2 + Cm(0.4), ry + Cm(0.1),
                     col_w - Cm(3.5), Cm(0.65), size=12, bold=True, color=C_WHITE)
            add_text(sl, str(e.get("tipo", "")).upper(),
                     cx2 + col_w - Cm(2.2), ry + Cm(0.1), Cm(2.0), Cm(0.65),
                     size=9, bold=True, color=cor, align=PP_ALIGN.RIGHT)
            ret   = e.get("retorno", "")
            venc  = e.get("vencimento", "")
            perfm = e.get("perfil_minimo", "")
            add_text(sl, f"Retorno: {ret}", cx2 + Cm(0.4), ry + Cm(0.8),
                     col_w - Cm(0.6), Cm(0.45), size=9.5, color=C_GREEN)
            add_text(sl, f"Vencimento: {venc}  ·  Perfil mín.: {perfm.capitalize()}",
                     cx2 + Cm(0.4), ry + Cm(1.3), col_w - Cm(0.6), Cm(0.45),
                     size=8, color=C_LGRAY)
    else:
        add_rect(sl, cx2, Cm(3.75), col_w, Cm(3.0), C_CARD, C_GRAY, 0.3)
        add_text(sl, "Sem operações estruturadas ativas", cx2 + Cm(0.4), Cm(5.0),
                 col_w - Cm(0.8), Cm(0.7), size=10, color=C_LGRAY, align=PP_ALIGN.CENTER)

    # Rodapé informativo
    n_calls = len(calls)
    n_estr  = len(estruturadas)
    narr = (f"{n_calls} call{'s' if n_calls != 1 else ''} da equipe e "
            f"{n_estr} operação{'ões' if n_estr != 1 else ''} estruturada{'s' if n_estr != 1 else ''} "
            f"disponíveis para este cliente. Analise a aderência ao perfil antes de operar.")
    add_caixa_texto(sl, narr, SH - Cm(2.7), cor_borda=C_PURP, cor_bg=C_CARD2)

# ── SLIDE 10: RENDA VARIÁVEL ──────────────────────────────────────────────────
def s_rv(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "RENDA VARIÁVEL", "Ações e Fundos Imobiliários na carteira")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    acoes = d.get("acoes", [])
    fiis  = d.get("fiis", [])

    col_w = (SW - Cm(2)) / 2 - Cm(0.3)
    cx1, cx2 = MARGIN, MARGIN + col_w + Cm(0.6)

    def render_tbl(cx, titulo, items, cor):
        add_text(sl, titulo, cx, Cm(3.1), col_w, Cm(0.55), size=9, bold=True, color=cor)
        if not items:
            add_rect(sl, cx, Cm(3.75), col_w, Cm(2), C_CARD, C_GRAY, 0.3)
            add_text(sl, "Nenhum ativo desta classe na carteira",
                     cx + Cm(0.4), Cm(4.2), col_w - Cm(0.8), Cm(0.7), size=9.5, color=C_LGRAY)
            return
        add_rect(sl, cx, Cm(3.75), col_w, Cm(0.65), C_CARD2)
        add_text(sl, "TICKER", cx + Cm(0.2), Cm(3.8), col_w * 0.55, Cm(0.55),
                 size=8, bold=True, color=C_LGRAY)
        add_text(sl, "%", cx + col_w * 0.6, Cm(3.8), col_w * 0.35, Cm(0.55),
                 size=8, bold=True, color=C_LGRAY)
        row_h = Cm(0.75)
        for k, a in enumerate(items[:12]):
            ry    = Cm(4.45) + k * row_h
            fundo = C_CARD if k % 2 == 0 else C_CARD3
            add_rect(sl, cx, ry, col_w, row_h, fundo)
            ticker = a.get("ticker", "")
            perc   = a.get("perc_carteira", a.get("perc", 0))
            nome_a = a.get("nome", "")
            add_text(sl, ticker, cx + Cm(0.2), ry + Cm(0.1), col_w * 0.35, Cm(0.55),
                     size=10, bold=True, color=cor)
            add_text(sl, nome_a, cx + Cm(0.2) + col_w * 0.35, ry + Cm(0.1),
                     col_w * 0.25, Cm(0.55), size=8, color=C_LGRAY)
            add_text(sl, f"{perc:.2f}%", cx + col_w * 0.6, ry + Cm(0.1),
                     col_w * 0.35, Cm(0.55), size=10, color=C_LGRAY, align=PP_ALIGN.RIGHT)

    render_tbl(cx1, "📊  AÇÕES", acoes, C_GREEN)
    render_tbl(cx2, "🏢  FUNDOS IMOBILIÁRIOS (FIIs)", fiis, C_BLUE)

    comp       = d.get("composicao", {})
    total_rv   = comp.get("acoes", 0)
    total_fiis = comp.get("fiis", 0)
    partes_rv  = []
    if acoes:
        partes_rv.append(f"{len(acoes)} ação{'ões' if len(acoes)>1 else ''}, "
                         f"alocação total {total_rv:.1f}% em RV.")
    if fiis:
        partes_rv.append(f"{len(fiis)} FII{'s' if len(fiis)>1 else ''}, "
                         f"representando {total_fiis:.1f}% da carteira.")
    narr_rv = " ".join(partes_rv) if partes_rv else "Sem exposição a renda variável."
    add_caixa_texto(sl, narr_rv, SH - Cm(2.7),
                    cor_borda=C_GREEN if (acoes or fiis) else C_AMBER,
                    cor_bg=C_CARD2)

# ── SLIDE 11: MODELO DE SERVIR ────────────────────────────────────────────────
def s_modelo_servir(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "MODELO DE SERVIR", "Trilha de relacionamento e engajamento do cliente")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    checklist = d.get("checklist", {})
    score     = d.get("score_servir", 0)
    total     = 6

    PILARES = [
        ("open_investments",         "Open Investments",       "CRÍTICA", "🔗"),
        ("financial_planning",       "Financial Planning",     "CRÍTICA", "🎯"),
        ("ordem_enviada",            "Ordem Enviada",          "ALTA",    "📋"),
        ("conta_acessada",           "Conta Acessada",         "ALTA",    "📱"),
        ("xperformance",             "X-Performance",          "MÉDIA",   "📊"),
        ("atividade_relacionamento", "Atividade Relac.",       "ALTA",    "🤝"),
    ]
    IMP_COR = {"CRÍTICA": C_RED, "ALTA": C_AMBER, "MÉDIA": C_LGRAY}

    # Score bar
    pct_score = score / total if total else 0
    cor_score = C_GREEN if pct_score >= 0.8 else (C_AMBER if pct_score >= 0.5 else C_RED)
    add_rect(sl, MARGIN, Cm(3.1), SW - Cm(1.4), Cm(1.8), C_CARD, C_GRAY, 0.3)
    add_rect(sl, MARGIN, Cm(3.1), (SW - Cm(1.4)) * pct_score, Cm(1.8), cor_score)
    add_text(sl, f"Score: {score}/{total} pilares concluídos",
             MARGIN + Cm(0.5), Cm(3.45), SW - Cm(2), Cm(1.1),
             size=14, bold=True, color=C_BG if pct_score > 0.3 else C_WHITE)

    # Cards dos pilares
    n_cols = 3
    col_w  = (SW - Cm(1.4)) / n_cols - Cm(0.25)
    row_h  = Cm(2.5)
    for i, (pid, nome, imp, icone) in enumerate(PILARES):
        col = i % n_cols; row = i // n_cols
        cx  = MARGIN + col * (col_w + Cm(0.25))
        ry  = Cm(5.3) + row * (row_h + Cm(0.2))
        feito     = bool(checklist.get(pid))
        cor_borda = C_GREEN if feito else IMP_COR.get(imp, C_GRAY)
        add_rect(sl, cx, ry, col_w, row_h, C_CARD, cor_borda, 0.5)
        if feito:
            add_rect(sl, cx, ry, col_w, Cm(0.15), C_GREEN)
        add_text(sl, f"{icone}  {nome}", cx + Cm(0.3), ry + Cm(0.3),
                 col_w - Cm(0.6), Cm(0.75), size=11, bold=True, color=C_WHITE)
        add_text(sl, imp, cx + Cm(0.3), ry + Cm(1.1), col_w - Cm(0.6), Cm(0.5),
                 size=8, color=IMP_COR.get(imp, C_LGRAY))
        status_txt = "✅  Concluído" if feito else "⏳  Pendente"
        add_text(sl, status_txt, cx + Cm(0.3), ry + Cm(1.7), col_w - Cm(0.6), Cm(0.5),
                 size=9, bold=feito, color=C_GREEN if feito else C_RED)

    pendentes = [nome for pid, nome, imp, icone in PILARES if not checklist.get(pid)]
    criticos  = [nome for pid, nome, imp, icone in PILARES if not checklist.get(pid) and imp == "CRÍTICA"]
    if score == 6:
        narrativa_ms = ("Excelente! Todos os 6 pilares concluídos. Engajamento máximo — menor risco "
                        "de ruptura e maior potencial de cross sell.")
        cor_ms = C_GREEN
    elif criticos:
        narrativa_ms = (f"{score}/6 pilares. Críticos pendentes: {' e '.join(criticos)} — "
                        f"prioridade máxima na próxima interação.")
        cor_ms = C_RED
    else:
        narrativa_ms = (f"{score}/6 pilares. Pendentes: {', '.join(pendentes)}. "
                        f"Completar fortalece o vínculo e reduz risco de portabilidade.")
        cor_ms = C_AMBER
    add_caixa_texto(sl, narrativa_ms, SH - Cm(2.7), cor_borda=cor_ms, cor_bg=C_CARD2)

# ── SLIDE 12: SUGESTÕES ───────────────────────────────────────────────────────
def s_sugestoes(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "SUGESTÕES DE REALOCAÇÃO",
           "Produtos recomendados pelo Head de Produtos — Levante Asset")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    sugs = d.get("sugestoes_produtos", [])
    if not sugs:
        add_rect(sl, MARGIN, Cm(4.0), SW - Cm(1.4), Cm(3.5), C_CARD, C_GRAY, 0.3)
        add_text(sl, "Sem sugestões publicadas para este perfil no momento",
                 SW / 2 - Cm(8), Cm(5.2), Cm(16), Cm(1),
                 size=12, color=C_LGRAY, align=PP_ALIGN.CENTER)
        return

    n  = min(len(sugs), 4)
    cw = (SW - Cm(1.4)) / n - Cm(0.25)
    top_y  = Cm(3.2)
    card_h = SH - top_y - Cm(0.75)

    for i, s in enumerate(sugs[:4]):
        p   = s.get("produto", {})
        cx  = MARGIN + i * (cw + Cm(0.25))
        cls = s.get("classe", "")
        cor = CLS_COR.get(cls, C_LGRAY)
        add_rect(sl, cx, top_y, cw, card_h, C_CARD, cor, 0.5)
        add_rect(sl, cx, top_y, cw, Cm(0.18), cor)
        add_rect(sl, cx + Cm(0.3), top_y + Cm(0.35), Cm(3.5), Cm(0.55), C_CARD2)
        add_text(sl, s.get("label_classe", CLS_LABEL.get(cls, cls)), cx + Cm(0.4),
                 top_y + Cm(0.38), Cm(3.3), Cm(0.48), size=7.5, bold=True, color=cor)
        gap = s.get("gap", 0)
        add_text(sl, f"Gap {gap:+.1f}%", cx + cw - Cm(2.0), top_y + Cm(0.38),
                 Cm(1.8), Cm(0.48), size=8, bold=True,
                 color=C_RED if gap < 0 else C_GREEN, align=PP_ALIGN.RIGHT)
        add_text(sl, p.get("nome", "—"), cx + Cm(0.3), top_y + Cm(1.05),
                 cw - Cm(0.6), Cm(1.5), size=12, bold=True, color=C_WHITE, wrap=True)
        add_rect(sl, cx + Cm(0.3), top_y + Cm(2.7), cw - Cm(0.6), Cm(0.04), C_GRAY)
        if p.get("taxa"):
            add_text(sl, p["taxa"], cx + Cm(0.3), top_y + Cm(2.85),
                     cw - Cm(0.6), Cm(0.65), size=13, bold=True, color=C_GREEN)
        if p.get("emissor"):
            add_text(sl, p["emissor"], cx + Cm(0.3), top_y + Cm(3.6),
                     cw - Cm(0.6), Cm(0.5), size=9, color=C_LGRAY)
        if p.get("vencimento"):
            add_text(sl, f"Venc: {p['vencimento']}", cx + Cm(0.3), top_y + Cm(4.2),
                     cw - Cm(0.6), Cm(0.5), size=8.5, color=C_GRAY)
        add_rect(sl, cx + Cm(0.3), top_y + Cm(4.8), cw - Cm(0.6), Cm(0.04), C_GRAY)
        if p.get("motivo"):
            add_text(sl, p["motivo"], cx + Cm(0.3), top_y + Cm(4.95),
                     cw - Cm(0.6), Cm(2.8), size=8.5, color=C_LGRAY, wrap=True)
        if p.get("indicado_por"):
            add_text(sl, f"Indicado: {p['indicado_por']}", cx + Cm(0.3),
                     top_y + card_h - Cm(0.85), cw - Cm(0.6), Cm(0.6),
                     size=7.5, color=C_GRAY, italic=True)

# ── SLIDE 13: CROSS SELL ──────────────────────────────────────────────────────
def s_cross_sell(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "CROSS SELL", "Oportunidades de produtos e serviços Braúna")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    cross_ativos = d.get("cross_ativos_nomes", d.get("cross_ativos", []))
    AREAS = [
        ("Aquisição de Bens",           "🏠", "Financiamento imobiliário e consórcio"),
        ("Gestão Discricionária Prunus","🌿", "Carteira administrada pela Prunus Asset"),
        ("Planejamento Patrimonial",    "🏛️", "Estruturação patrimonial e sucessória"),
        ("Planejamento Financeiro",     "🎯", "Financial Planning completo"),
        ("Investimentos Internacionais","🌎", "Ativos no exterior e dolarização"),
    ]
    col_w = (SW - Cm(1.4)) / len(AREAS) - Cm(0.25)
    top_y = Cm(3.2)
    card_h = SH - top_y - Cm(0.75)

    for i, (nome_a, icone, desc) in enumerate(AREAS):
        ativo = nome_a in cross_ativos
        cx    = MARGIN + i * (col_w + Cm(0.25))
        cor   = C_GREEN if ativo else C_GRAY
        add_rect(sl, cx, top_y, col_w, card_h, C_CARD, cor, 0.5)
        add_rect(sl, cx, top_y, col_w, Cm(0.18), cor)
        add_text(sl, icone, cx + col_w / 2 - Cm(1), top_y + Cm(0.5), Cm(2), Cm(1.4),
                 size=28, align=PP_ALIGN.CENTER)
        add_text(sl, nome_a, cx + Cm(0.3), top_y + Cm(2.1), col_w - Cm(0.6), Cm(1.4),
                 size=10, bold=True, color=C_WHITE, wrap=True, align=PP_ALIGN.CENTER)
        add_text(sl, desc, cx + Cm(0.3), top_y + Cm(3.6), col_w - Cm(0.6), Cm(1.8),
                 size=8.5, color=C_LGRAY, wrap=True, align=PP_ALIGN.CENTER)
        status = "✓  ATIVO" if ativo else "○  Oportunidade"
        add_text(sl, status, cx + Cm(0.3), top_y + card_h - Cm(1.0), col_w - Cm(0.6), Cm(0.65),
                 size=9, bold=ativo, color=cor, align=PP_ALIGN.CENTER)

    cross_n   = sum(1 for n2, _, _ in AREAS if n2 in cross_ativos)
    n_inativos = len(AREAS) - cross_n
    if cross_n >= 4:
        narr_cross = (f"Cliente bem engajado ({cross_n}/5 produtos ativos). "
                      f"Foco em manutenção e satisfação.")
    else:
        narr_cross = (f"{n_inativos} de 5 produtos sem ativação — potencial de aprofundamento. "
                      f"Produtos ativos: {cross_n}/5.")
    add_caixa_texto(sl, narr_cross, top_y + card_h + Cm(0.3),
                    cor_borda=C_GREEN if cross_n >= 4 else C_AMBER, cor_bg=C_CARD2)

# ── SLIDE 14: RESUMO EXECUTIVO ────────────────────────────────────────────────
def s_resumo(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "RESUMO EXECUTIVO", "Principais indicadores desta reunião")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    comp    = d.get("composicao", {})
    pat     = d.get("patrimonio", 0)
    rent    = d.get("rent", {})
    pr      = rent.get("portfolio", {}) if isinstance(rent, dict) else {}
    cr      = rent.get("cdi", {})       if isinstance(rent, dict) else {}
    score   = d.get("score_servir", 0)
    cross_n = len(d.get("cross_ativos_nomes", d.get("cross_ativos", [])))
    desvios = d.get("desvios", [])
    n_fora  = len([x for x in desvios if abs(x.get("desvio_pp", x.get("desvio", 0))) > 3])
    r12     = pr.get("12m", 0)
    c12     = cr.get("12m", 0)
    pct_cdi = round(r12 / c12 * 100, 0) if c12 else 0

    cards = [
        ("💰  Patrimônio",    fmt(pat),           "Total sob gestão",       C_GOLD),
        ("📈  Rentab. 12M",   f"{r12:.2f}%",      f"{pct_cdi:.0f}% do CDI", pct_cor(r12)),
        ("🤝  Modelo Servir", f"{score}/6",        "Pilares concluídos",     C_GREEN if score >= 5 else (C_AMBER if score >= 3 else C_RED)),
        ("🔗  Cross Sell",    f"{cross_n}/5",      "Produtos ativos",        C_GREEN if cross_n >= 3 else C_AMBER),
        ("⚠️  Desvios",       str(n_fora),         "Classes fora do modelo", C_GREEN if n_fora == 0 else (C_AMBER if n_fora <= 2 else C_RED)),
    ]
    cw = (SW - Cm(1.4)) / len(cards) - Cm(0.25)
    for i, (lbl, val, sub, cor) in enumerate(cards):
        cx = MARGIN + i * (cw + Cm(0.25))
        add_rect(sl, cx, Cm(3.2), cw, Cm(3.2), C_CARD, cor, 0.5)
        add_rect(sl, cx, Cm(3.2), cw, Cm(0.18), cor)
        add_text(sl, lbl, cx + Cm(0.3), Cm(3.5), cw - Cm(0.6), Cm(0.6), size=9, color=C_LGRAY)
        add_text(sl, val,  cx + Cm(0.3), Cm(4.1), cw - Cm(0.6), Cm(1.3), size=20, bold=True, color=cor)
        add_text(sl, sub,  cx + Cm(0.3), Cm(5.5), cw - Cm(0.6), Cm(0.6), size=8, color=C_LGRAY)

    # Barra de composição segmentada
    add_text(sl, "COMPOSIÇÃO ATUAL", MARGIN, Cm(7.2), SW, Cm(0.55), size=9, bold=True, color=C_LGRAY)
    cats_v     = [(c, comp.get(c, 0)) for c in CATS if comp.get(c, 0) > 0]
    bar_total  = sum(v for _, v in cats_v) or 1
    bar_w_total = SW - Cm(1.4)
    bx = MARGIN; by = Cm(7.9)
    for cat, v in cats_v:
        bw_seg = bar_w_total * (v / bar_total)
        add_rect(sl, bx, by, max(bw_seg - Cm(0.05), Cm(0.1)), Cm(1.0),
                 CLS_COR.get(cat, C_LGRAY))
        bx += bw_seg

    # Legenda
    bx2 = MARGIN; ly = Cm(9.15)
    for cat, v in cats_v:
        if v < 1: continue
        add_rect(sl, bx2, ly, Cm(0.4), Cm(0.4), CLS_COR.get(cat, C_LGRAY))
        lbl_txt = f"{CLS_LABEL.get(cat,cat)} {v:.0f}%"
        add_text(sl, lbl_txt, bx2 + Cm(0.55), ly, Cm(4.0), Cm(0.45), size=8, color=C_LGRAY)
        bx2 += Cm(4.3)
        if bx2 > SW - Cm(5): bx2 = MARGIN; ly += Cm(0.6)

    nome_cli = d.get("nome_cliente", "O cliente")
    perfil   = d.get("perfil", "")
    pontos_p = []
    pontos_a = []
    if pct_cdi >= 90: pontos_p.append(f"rentabilidade saudável ({pct_cdi:.0f}% do CDI em 12M)")
    else:             pontos_a.append(f"rentabilidade abaixo do esperado ({pct_cdi:.0f}% do CDI)")
    if score >= 5:    pontos_p.append(f"Modelo de Servir estruturado ({score}/6)")
    elif score <= 2:  pontos_a.append(f"Modelo de Servir crítico ({score}/6)")
    else:             pontos_a.append(f"Modelo de Servir parcial ({score}/6)")
    if n_fora == 0:   pontos_p.append("carteira alinhada ao modelo")
    elif n_fora >= 3: pontos_a.append(f"{n_fora} classes fora do modelo")
    if cross_n >= 3:  pontos_p.append(f"cross sell ativo ({cross_n}/5)")
    else:             pontos_a.append(f"cross sell ({cross_n}/5 produtos ativos)")

    partes = []
    if pontos_p: partes.append("Positivos: " + "; ".join(pontos_p))
    if pontos_a: partes.append("Atenção: " + "; ".join(pontos_a))
    narr = f"{nome_cli} ({perfil}): " + ". ".join(partes) + "." if partes else ""
    if narr:
        add_caixa_texto(sl, narr, SH - Cm(2.7),
                        cor_borda=C_GREEN if not pontos_a else (C_AMBER if len(pontos_a) <= 1 else C_RED),
                        cor_bg=C_CARD2)

# ── SLIDE 15: PRÓXIMOS PASSOS (visual cards) ──────────────────────────────────
def s_proximos(prs, d):
    sl = new_slide(prs)
    bg(sl)
    header(sl, "PRÓXIMOS PASSOS", "Encaminhamentos acordados nesta reunião")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    ICONS = ["📋", "📅", "🔗", "📊", "🔔"]

    passos_default = [
        ("Assinar proposta de realocação",
         "Assessor encaminha modelo por e-mail",
         "Assessor",
         "5 dias úteis"),
        ("Agendar revisão em 60 dias",
         "Assessor agenda contato de acompanhamento",
         "Assessor",
         "60 dias"),
        ("Ativar Open Investments (OPIN)",
         "Cliente acessa app e autoriza conexão",
         "Cliente",
         "7 dias"),
        ("Enviar simulação de IR para ativos a resgatar",
         "Assessor prepara planilha de ganho de capital",
         "Assessor",
         "3 dias"),
        ("Confirmar interesse nos produtos apresentados",
         "Cliente retorna confirmação ao assessor",
         "Cliente",
         "10 dias"),
    ]

    passos_ia = d.get("ia_proximos_passos", "")
    if passos_ia:
        linhas = [l.strip("•- ") for l in passos_ia.split("\n") if l.strip()]
        passos = [(l, "Conforme acordado", "Assessor", "Conforme acordado") for l in linhas]
    else:
        passos = passos_default

    # Responsável/prazo header
    add_text(sl, "AÇÃO", MARGIN + Cm(3.5), Cm(3.0), Cm(14), Cm(0.5),
             size=8, bold=True, color=C_LGRAY)
    add_text(sl, "RESPONSÁVEL", SW - Cm(7.5), Cm(3.0), Cm(3.5), Cm(0.5),
             size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.CENTER)
    add_text(sl, "PRAZO", SW - Cm(4.0), Cm(3.0), Cm(3.2), Cm(0.5),
             size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.CENTER)

    row_h = Cm(2.1)
    for i, item in enumerate(passos[:5]):
        acao, desc, resp, prazo = (item + ("", "", ""))[:4]
        ry   = Cm(3.55) + i * (row_h + Cm(0.08))
        icon = ICONS[i % len(ICONS)]
        resp_cor = C_BLUE if str(resp).lower() == "cliente" else C_GOLD

        # Card background
        add_rect(sl, MARGIN, ry, SW - Cm(1.4), row_h, C_CARD, C_CARD2, 0.3)
        # Gold left strip
        add_rect(sl, MARGIN, ry, Cm(0.12), row_h, C_GOLD)

        # Number + icon
        add_rect(sl, MARGIN + Cm(0.18), ry, Cm(3.1), row_h, C_CARD2)
        add_text(sl, icon,         MARGIN + Cm(0.25), ry + Cm(0.2), Cm(3.0), Cm(0.8),
                 size=20, align=PP_ALIGN.CENTER)
        add_text(sl, f"0{i+1}",    MARGIN + Cm(0.25), ry + Cm(1.1), Cm(3.0), Cm(0.7),
                 size=14, bold=True, color=C_GOLD, align=PP_ALIGN.CENTER)

        # Ação + descrição
        add_text(sl, acao, MARGIN + Cm(3.5), ry + Cm(0.28),
                 SW - Cm(11.5), Cm(0.8), size=12, bold=True, color=C_WHITE)
        add_text(sl, desc, MARGIN + Cm(3.5), ry + Cm(1.15),
                 SW - Cm(11.5), Cm(0.6), size=9, color=C_LGRAY, italic=True)

        # Responsável badge
        add_rect(sl, SW - Cm(7.5), ry + Cm(0.5), Cm(3.2), Cm(0.65), resp_cor)
        add_text(sl, str(resp), SW - Cm(7.5), ry + Cm(0.58), Cm(3.2), Cm(0.5),
                 size=9, bold=True, color=C_BG, align=PP_ALIGN.CENTER)

        # Prazo
        add_rect(sl, SW - Cm(4.1), ry + Cm(0.5), Cm(3.0), Cm(0.65), C_CARD3, C_GOLD, 0.4)
        add_text(sl, str(prazo), SW - Cm(4.1), ry + Cm(0.58), Cm(3.0), Cm(0.5),
                 size=8.5, color=C_GOLD, align=PP_ALIGN.CENTER)

    # Próxima revisão
    try:
        dr = d.get("data_ref", "")
        partes_d = dr.split("/")
        if len(partes_d) == 3:
            base_dt = datetime.date(int(partes_d[2]), int(partes_d[1]), int(partes_d[0]))
        else:
            base_dt = datetime.date.today()
        proxima_str = (base_dt + datetime.timedelta(days=60)).strftime("%d/%m/%Y")
    except Exception:
        proxima_str = "em 60 dias"

    add_rect(sl, MARGIN, SH - Cm(1.55), SW - Cm(1.4), Cm(0.04), C_GOLD)
    add_text(sl, f"📅  Próxima revisão sugerida: {proxima_str}",
             MARGIN, SH - Cm(1.45), SW - Cm(1.4), Cm(0.5),
             size=9, bold=True, color=C_GOLD)
    add_text(sl, d.get("assessor", "Assessor Braúna"), MARGIN, SH - Cm(0.95),
             Cm(9), Cm(0.5), size=9, color=C_LGRAY)

# ── SLIDE 16: ENCERRAMENTO ────────────────────────────────────────────────────
def s_encerramento(prs, d):
    sl = new_slide(prs)
    bg(sl)
    add_rect(sl, 0, 0, Cm(0.12), SH, C_GOLD)
    add_rect(sl, 0, 0, Cm(1.3), SH, C_CARD)
    gold_line(sl, y=SH / 2 - Cm(0.04), thickness=Cm(0.08))

    add_text(sl, "OBRIGADO", Cm(1.7), SH / 2 - Cm(4.5), SW - Cm(2), Cm(3),
             size=44, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
    add_text(sl, "Estamos comprometidos com a realização dos seus objetivos financeiros.",
             Cm(1.7), SH / 2 - Cm(1.3), SW - Cm(2), Cm(0.8),
             size=12, color=C_LGRAY, align=PP_ALIGN.CENTER)
    add_text(sl, "Nosso time está à disposição.",
             Cm(1.7), SH / 2 - Cm(0.5), SW - Cm(2), Cm(0.65),
             size=11, color=C_LGRAY, align=PP_ALIGN.CENTER)

    assessor       = d.get("assessor", "Assessor Braúna")
    email_assessor = d.get("email_assessor", d.get("assessor_email",
                            "contato@braunainvestimentos.com.br"))
    add_text(sl, assessor, Cm(1.7), SH / 2 + Cm(0.5), SW - Cm(2), Cm(0.95),
             size=18, bold=True, color=C_GOLD, align=PP_ALIGN.CENTER)
    add_text(sl, email_assessor, Cm(1.7), SH / 2 + Cm(1.5), SW - Cm(2), Cm(0.65),
             size=11, color=C_LGRAY, align=PP_ALIGN.CENTER)
    add_text(sl, "Assessor de Investimentos — Braúna Investimentos", Cm(1.7),
             SH / 2 + Cm(2.2), SW - Cm(2), Cm(0.6),
             size=9.5, color=C_GRAY, align=PP_ALIGN.CENTER)

    cards_enc = [
        ("📞  Contato direto",          "Fale com seu assessor a qualquer momento"),
        ("📅  Próxima reunião em 60 dias","Revisão periódica da carteira agendada"),
        ("📊  Relatório X-Performance", "Acompanhe sua carteira pelo portal"),
    ]
    cw_enc = (SW - Cm(2.8)) / 3 - Cm(0.2)
    for i, (titulo_enc, desc_enc) in enumerate(cards_enc):
        cx_enc = Cm(1.7) + i * (cw_enc + Cm(0.2))
        add_rect(sl, cx_enc, SH - Cm(3.0), cw_enc, Cm(1.8), C_CARD2, C_GRAY, 0.3)
        add_text(sl, titulo_enc, cx_enc + Cm(0.3), SH - Cm(2.85),
                 cw_enc - Cm(0.6), Cm(0.7), size=9.5, bold=True, color=C_GOLD, wrap=True)
        add_text(sl, desc_enc, cx_enc + Cm(0.3), SH - Cm(2.15),
                 cw_enc - Cm(0.6), Cm(0.75), size=8.5, color=C_LGRAY, wrap=True)

    fontes = (d.get("cenario_macro") or {}).get("fontes", [])
    if fontes:
        fontes_txt = "Fontes: " + " · ".join(
            f.get("nome", "") or f.get("fonte", "") for f in fontes[:4]
            if f.get("nome") or f.get("fonte"))
        add_text(sl, fontes_txt, Cm(1.7), SH - Cm(1.3), SW - Cm(2), Cm(0.5),
                 size=7.5, color=C_GRAY, align=PP_ALIGN.CENTER)

    add_text(sl, "Documento confidencial · Não constitui recomendação formal de investimento",
             Cm(1.7), SH - Cm(0.75), SW - Cm(2), Cm(0.55),
             size=7.5, color=C_GRAY, align=PP_ALIGN.CENTER)

# ── GERADOR PRINCIPAL ─────────────────────────────────────────────────────────
def gerar_apresentacao_pptx(d: dict) -> bytes:
    """
    Gera PPTX com identidade Braúna. Retorna bytes.
    Slides fixos: 1-Capa, 2-Agenda, 3-Cenário Global, 4-Brasil&HP,
                  5-Patrimônio (bar chart), 6-Composição (donut),
                  7-Carteira vs Modelo (hbar), 11-Modelo Servir,
                  14-Resumo, 15-Próximos Passos, 16-Encerramento
    Opcionais: 8-Desvios, 9-Calls&Oportunidades, 10-RV,
               12-Sugestões, 13-Cross Sell
    """
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    tem_desvios      = bool(d.get("desvios"))
    tem_calls        = bool(d.get("calls") or d.get("estruturadas"))
    tem_rv           = bool(d.get("acoes") or d.get("fiis"))
    tem_sugs         = bool(d.get("sugestoes_produtos"))
    tem_cross        = bool(d.get("cross_ativos") or d.get("cross_ativos_nomes"))

    # Monta agenda dinamicamente
    agenda_items = [
        (1, "Cenário Global",      "Panorama macroeconômico internacional"),
        (2, "Brasil & HP",         "Visão Head de Produtos — Levante Asset"),
        (3, "Patrimônio",          "Evolução e rentabilidade da carteira"),
        (4, "Composição",          "Alocação por classe de ativo"),
        (5, "Carteira vs. Modelo", "Comparativo e desvios do perfil"),
    ]
    n = 6
    if tem_desvios:
        agenda_items.append((n, "Desvios",            "O que ajustar para atingir o modelo")); n += 1
    if tem_calls:
        agenda_items.append((n, "Calls & Oportunidades", "Recomendações e operações estruturadas")); n += 1
    if tem_rv:
        agenda_items.append((n, "Renda Variável",     "Ações e FIIs na carteira")); n += 1
    agenda_items.append((n,     "Modelo de Servir",   "Trilha de relacionamento")); n += 1
    if tem_sugs:
        agenda_items.append((n, "Sugestões",          "Produtos recomendados pelo Head de Produtos")); n += 1
    if tem_cross:
        agenda_items.append((n, "Cross Sell",         "Oportunidades de produtos e serviços")); n += 1
    agenda_items.append((n,     "Resumo Executivo",   "Principais indicadores da reunião")); n += 1
    agenda_items.append((n,     "Próximos Passos",    "Encaminhamentos acordados")); n += 1

    # Slides fixos
    s_capa(prs, d)
    s_agenda(prs, d, agenda_items)
    s_cenario_global(prs, d)
    s_cenario_brasil(prs, d)
    s_patrimonio(prs, d)
    s_composicao(prs, d)
    s_vs_modelo(prs, d)

    # Opcionais
    if tem_desvios:
        s_desvios(prs, d)
    if tem_calls:
        s_calls(prs, d)
    if tem_rv:
        s_rv(prs, d)

    s_modelo_servir(prs, d)

    if tem_sugs:
        s_sugestoes(prs, d)
    if tem_cross:
        s_cross_sell(prs, d)

    s_resumo(prs, d)
    s_proximos(prs, d)
    s_encerramento(prs, d)

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()
