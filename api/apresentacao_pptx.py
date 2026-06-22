"""
Gerador de Apresentação PPTX — Braúna Investimentos
Cenário Macro · Análise da Carteira · Sugestões de Realocação
"""
import io
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm

# ── Paleta ────────────────────────────────────────────────────────────────────
C_BG     = RGBColor(0x0A, 0x0A, 0x08)
C_CARD   = RGBColor(0x11, 0x11, 0x10)
C_CARD2  = RGBColor(0x1A, 0x1A, 0x18)
C_GOLD   = RGBColor(0xD6, 0xB2, 0x7A)
C_GOLD2  = RGBColor(0xE8, 0xC9, 0x6B)
C_GREEN  = RGBColor(0x5D, 0xCA, 0xA5)
C_RED    = RGBColor(0xFF, 0x6B, 0x6B)
C_AMBER  = RGBColor(0xF0, 0xA8, 0x30)
C_BLUE   = RGBColor(0x7D, 0xCF, 0xEF)
C_PURPLE = RGBColor(0xB0, 0x8F, 0xCF)
C_WHITE  = RGBColor(0xF0, 0xF0, 0xF0)
C_LGRAY  = RGBColor(0x88, 0x88, 0x80)
C_GRAY   = RGBColor(0x3A, 0x3A, 0x34)

CLS_COR = {
    "pos_fixado":    C_GOLD,
    "inflacao":      C_AMBER,
    "pre_fixado":    RGBColor(0xF0, 0x78, 0x50),
    "acoes":         C_GREEN,
    "fiis":          C_BLUE,
    "multimercado":  C_PURPLE,
    "alternativos":  RGBColor(0x4E, 0xC9, 0xB0),
    "internacional": RGBColor(0x5B, 0x9B, 0xD5),
    "criptomoedas":  C_LGRAY,
}
CLS_LABEL = {
    "pos_fixado": "Pós Fixado", "inflacao": "Inflação", "pre_fixado": "Pré Fixado",
    "acoes": "Ações", "fiis": "FIIs", "multimercado": "Multimercado",
    "alternativos": "Alternativos", "internacional": "Internacional",
    "criptomoedas": "Criptomoedas",
}

# Slide 16:9 widescreen
SW = Cm(33.87)
SH = Cm(19.05)


# ── Primitivas ────────────────────────────────────────────────────────────────
def _rgb(slide):
    return slide.shapes

def add_rect(slide, x, y, w, h, fill_rgb, border_rgb=None, border_pt=0.5):
    shape = slide.shapes.add_shape(1, x, y, w, h)  # MSO_SHAPE_TYPE.RECTANGLE = 1
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_rgb
    if border_rgb:
        shape.line.color.rgb = border_rgb
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    return shape

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

def slide_bg(slide):
    add_rect(slide, 0, 0, SW, SH, C_BG)

def add_header(slide, titulo, sub=""):
    # Linha dourada no topo
    add_rect(slide, 0, 0, SW, Cm(0.08), C_GOLD)
    # Logo texto
    add_text(slide, "BRAÚNA INVESTIMENTOS", Cm(0.7), Cm(0.15), Cm(10), Cm(0.7),
             size=7, bold=True, color=C_GOLD)
    # Título do slide
    add_text(slide, titulo, Cm(0.7), Cm(0.9), Cm(25), Cm(1.2),
             size=20, bold=True, color=C_WHITE)
    if sub:
        add_text(slide, sub, Cm(0.7), Cm(2.1), Cm(25), Cm(0.7),
                 size=10, color=C_LGRAY)

def add_footer(slide, nome, data):
    add_rect(slide, 0, SH - Cm(0.6), SW, Cm(0.6), C_CARD2)
    add_text(slide, nome, Cm(0.7), SH - Cm(0.55), Cm(15), Cm(0.5),
             size=8, color=C_LGRAY)
    add_text(slide, f"Reunião de carteira  ·  {data}", SW - Cm(9), SH - Cm(0.55),
             Cm(8.5), Cm(0.5), size=8, color=C_LGRAY, align=PP_ALIGN.RIGHT)

def fmt(v):
    if v >= 1_000_000:
        return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:
        return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:.0f}"


# ── SLIDE 1: CAPA ─────────────────────────────────────────────────────────────
def slide_capa(prs, d):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    slide_bg(slide)
    add_rect(slide, 0, 0, SW, Cm(0.08), C_GOLD)

    # Faixa lateral dourada
    add_rect(slide, 0, 0, Cm(1.2), SH, RGBColor(0x18, 0x14, 0x08))
    add_rect(slide, 0, 0, Cm(0.12), SH, C_GOLD)

    # Logo
    add_text(slide, "BRAÚNA INVESTIMENTOS", Cm(1.8), Cm(2.5), Cm(20), Cm(1.2),
             size=11, bold=True, color=C_GOLD, italic=False)

    # Título principal
    add_text(slide, "APRESENTAÇÃO DE REUNIÃO", Cm(1.8), Cm(4.2), Cm(28), Cm(2),
             size=26, bold=True, color=C_WHITE)

    # Nome cliente
    nome = d.get("nome_cliente", "Cliente")
    add_rect(slide, Cm(1.8), Cm(7.0), Cm(22), Cm(0.06), C_GOLD)
    add_text(slide, nome, Cm(1.8), Cm(7.3), Cm(22), Cm(1.4),
             size=22, bold=False, color=C_GOLD)

    # Patrimônio + data
    pat = d.get("patrimonio", 0)
    data = d.get("data_ref", "")
    add_text(slide, f"Patrimônio: {fmt(pat)}     ·     Data: {data}",
             Cm(1.8), Cm(9.5), Cm(22), Cm(0.8), size=11, color=C_LGRAY)

    # Perfil + Assessor
    perfil = str(d.get("perfil","")).capitalize()
    assessor = d.get("assessor","")
    add_text(slide, f"Perfil: {perfil}     ·     Assessor: {assessor}",
             Cm(1.8), Cm(10.5), Cm(22), Cm(0.8), size=10, color=C_LGRAY)

    # Rodapé
    add_rect(slide, 0, SH - Cm(1.2), SW, Cm(1.2), C_CARD)
    add_text(slide, "Documento confidencial · Uso exclusivo do cliente · Braúna Investimentos",
             Cm(1.8), SH - Cm(1.0), Cm(28), Cm(0.7), size=8, color=C_GRAY)


# ── SLIDE 2: CENÁRIO MACRO ────────────────────────────────────────────────────
def slide_cenario(prs, d):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(slide)
    add_header(slide, "CENÁRIO MACROECONÔMICO", "Visão Head de Produtos — Levante Asset")
    add_footer(slide, d.get("nome_cliente",""), d.get("data_ref",""))

    cenario = d.get("cenario_macro", {})
    vieses  = cenario.get("vieses", {})

    top_y = Cm(3.2)
    col_w = (SW - Cm(2.0)) / 2 - Cm(0.3)

    # Coluna Esquerda: Global + Brasil
    cx1 = Cm(0.7)
    # Global
    add_text(slide, "CENÁRIO GLOBAL", cx1, top_y, col_w, Cm(0.5),
             size=8, bold=True, color=C_LGRAY)
    add_rect(slide, cx1, top_y + Cm(0.6), col_w, Cm(3.8), C_CARD, C_GRAY, 0.3)
    txt_g = cenario.get("global", "—")
    add_text(slide, txt_g, cx1 + Cm(0.3), top_y + Cm(0.9), col_w - Cm(0.6), Cm(3.4),
             size=9.5, color=C_LGRAY, wrap=True)

    # Brasil
    by = top_y + Cm(4.8)
    add_text(slide, "BRASIL", cx1, by, col_w, Cm(0.5),
             size=8, bold=True, color=C_LGRAY)
    add_rect(slide, cx1, by + Cm(0.6), col_w, Cm(3.8), C_CARD, C_GRAY, 0.3)
    add_text(slide, cenario.get("brasil","—"), cx1 + Cm(0.3), by + Cm(0.9),
             col_w - Cm(0.6), Cm(3.4), size=9.5, color=C_LGRAY, wrap=True)

    # Coluna Direita: Posicionamento + Vieses
    cx2 = cx1 + col_w + Cm(0.6)

    # Posicionamento HP
    add_text(slide, "POSICIONAMENTO HEAD DE PRODUTOS", cx2, top_y, col_w, Cm(0.5),
             size=8, bold=True, color=C_GOLD)
    add_rect(slide, cx2, top_y + Cm(0.6), col_w, Cm(3.8), C_CARD2, C_GOLD, 0.3)
    add_text(slide, cenario.get("posicionamento","—"), cx2 + Cm(0.3), top_y + Cm(0.9),
             col_w - Cm(0.6), Cm(3.4), size=9.5, color=C_LGRAY, wrap=True)

    # Vieses por classe
    VCOR = {"positivo": C_GREEN, "neutro": C_AMBER, "negativo": C_RED}
    VIC  = {"positivo": "▲", "neutro": "→", "negativo": "▼"}

    add_text(slide, "VIESES POR CLASSE DE ATIVO", cx2, by, col_w, Cm(0.5),
             size=8, bold=True, color=C_GOLD)
    add_rect(slide, cx2, by + Cm(0.6), col_w, Cm(3.8), C_CARD2, C_GRAY, 0.3)

    items = list(vieses.items())
    row_h = Cm(0.65)
    for i, (cls, v) in enumerate(items[:6]):
        row_y = by + Cm(1.0) + i * row_h
        cor   = VCOR.get(v, C_LGRAY)
        ic    = VIC.get(v, "→")
        label = CLS_LABEL.get(cls, cls)
        add_rect(slide, cx2 + Cm(0.3), row_y + Cm(0.05), Cm(0.25), Cm(0.35), cor)
        add_text(slide, label, cx2 + Cm(0.7), row_y, col_w - Cm(2.2), Cm(0.55),
                 size=9, color=C_WHITE)
        add_text(slide, ic, cx2 + col_w - Cm(0.8), row_y, Cm(0.6), Cm(0.55),
                 size=10, bold=True, color=cor, align=PP_ALIGN.RIGHT)


# ── SLIDE 3: ANÁLISE DA CARTEIRA ──────────────────────────────────────────────
def slide_carteira(prs, d):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(slide)
    add_header(slide, "ANÁLISE DA CARTEIRA", "Composição atual vs. Modelo de Perfil")
    add_footer(slide, d.get("nome_cliente",""), d.get("data_ref",""))

    comp    = d.get("composicao", {})
    modelo  = d.get("modelo_hp", {})
    pat     = d.get("patrimonio", 0)

    # Métricas no topo
    rent = d.get("rent", {}).get("portfolio", {})
    r12  = rent.get("12m", 0)
    cdi  = d.get("rent", {}).get("cdi", {}).get("12m", 0)
    pct_cdi = (r12 / cdi * 100) if cdi else 0

    metricas = [
        ("Patrimônio", fmt(pat), C_GOLD),
        ("Rentab. 12M", f"{r12:.2f}%", C_GREEN if r12 >= 0 else C_RED),
        ("% CDI 12M", f"{pct_cdi:.0f}%", C_GREEN if pct_cdi >= 80 else C_AMBER),
        ("Rentab. Mês", f"{rent.get('mes',0):.2f}%", C_GREEN if rent.get('mes',0)>=0 else C_RED),
    ]

    mw = (SW - Cm(1.4)) / 4 - Cm(0.2)
    for i, (lbl, val, cor) in enumerate(metricas):
        mx = Cm(0.7) + i * (mw + Cm(0.2))
        add_rect(slide, mx, Cm(3.0), mw, Cm(1.6), C_CARD, C_GRAY, 0.3)
        add_text(slide, lbl, mx + Cm(0.2), Cm(3.1), mw - Cm(0.4), Cm(0.5),
                 size=7.5, color=C_LGRAY)
        add_text(slide, val, mx + Cm(0.2), Cm(3.65), mw - Cm(0.4), Cm(0.8),
                 size=15, bold=True, color=cor)

    # Tabela de composição
    cat_y = Cm(5.0)
    add_text(slide, "CLASSE", Cm(0.7), cat_y, Cm(5), Cm(0.5), size=8, bold=True, color=C_LGRAY)
    add_text(slide, "ATUAL", Cm(5.9), cat_y, Cm(2.5), Cm(0.5), size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.RIGHT)
    add_text(slide, "MODELO", Cm(8.5), cat_y, Cm(2.5), Cm(0.5), size=8, bold=True, color=C_GOLD, align=PP_ALIGN.RIGHT)
    add_text(slide, "DESVIO", Cm(11.1), cat_y, Cm(2.5), Cm(0.5), size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.RIGHT)
    add_text(slide, "R$ ALOCADO", Cm(13.7), cat_y, Cm(4), Cm(0.5), size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.RIGHT)

    CATS = ["pos_fixado","inflacao","pre_fixado","acoes","fiis","multimercado","alternativos","internacional"]
    row_h = Cm(0.85)
    for i, cat in enumerate(CATS):
        atual  = comp.get(cat, 0)
        mod    = modelo.get(cat, 0)
        desvio = round(atual - mod, 1)
        if atual == 0 and mod == 0:
            continue
        ry = cat_y + Cm(0.6) + i * row_h
        cor_linha = C_CARD if i % 2 == 0 else C_CARD2
        add_rect(slide, Cm(0.7), ry, SW - Cm(1.4), row_h - Cm(0.05), cor_linha)
        cor_cat = CLS_COR.get(cat, C_LGRAY)
        add_rect(slide, Cm(0.7), ry, Cm(0.2), row_h - Cm(0.05), cor_cat)

        add_text(slide, CLS_LABEL.get(cat, cat), Cm(1.1), ry + Cm(0.18),
                 Cm(4.8), Cm(0.55), size=10, color=C_WHITE)
        add_text(slide, f"{atual:.1f}%", Cm(5.9), ry + Cm(0.18), Cm(2.5), Cm(0.55),
                 size=10, color=C_WHITE, align=PP_ALIGN.RIGHT)
        add_text(slide, f"{mod:.1f}%", Cm(8.5), ry + Cm(0.18), Cm(2.5), Cm(0.55),
                 size=10, color=C_GOLD, align=PP_ALIGN.RIGHT)
        cor_dev = C_RED if desvio < -3 else (C_GREEN if desvio > 3 else C_LGRAY)
        add_text(slide, f"{desvio:+.1f}%", Cm(11.1), ry + Cm(0.18), Cm(2.5), Cm(0.55),
                 size=10, bold=abs(desvio) > 3, color=cor_dev, align=PP_ALIGN.RIGHT)
        val_r = fmt(pat * atual / 100) if pat else "—"
        add_text(slide, val_r, Cm(13.7), ry + Cm(0.18), Cm(4), Cm(0.55),
                 size=10, color=C_LGRAY, align=PP_ALIGN.RIGHT)

    # Barras visuais (lado direito)
    bx = Cm(18.5)
    bw = SW - bx - Cm(0.7)
    add_text(slide, "ALOCAÇÃO ATUAL", bx, cat_y, bw, Cm(0.5),
             size=8, bold=True, color=C_LGRAY)
    bar_y = cat_y + Cm(0.6)
    max_v = max((comp.get(c,0) for c in CATS), default=1) or 1
    bar_row_h = Cm(0.75)
    for i, cat in enumerate(CATS):
        v = comp.get(cat, 0)
        if v == 0: continue
        by2 = bar_y + i * bar_row_h
        pct = v / max_v
        add_rect(slide, bx, by2 + Cm(0.1), bw * pct, Cm(0.45), CLS_COR.get(cat, C_LGRAY))
        add_text(slide, f"{v:.1f}%", bx + bw * pct + Cm(0.1), by2 + Cm(0.1),
                 Cm(1.5), Cm(0.45), size=8.5, color=C_LGRAY)


# ── SLIDE 4: DESVIOS E REALOCAÇÃO ─────────────────────────────────────────────
def slide_desvios(prs, d):
    desvios = d.get("desvios", [])
    if not desvios:
        return

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(slide)
    add_header(slide, "DESVIOS DA CARTEIRA", "Ações necessárias para atingir o modelo")
    add_footer(slide, d.get("nome_cliente",""), d.get("data_ref",""))

    pat = d.get("patrimonio", 0)
    col_w = (SW - Cm(2.0)) / 2 - Cm(0.2)
    cx1, cx2 = Cm(0.7), Cm(0.7) + col_w + Cm(0.6)

    add_text(slide, "EXCESSO — VENDER / RESGATAR", cx1, Cm(3.2), col_w, Cm(0.5),
             size=9, bold=True, color=C_RED)
    add_text(slide, "DÉFICIT — COMPRAR / APORTAR", cx2, Cm(3.2), col_w, Cm(0.5),
             size=9, bold=True, color=C_GREEN)

    exc = [x for x in desvios if x.get("desvio_pp",0) > 0]
    def_ = [x for x in desvios if x.get("desvio_pp",0) < 0]

    row_h = Cm(1.4)
    for col, items, cor_borda in [(cx1, exc, C_RED), (cx2, def_, C_GREEN)]:
        for i, dev in enumerate(items[:6]):
            ry = Cm(3.9) + i * row_h
            add_rect(slide, col, ry, col_w, row_h - Cm(0.1), C_CARD, cor_borda, 0.3)
            add_rect(slide, col, ry, Cm(0.2), row_h - Cm(0.1), cor_borda)
            cat  = dev.get("classe","")
            desp = dev.get("desvio_pp", 0)
            val  = pat * abs(desp) / 100 if pat else 0
            add_text(slide, CLS_LABEL.get(cat, cat), col + Cm(0.5), ry + Cm(0.1),
                     col_w - Cm(2.5), Cm(0.6), size=11, bold=True, color=C_WHITE)
            add_text(slide, f"{desp:+.1f}%", col + col_w - Cm(1.5), ry + Cm(0.1),
                     Cm(1.3), Cm(0.6), size=11, bold=True, color=cor_borda,
                     align=PP_ALIGN.RIGHT)
            add_text(slide, f"Atual: {dev.get('atual',0):.1f}%  ·  Modelo: {dev.get('modelo',0):.1f}%  ·  {fmt(val)}",
                     col + Cm(0.5), ry + Cm(0.75), col_w - Cm(0.8), Cm(0.5),
                     size=8.5, color=C_LGRAY)


# ── SLIDE 5: SUGESTÕES ────────────────────────────────────────────────────────
def slide_sugestoes(prs, d):
    sugs = d.get("sugestoes_produtos", [])
    if not sugs:
        return

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(slide)
    add_header(slide, "SUGESTÕES DE REALOCAÇÃO",
               "Produtos recomendados pelo Head de Produtos")
    add_footer(slide, d.get("nome_cliente",""), d.get("data_ref",""))

    n  = min(len(sugs), 4)
    cw = (SW - Cm(1.4)) / n - Cm(0.3)
    top_y = Cm(3.2)
    card_h = SH - top_y - Cm(1.0)

    for i, s in enumerate(sugs[:4]):
        p    = s.get("produto", {})
        cx   = Cm(0.7) + i * (cw + Cm(0.3))
        cls  = s.get("classe","")
        cor  = CLS_COR.get(cls, C_LGRAY)

        add_rect(slide, cx, top_y, cw, card_h, C_CARD, cor, 0.5)
        # Topo colorido
        add_rect(slide, cx, top_y, cw, Cm(0.2), cor)

        # Badge classe
        add_rect(slide, cx + Cm(0.3), top_y + Cm(0.35), Cm(3.5), Cm(0.55), C_CARD2)
        add_text(slide, s.get("label_classe", cls), cx + Cm(0.4), top_y + Cm(0.38),
                 Cm(3.3), Cm(0.48), size=7.5, bold=True, color=cor)

        # Gap
        gap = s.get("gap", 0)
        cor_g = C_RED if gap < 0 else C_GREEN
        add_text(slide, f"Gap {gap:+.1f}%", cx + cw - Cm(2), top_y + Cm(0.38),
                 Cm(1.8), Cm(0.48), size=8, bold=True, color=cor_g, align=PP_ALIGN.RIGHT)

        # Nome do produto
        nome_p = p.get("nome", "—")
        add_text(slide, nome_p, cx + Cm(0.3), top_y + Cm(1.05),
                 cw - Cm(0.6), Cm(1.4), size=12, bold=True, color=C_WHITE, wrap=True)

        # Linha divisória
        add_rect(slide, cx + Cm(0.3), top_y + Cm(2.6), cw - Cm(0.6), Cm(0.03), C_GRAY)

        # Taxa
        if p.get("taxa"):
            add_text(slide, p["taxa"], cx + Cm(0.3), top_y + Cm(2.75),
                     cw - Cm(0.6), Cm(0.6), size=13, bold=True, color=C_GREEN)

        # Emissor
        if p.get("emissor"):
            add_text(slide, p["emissor"], cx + Cm(0.3), top_y + Cm(3.4),
                     cw - Cm(0.6), Cm(0.5), size=9, color=C_LGRAY)

        # Vencimento
        if p.get("vencimento"):
            add_text(slide, f"Venc: {p['vencimento']}", cx + Cm(0.3), top_y + Cm(3.95),
                     cw - Cm(0.6), Cm(0.5), size=8.5, color=C_GRAY)

        # Linha
        add_rect(slide, cx + Cm(0.3), top_y + Cm(4.5), cw - Cm(0.6), Cm(0.03), C_GRAY)

        # Motivo
        if p.get("motivo"):
            add_text(slide, p["motivo"], cx + Cm(0.3), top_y + Cm(4.65),
                     cw - Cm(0.6), Cm(2.5), size=8.5, color=C_LGRAY, wrap=True)

        # Indicado por
        if p.get("indicado_por"):
            add_text(slide, f"Indicado por: {p['indicado_por']}", cx + Cm(0.3),
                     top_y + card_h - Cm(0.9), cw - Cm(0.6), Cm(0.6),
                     size=7.5, color=C_GRAY, italic=True)


# ── SLIDE 6: PRÓXIMOS PASSOS ──────────────────────────────────────────────────
def slide_proximos(prs, d, ia_passos=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide_bg(slide)
    add_header(slide, "PRÓXIMOS PASSOS", "Encaminhamentos acordados na reunião")
    add_footer(slide, d.get("nome_cliente",""), d.get("data_ref",""))

    passos_default = [
        "Assinar a proposta de realocação apresentada hoje",
        "Agendar revisão de carteira em 60 dias",
        "Verificar documentação para Open Investments (OPIN)",
        "Enviar simulação de IR para ativos a serem resgatados",
    ]
    if ia_passos:
        passos = [l.strip("•- ") for l in ia_passos.split("\n") if l.strip()]
    else:
        passos = passos_default

    row_h = Cm(2.0)
    start_y = Cm(3.5)
    for i, passo in enumerate(passos[:5]):
        ry = start_y + i * row_h
        add_rect(slide, Cm(0.7), ry, SW - Cm(1.4), row_h - Cm(0.15), C_CARD, C_CARD2, 0.3)
        # Número
        add_rect(slide, Cm(0.7), ry, Cm(1.5), row_h - Cm(0.15), C_GOLD)
        add_text(slide, f"0{i+1}", Cm(0.7), ry + Cm(0.5), Cm(1.5), Cm(0.9),
                 size=14, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
        add_text(slide, passo, Cm(2.5), ry + Cm(0.55), SW - Cm(3.5), Cm(0.9),
                 size=12, color=C_WHITE)

    # Assinatura
    add_rect(slide, Cm(0.7), SH - Cm(1.9), Cm(8), Cm(0.03), C_GRAY)
    add_text(slide, d.get("assessor", "Assessor Braúna"), Cm(0.7), SH - Cm(1.8),
             Cm(8), Cm(0.6), size=10, color=C_LGRAY)
    add_text(slide, "Assessor de Investimentos — Braúna Investimentos", Cm(0.7),
             SH - Cm(1.25), Cm(10), Cm(0.5), size=7.5, color=C_GRAY)


# ── GERADOR PRINCIPAL ─────────────────────────────────────────────────────────
def gerar_apresentacao_pptx(d: dict) -> bytes:
    """Gera arquivo PPTX com identidade Braúna, pronto para apresentação ao cliente."""
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    ia_passos = d.get("ia_proximos_passos", "")

    # Slide 1: Capa
    slide_capa(prs, d)

    # Slide 2: Cenário Macro (se disponível)
    if d.get("cenario_macro"):
        slide_cenario(prs, d)

    # Slide 3: Análise da Carteira
    slide_carteira(prs, d)

    # Slide 4: Desvios (se houver)
    if d.get("desvios"):
        slide_desvios(prs, d)

    # Slide 5: Sugestões de Realocação (se houver)
    if d.get("sugestoes_produtos"):
        slide_sugestoes(prs, d)

    # Slide 6: Próximos Passos
    slide_proximos(prs, d, ia_passos)

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()
