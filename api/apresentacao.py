"""
Gerador de Apresentação de Reunião — Braúna Investimentos
Fontes maiores · Identidade visual Braúna · Slides dinâmicos por cliente
"""
import io, os, json, textwrap, math
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color

# ── Paleta Braúna ─────────────────────────────────────────────────────────────
BG     = HexColor("#0A0A08")   # fundo principal
CARD1  = HexColor("#111110")   # card primário
CARD2  = HexColor("#181812")   # card secundário
CARD3  = HexColor("#1E1E16")   # card terciário
GOLD   = HexColor("#D6B27A")   # dourado principal
GOLD2  = HexColor("#E8C96B")   # dourado claro
GOLD3  = HexColor("#C09A5A")   # dourado escuro
GREEN  = HexColor("#5DCAA5")   # positivo / ok
RED    = HexColor("#FF6B6B")   # negativo / alerta
AMBER  = HexColor("#F0A830")   # atenção
BLUE   = HexColor("#7DCFEF")   # FIIs / info
PURPLE = HexColor("#B08FCF")   # multimercado
TEAL   = HexColor("#4EC9B0")   # alternativos
WHITE  = HexColor("#F0F0F0")
LGRAY  = HexColor("#888880")
GRAY   = HexColor("#3A3A34")
DGRAY  = HexColor("#252520")
BLACK  = HexColor("#0A0A08")

# Landscape A4: 297 × 210 mm
W, H = A4[1], A4[0]

# Cor por classe de ativo
CLS_COR = {
    "pos_fixado":   GOLD,
    "inflacao":     AMBER,
    "pre_fixado":   HexColor("#F07850"),
    "acoes":        GREEN,
    "fiis":         BLUE,
    "multimercado": PURPLE,
    "alternativos": TEAL,
    "internacional":HexColor("#5B9BD5"),
    "criptomoedas": LGRAY,
}
CLS_LABEL = {
    "pos_fixado": "Pós Fixado", "inflacao": "Inflação", "pre_fixado": "Pré Fixado",
    "acoes": "Ações", "fiis": "FIIs", "multimercado": "Multimercado",
    "alternativos": "Alternativos", "internacional": "Internacional",
    "criptomoedas": "Criptomoedas",
}

# ── Primitivas de desenho ─────────────────────────────────────────────────────
def bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

def rect_fill(c, x, y, w, h, color, radius=4):
    c.setFillColor(color)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=1, stroke=0)
    else:
        c.rect(x, y, w, h, fill=1, stroke=0)

def rect_border(c, x, y, w, h, color, lw=0.7, radius=4):
    c.setStrokeColor(color)
    c.setLineWidth(lw)
    if radius:
        c.roundRect(x, y, w, h, radius, fill=0, stroke=1)
    else:
        c.rect(x, y, w, h, fill=0, stroke=1)

def card(c, x, y, w, h, fill=None, border=None, radius=5):
    rect_fill(c, x, y, w, h, fill or CARD1, radius)
    if border:
        rect_border(c, x, y, w, h, border, radius=radius)

def line(c, x1, y1, x2, color=None, lw=0.5):
    c.setStrokeColor(color or GRAY)
    c.setLineWidth(lw)
    c.line(x1, y1, x2, y1)

def vline(c, x, y1, y2, color=None, lw=0.5):
    c.setStrokeColor(color or GRAY)
    c.setLineWidth(lw)
    c.line(x, y1, x, y2)

def txt(c, t, x, y, size=11, color=None, bold=False, align="left", max_w=None):
    if t is None: return 0
    t = str(t)
    if not t: return 0
    if max_w:
        chars = max(1, int(max_w / (size * 0.52)))
        lines = []
        for para in t.split("\n"):
            wrapped = textwrap.wrap(para, chars) or [""]
            lines.extend(wrapped)
        lh = size * 1.45
        for i, ln in enumerate(lines):
            _txt(c, ln, x, y - i * lh, size, color, bold, align)
        return len(lines)
    _txt(c, t, x, y, size, color, bold, align)
    return 1

def _txt(c, t, x, y, size, color, bold, align):
    c.setFillColor(color or WHITE)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    if align == "center": c.drawCentredString(x, y, t)
    elif align == "right": c.drawRightString(x, y, t)
    else: c.drawString(x, y, t)

def bar(c, x, y, w, h, pct, fill_color, bg_color=None):
    rect_fill(c, x, y, w, h, bg_color or DGRAY, 2)
    bw = max(0, min(w * pct / 100, w))
    if bw > 0:
        rect_fill(c, x, y, bw, h, fill_color, 2)

def dot(c, x, y, r, color):
    c.setFillColor(color)
    c.circle(x, y, r, fill=1, stroke=0)

def badge(c, x, y, label, bg_color, text_color=None, size=8):
    tw = len(label) * size * 0.62 + 10
    rect_fill(c, x, y - 3*mm, tw, 5.5*mm, bg_color, 2.5*mm)
    _txt(c, label, x + tw/2, y, size, text_color or BLACK, True, "center")
    return tw

# ── Header / Footer ───────────────────────────────────────────────────────────
_TOTAL_SLIDES = 0   # será definido antes de renderizar

def header(c, titulo, sub="", pg=1, total=1):
    # Faixa superior
    rect_fill(c, 0, H - 18*mm, W, 18*mm, CARD1, 0)
    c.setFillColor(GOLD); c.rect(0, H - 18*mm, W, 0.8, fill=1, stroke=0)
    # Logo
    txt(c, "BRAÚNA", 8*mm, H - 6.5*mm, 10, GOLD, bold=True)
    txt(c, "INVESTIMENTOS", 8*mm, H - 12.5*mm, 6.5, LGRAY)
    vline(c, 42*mm, H - 17*mm, H - 1*mm, GRAY)
    # Título central
    txt(c, titulo, W/2, H - 7*mm, 14, WHITE, bold=True, align="center")
    if sub:
        txt(c, sub, W/2, H - 13.5*mm, 8, LGRAY, align="center")
    # Página
    txt(c, f"{pg} / {total}", W - 8*mm, H - 10*mm, 9, GRAY, align="right")

def footer(c, nome, data):
    rect_fill(c, 0, 0, W, 10*mm, CARD1, 0)
    c.setFillColor(GOLD); c.rect(0, 10*mm, W, 0.5, fill=1, stroke=0)
    aviso = "Material informativo — não constitui oferta de valores mobiliários."
    txt(c, f"Braúna Investimentos  ·  {nome}  ·  {data}  ·  {aviso}",
        W/2, 3.8*mm, 6.5, GRAY, align="center")

def section_title(c, t, x, y, color=None):
    c.setFillColor(color or GOLD)
    c.rect(x, y - 0.3*mm, 3, 5*mm, fill=1, stroke=0)
    txt(c, t, x + 5*mm, y + 3*mm, 9, color or GOLD, bold=True)
    return y - 2*mm

# ── Área útil ─────────────────────────────────────────────────────────────────
def area():
    """Retorna (x_inicio, y_topo, largura, altura) da área útil."""
    return 8*mm, H - 22*mm, W - 16*mm, H - 32*mm

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 1 — CAPA
# ══════════════════════════════════════════════════════════════════════════════
def slide_capa(c, d, ia, pg, total):
    bg(c)
    # Barra lateral dourada
    rect_fill(c, 0, 0, 2*mm, H, GOLD, 0)
    rect_fill(c, 0, 0, 78*mm, H, CARD1, 0)
    c.setFillColor(GOLD); c.rect(78*mm, 0, 1, H, fill=1, stroke=0)

    # Logo lado esquerdo
    txt(c, "BRAÚNA", 10*mm, H - 22*mm, 32, GOLD, bold=True)
    txt(c, "INVESTIMENTOS", 11*mm, H - 31*mm, 10, LGRAY)
    line(c, 10*mm, H - 35*mm, 72*mm, GOLD3, 0.8)
    txt(c, "APRESENTAÇÃO DE", 10*mm, H - 44*mm, 10, LGRAY)
    txt(c, "CARTEIRA", 10*mm, H - 54*mm, 10, LGRAY)
    txt(c, d.get("data_ref",""), 10*mm, H/2 - 8*mm, 9.5, GRAY)

    # Conteúdo direito
    cx = 86*mm
    txt(c, "ANÁLISE DE", cx, H - 22*mm, 10, LGRAY)
    txt(c, d.get("nome_cliente","Cliente"), cx, H - 38*mm, 26, WHITE, bold=True)
    txt(c, f"Conta XP  {d.get('conta','—')}",  cx, H - 49*mm, 10.5, LGRAY)
    line(c, cx, H - 53*mm, W - 8*mm, GRAY, 0.5)

    # KPIs
    kpis = [
        ("Patrimônio Total", f"R$ {d.get('patrimonio',0):,.0f}".replace(",",".")),
        ("Perfil",           d.get("perfil","—").capitalize()),
        ("Rent. 12M",        f"{d.get('rent_12m',0):.2f}%"),
        ("vs CDI 12M",       f"{d.get('pct_cdi',0):.0f}% do CDI"),
    ]
    kw = (W - cx - 12*mm) / 4 - 3*mm
    for i, (lbl, val) in enumerate(kpis):
        kx = cx + i * (kw + 3*mm)
        ky = H - 54*mm
        card(c, kx, ky - 22*mm, kw, 20*mm, CARD2, GRAY)
        txt(c, lbl, kx + 3*mm, ky - 6*mm, 7.5, LGRAY)
        txt(c, val, kx + 3*mm, ky - 16*mm, 13, GOLD, bold=True)

    # Resumo IA
    if ia.get("resumo_exec"):
        card(c, cx, H/2 - 34*mm, W - cx - 8*mm, 22*mm, CARD3, GOLD3)
        txt(c, "VISÃO DO ASSESSOR", cx + 4*mm, H/2 - 16*mm, 7, GOLD3, bold=True)
        txt(c, ia["resumo_exec"], cx + 4*mm, H/2 - 24*mm, 9, LGRAY,
            max_w=W - cx - 14*mm)

    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 2 — EVOLUÇÃO PATRIMONIAL
# ══════════════════════════════════════════════════════════════════════════════
def slide_patrimonio(c, d, ia, pg, total):
    bg(c)
    header(c, "EVOLUÇÃO PATRIMONIAL", "Histórico completo · Referência XPerformance XP", pg, total)
    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

    rent = d.get("rent", {})
    port = rent.get("portfolio", {}) if isinstance(rent, dict) else {}
    cdi  = rent.get("cdi", {}) if isinstance(rent, dict) else {}

    # Cards rentabilidade
    periodos = [("Mês", "mes"), ("Ano", "ano"), ("12 Meses", "12m"), ("24 Meses", "24m")]
    cw = (W - 16*mm) / 4 - 2*mm
    for i, (label, key) in enumerate(periodos):
        rp = port.get(key, 0); rc = cdi.get(key, 0)
        kx = 8*mm + i * (cw + 2.5*mm)
        cor = GREEN if rp >= rc else AMBER
        pct_cdi = round(rp / rc * 100) if rc else 0
        card(c, kx, H - 64*mm, cw, 40*mm, CARD1, GRAY)
        # Accent top bar
        c.setFillColor(cor); c.rect(kx, H - 25*mm, cw, 2, fill=1, stroke=0)
        txt(c, label, kx + 4*mm, H - 28*mm, 8.5, LGRAY)
        txt(c, f"{rp:.2f}%", kx + 4*mm, H - 40*mm, 22, cor, bold=True)
        txt(c, f"CDI: {rc:.2f}%", kx + 4*mm, H - 50*mm, 9, GRAY)
        cor_pct = GREEN if pct_cdi >= 100 else AMBER
        txt(c, f"{pct_cdi:.0f}% do CDI", kx + 4*mm, H - 59*mm, 10, cor_pct, bold=True)

    # Estatísticas históricas
    est = d.get("estatisticas", {})
    ay = H - 72*mm
    section_title(c, "ESTATÍSTICAS HISTÓRICAS — ÚLTIMOS 24 MESES", 8*mm, ay)
    card(c, 8*mm, ay - 34*mm, W - 16*mm, 32*mm, CARD2, GRAY)

    stats = [
        ("Meses positivos",      f"{est.get('meses_positivos',0)} de {est.get('meses_positivos',0)+est.get('meses_negativos',0)}", GREEN),
        ("Retorno máximo mensal",f"+{est.get('retorno_max_mensal',0):.2f}%", GREEN),
        ("Meses acima do CDI",   f"{est.get('meses_acima_cdi',0)}", GREEN),
        ("Volatilidade 12M",     f"{est.get('volatilidade_12m',0):.2f}%", AMBER),
        ("Meses negativos",      f"{est.get('meses_negativos',0)}", RED),
        ("Retorno mínimo mensal",f"{est.get('retorno_min_mensal',0):.2f}%", RED),
        ("Meses abaixo do CDI",  f"{est.get('meses_abaixo_cdi',0)}", LGRAY),
        ("Volatilidade 24M",     f"{est.get('volatilidade_24m',0):.2f}%", AMBER),
    ]
    sw = (W - 20*mm) / 4
    for i, (lbl, val, cor) in enumerate(stats):
        col = i % 4; row = i // 4
        sx = 10*mm + col * sw
        sy = ay - 14*mm - row * 14*mm
        txt(c, lbl, sx, sy, 8, LGRAY)
        txt(c, val, sx, sy - 8*mm, 12, cor, bold=True)

    # Tabela histórica mensal
    hist = d.get("historico_mensal", {})
    if hist:
        hy = ay - 42*mm
        section_title(c, "RENTABILIDADE HISTÓRICA POR ANO", 8*mm, hy)
        meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez","Ano"]
        col_w = (W - 30*mm) / 13
        # Cabeçalho
        txt(c, "Ano", 10*mm, hy - 10*mm, 8.5, LGRAY, bold=True)
        for j, m in enumerate(meses):
            txt(c, m, 26*mm + j * col_w + col_w/2, hy - 10*mm, 8, LGRAY, bold=True, align="center")
        line(c, 8*mm, hy - 12*mm, W - 8*mm, GRAY)

        for ri, (ano, mdata) in enumerate(sorted(hist.items(), reverse=True)):
            ry = hy - 20*mm - ri * 12*mm
            bg_c = CARD1 if ri % 2 == 0 else CARD2
            rect_fill(c, 8*mm, ry - 8*mm, W - 16*mm, 12*mm, bg_c, 0)
            txt(c, str(ano), 10*mm, ry, 10, GOLD, bold=True)
            vals = mdata.get("meses", [None]*12) + [mdata.get("ano", None)]
            for j, v in enumerate(vals):
                cx2 = 26*mm + j * col_w + col_w/2
                if v is not None:
                    txt(c, f"{v:+.1f}%", cx2, ry, 9, GREEN if v >= 0 else RED, align="center")
                else:
                    txt(c, "—", cx2, ry, 8, GRAY, align="center")

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 3 — CARTEIRA vs. MODELO
# ══════════════════════════════════════════════════════════════════════════════
def slide_comparativo(c, d, ia, pg, total):
    bg(c)
    header(c, "CARTEIRA ATUAL vs. MODELO IDEAL",
           f"Modelo Levante Asset  ·  Perfil {d.get('perfil','').capitalize()}", pg, total)
    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

    desvios   = d.get("desvios", [])
    rent_cls  = d.get("rent_por_classe", {})
    STATUS    = {"ok": ("OK", GREEN), "atencao": ("!", AMBER), "fora": ("✕", RED)}

    # Cabeçalho da tabela
    cols = [("CLASSE",8),("ATUAL",63),("META",80),("DESVIO",96),
            ("MÊS",116),("ANO",130),("12M",145),("BARRA ATUAL vs META",162)]
    for lbl, px in cols:
        txt(c, lbl, px*mm, H - 23*mm, 7.5, LGRAY, bold=True)
    line(c, 8*mm, H - 25*mm, W - 8*mm, GOLD3, 0.7)

    row_h = 14.5*mm
    for i, dv in enumerate(desvios[:9]):
        ry   = H - 29*mm - i * row_h
        bg_c = CARD1 if i % 2 == 0 else CARD2
        rect_fill(c, 7*mm, ry - 9.5*mm, W - 14*mm, row_h - 1*mm, bg_c, 0)

        cls  = dv.get("cls","")
        cor_cls = CLS_COR.get(cls, LGRAY)
        st   = dv.get("status","ok")
        ic, sc = STATUS.get(st, ("?", LGRAY))
        r    = rent_cls.get(cls, {})
        dev  = dv.get("desvio", 0)
        atual= dv.get("atual", 0)
        alvo = dv.get("alvo", 0)

        # Dot de cor da classe
        dot(c, 10.5*mm, ry - 1*mm, 2*mm, cor_cls)
        # Nome da classe
        bold_cls = st == "fora"
        txt(c, dv.get("label",""), 14*mm, ry - 0.5*mm, 10, WHITE, bold=bold_cls)
        # Valores
        txt(c, f"{atual:.1f}%", 63*mm, ry - 0.5*mm, 11, GOLD, bold=True)
        txt(c, f"{alvo:.1f}%",  80*mm, ry - 0.5*mm, 10, LGRAY)
        cor_dev = RED if abs(dev) > 3 else (AMBER if abs(dev) > 1.5 else GREEN)
        txt(c, f"{dev:+.1f}%", 96*mm, ry - 0.5*mm, 11, cor_dev, bold=True)
        # Rentabilidade por classe
        for val, px in [(r.get("mes",0),116),(r.get("ano",0),130),(r.get("12m",0),145)]:
            txt(c, f"{val:+.1f}%", px*mm, ry - 0.5*mm, 9.5, GREEN if val >= 0 else RED)
        # Barra visual dupla
        bx, bw = 162*mm, W - 170*mm
        bar(c, bx, ry - 5*mm, bw, 4*mm, 100, DGRAY)
        if alvo > 0:
            bar(c, bx, ry - 5*mm, bw, 4*mm, min(alvo / 60 * 100, 100), GRAY)
        if atual > 0:
            bar(c, bx, ry - 5*mm, bw, 4*mm, min(atual / 60 * 100, 100), sc)
        # Badge status
        badge(c, W - 17*mm, ry - 0.5*mm, ic, sc, BLACK, 8)

    # Diagnóstico IA
    if ia.get("diagnostico"):
        card(c, 7*mm, 11*mm, W - 14*mm, 16*mm, CARD3, GOLD3)
        txt(c, "DIAGNÓSTICO", 12*mm, 23.5*mm, 7.5, GOLD3, bold=True)
        txt(c, ia["diagnostico"], 12*mm, 17*mm, 9, LGRAY, max_w=W - 22*mm)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE 4+ — POSIÇÃO DETALHADA (dinâmico por classe)
# ══════════════════════════════════════════════════════════════════════════════
def slide_posicao_classe(c, d, ia, pg, total, cls_key, ativos):
    """Slide de posição detalhada para uma classe de ativos de renda fixa/outros."""
    cor_cls = CLS_COR.get(cls_key, LGRAY)
    label_cls = CLS_LABEL.get(cls_key, cls_key)
    bg(c)
    header(c, f"POSIÇÃO DETALHADA — {label_cls.upper()}",
           "Rentabilidade marcada a mercado · XPerformance XP", pg, total)
    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

    # Resumo da classe
    total_cls = sum(a.get("saldo",0) for a in ativos)
    rent_cls  = d.get("rent_por_classe",{}).get(cls_key, {})
    comp_cls  = d.get("composicao",{}).get(cls_key, 0)

    # KPIs da classe — faixa horizontal compacta no topo
    kpis_cls = [
        ("Saldo Total",   f"R$ {total_cls:,.0f}".replace(",",".")),
        ("% da Carteira", f"{comp_cls:.1f}%"),
        ("Rent. Mês",     f"{rent_cls.get('mes',0):+.2f}%"),
        ("Rent. Ano",     f"{rent_cls.get('ano',0):+.2f}%"),
        ("Rent. 12M",     f"{rent_cls.get('12m',0):+.2f}%"),
        ("Rent. 24M",     f"{rent_cls.get('24m',0):+.2f}%"),
    ]
    kw = (W - 16*mm) / 6 - 2*mm
    for i, (lbl, val) in enumerate(kpis_cls):
        kx = 8*mm + i * (kw + 2.5*mm)
        card(c, kx, H - 46*mm, kw, 22*mm, CARD1, cor_cls)
        c.setFillColor(cor_cls); c.rect(kx, H - 25*mm, kw, 2, fill=1, stroke=0)
        txt(c, lbl, kx + 3*mm, H - 28*mm, 7.5, LGRAY)
        # Cor do valor: verde/vermelho para rentabilidade, dourado para resto
        if i >= 2:
            v_num = rent_cls.get(["mes","ano","12m","24m"][i-2], 0)
            cor_v = GREEN if v_num >= 0 else RED
        else:
            cor_v = cor_cls
        txt(c, val, kx + 3*mm, H - 39*mm, 13, cor_v, bold=True)

    # Tabela de ativos
    ay = H - 53*mm
    # Colunas: nome longo ocupa até 100mm, depois saldo/alloc/rentab (sem 12M — dado indisponível por ativo)
    cols = [("ATIVO / PRODUTO", 8), ("SALDO", 108), ("% ALLOC", 130),
            ("MÊS", 150), ("%CDI", 167), ("ANO", 183), ("24M", 200)]
    for lbl, px in cols:
        txt(c, lbl, px*mm, ay, 7.5, LGRAY, bold=True)
    line(c, 8*mm, ay - 2*mm, W - 8*mm, cor_cls, 0.7)

    row_h = 11*mm
    for i, a in enumerate(ativos):
        ry   = ay - 5*mm - i * row_h
        bg_c = CARD1 if i % 2 == 0 else CARD2
        rect_fill(c, 7*mm, ry - 7*mm, W - 14*mm, row_h - 0.5*mm, bg_c, 0)

        saldo = a.get("saldo",0)
        perc  = a.get("perc",0)
        nome  = a.get("nome", a.get("ticker","—"))

        # Nome do ativo
        txt(c, nome, 9*mm, ry, 9, WHITE)
        if a.get("indexador"):
            txt(c, a["indexador"], 9*mm, ry - 5.5*mm, 7, LGRAY)

        txt(c, f"R$ {saldo:,.0f}".replace(",","."), 108*mm, ry, 10, WHITE, bold=True)
        txt(c, f"{perc:.2f}%", 130*mm, ry, 9.5, GOLD)

        for val, px, use_cdi in [
            (a.get("rent_mes",0), 150, False),
            (a.get("pct_cdi_mes", a.get("rent_mes",0)/1.07*100 if a.get("rent_mes") else 0), 167, True),
            (a.get("rent_ano",0), 183, False),
            (a.get("rent_24m",0), 200, False),
        ]:
            cor_v = GREEN if val >= 0 else RED
            if use_cdi: cor_v = GREEN if val >= 100 else AMBER
            suf = "%" if not use_cdi else "%"
            lbl_v = f"{val:+.1f}%" if not use_cdi else f"{val:.0f}%"
            txt(c, lbl_v, px*mm, ry, 9, cor_v)

    # Barra de alocação relativa
    if ativos:
        bx, by = 8*mm, ay - 5*mm - len(ativos)*row_h - 8*mm
        if by > 14*mm:
            txt(c, "PESO RELATIVO NA CLASSE", 8*mm, by + 4*mm, 7.5, LGRAY, bold=True)
            bw_total = W - 16*mm
            x_cur = 8*mm
            for a in ativos:
                w_bar = bw_total * a.get("perc",0) / max(comp_cls, 1)
                if w_bar > 1:
                    rect_fill(c, x_cur, by - 6*mm, w_bar - 0.5, 5*mm, cor_cls, 0)
                    if w_bar > 12*mm:
                        txt(c, a.get("ticker", a.get("nome",""))[:8],
                            x_cur + w_bar/2, by, 6.5, BLACK, align="center")
                x_cur += w_bar

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE — RENDA VARIÁVEL (AÇÕES + FIIs)
# ══════════════════════════════════════════════════════════════════════════════
def slide_rv(c, d, ia, pg, total):
    bg(c)
    header(c, "RENDA VARIÁVEL — AÇÕES & FIIs",
           "Posição detalhada · Referência XP", pg, total)
    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

    acoes = d.get("acoes", [])
    fiis  = d.get("fiis", [])

    # ── Layout: Ações à esquerda, FIIs à direita, separador central ──
    SEP   = 148*mm          # separador vertical
    ax    = 8*mm
    aw    = SEP - ax - 4*mm # largura da área de ações  ≈ 136mm
    fx    = SEP + 4*mm      # início FIIs               ≈ 152mm
    fw    = W - fx - 8*mm   # largura FIIs               ≈ 137mm

    # ── Cabeçalho Ações ──
    section_title(c, f"AÇÕES  ({len(acoes)} ativos)", ax, H - 24*mm, GREEN)
    line(c, ax, H - 27*mm, ax + aw, GREEN, 0.6)
    # Colunas: Ticker | Qtd | Saldo | % | Mês | Ano | 12M
    a_cols = [("Ticker",0),("Qtd.",32),("Saldo",55),("% Cart.",86),
              ("Mês",105),("Ano",117),("24M",129)]
    for lbl, px in a_cols:
        txt(c, lbl, ax + px*mm, H - 31*mm, 7.5, LGRAY, bold=True)

    row_h = 11.5*mm
    for i, a in enumerate(acoes[:12]):
        ry   = H - 36*mm - i * row_h
        bg_c = CARD1 if i % 2 == 0 else CARD2
        rect_fill(c, ax, ry - 8*mm, aw, row_h - 0.5*mm, bg_c, 0)
        txt(c, a.get("ticker",""), ax + 1*mm, ry, 12, GREEN, bold=True)
        txt(c, str(a.get("qtd","—")),                  ax + 32*mm, ry, 9, LGRAY)
        txt(c, f"R$ {a.get('saldo',0):,.0f}".replace(",","."), ax + 55*mm, ry, 9.5, WHITE)
        txt(c, f"{a.get('perc',0):.2f}%",              ax + 86*mm, ry, 9.5, WHITE)
        for val, px in [(a.get("rent_mes",0),105),(a.get("rent_ano",0),117),(a.get("rent_24m",0),129)]:
            txt(c, f"{val:+.1f}%", ax + px*mm, ry, 9, GREEN if val >= 0 else RED)

    # ── Separador vertical ──
    vline(c, SEP, H - 22*mm, 12*mm, GRAY, 0.6)

    # ── Cabeçalho FIIs ──
    section_title(c, f"FIIs  ({len(fiis)} ativos)", fx, H - 24*mm, BLUE)
    line(c, fx, H - 27*mm, fx + fw, BLUE, 0.6)
    # Colunas: Ticker | Qtd | Saldo | % | Mês | Ano | 12M | 24M
    # fw ≈ 137mm — colunas ajustadas para caber sem corte
    f_cols = [("Ticker",0),("Qtd.",26),("Saldo",47),("% Cart.",78),
              ("Mês",98),("Ano",110),("24M",122)]
    for lbl, px in f_cols:
        txt(c, lbl, fx + px*mm, H - 31*mm, 7.5, LGRAY, bold=True)

    for i, f in enumerate(fiis[:12]):
        ry   = H - 36*mm - i * row_h
        bg_c = CARD1 if i % 2 == 0 else CARD2
        rect_fill(c, fx, ry - 8*mm, fw, row_h - 0.5*mm, bg_c, 0)
        txt(c, f.get("ticker",""), fx + 1*mm, ry, 12, BLUE, bold=True)
        txt(c, str(f.get("qtd","—")),                  fx + 26*mm, ry, 9, LGRAY)
        txt(c, f"R$ {f.get('saldo',0):,.0f}".replace(",","."), fx + 47*mm, ry, 9.5, WHITE)
        txt(c, f"{f.get('perc',0):.2f}%",              fx + 78*mm, ry, 9.5, WHITE)
        for val, px in [(f.get("rent_mes",0),98),(f.get("rent_ano",0),110),
                        (f.get("rent_24m",0),122)]:
            txt(c, f"{val:+.1f}%", fx + px*mm, ry, 9, GREEN if val >= 0 else RED)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE — CENÁRIO MACRO
# ══════════════════════════════════════════════════════════════════════════════
def slide_cenario(c, d, ia, pg, total):
    bg(c)
    header(c, "CENÁRIO MACRO", "Visão Head de Produtos — Levante Asset", pg, total)
    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

    cenario = d.get("cenario_macro", {})
    vieses  = cenario.get("vieses", {})
    VCOR    = {"positivo": GREEN, "neutro": AMBER, "negativo": RED}
    VIC     = {"positivo": "▲", "neutro": "→", "negativo": "▼"}

    half_w = (W - 18*mm) / 2
    ay = H - 24*mm

    # Bloco Global
    section_title(c, "CENÁRIO GLOBAL", 8*mm, ay)
    card(c, 8*mm, ay - 52*mm, half_w, 50*mm, CARD1, GRAY)
    txt(c, cenario.get("global","—"), 12*mm, ay - 8*mm, 9.5, LGRAY,
        max_w=half_w - 6*mm)

    # Bloco Posicionamento
    px2 = 12*mm + half_w
    section_title(c, "POSICIONAMENTO HP", px2, ay, GOLD)
    card(c, px2, ay - 52*mm, half_w, 50*mm, CARD2, GOLD3)
    txt(c, cenario.get("posicionamento","—"), px2 + 4*mm, ay - 8*mm, 9.5, LGRAY,
        max_w=half_w - 6*mm)

    # Bloco Brasil
    by2 = ay - 58*mm
    section_title(c, "BRASIL", 8*mm, by2)
    card(c, 8*mm, by2 - 44*mm, half_w, 42*mm, CARD1, GRAY)
    txt(c, cenario.get("brasil","—"), 12*mm, by2 - 8*mm, 9.5, LGRAY,
        max_w=half_w - 6*mm)

    # Bloco Vieses
    section_title(c, "VIESES POR CLASSE", px2, by2, GOLD)
    card(c, px2, by2 - 44*mm, half_w, 42*mm, CARD2, GRAY)
    items = list(vieses.items())
    col_count = 2
    per_col = math.ceil(len(items) / col_count)
    for i, (cls, v) in enumerate(items):
        col = i // per_col; row = i % per_col
        vx  = px2 + 4*mm + col * (half_w / 2)
        vy  = by2 - 14*mm - row * 10*mm
        cor = VCOR.get(v, GRAY)
        ic  = VIC.get(v, "→")
        dot(c, vx + 2*mm, vy + 1*mm, 1.5*mm, cor)
        txt(c, CLS_LABEL.get(cls, cls), vx + 6*mm, vy, 9.5, WHITE)
        txt(c, ic, vx + 6*mm + len(CLS_LABEL.get(cls,cls))*5.5, vy, 10, cor, bold=True)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE — SUGESTÕES DE REALOCAÇÃO
# ══════════════════════════════════════════════════════════════════════════════
def slide_sugestoes(c, d, ia, pg, total):
    bg(c)
    header(c, "SUGESTÕES DE REALOCAÇÃO",
           "Produtos recomendados pelo Head de Produtos", pg, total)
    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

    sugs = d.get("sugestoes_produtos", [])
    if not sugs:
        txt(c, "Nenhum produto cadastrado pelo Head de Produtos.", W/2, H/2, 14, LGRAY, align="center")
        return

    # Narrativa IA
    if ia.get("narrativa_sug"):
        card(c, 7*mm, H - 36*mm, W - 14*mm, 13*mm, CARD3, GOLD3)
        txt(c, ia["narrativa_sug"], 12*mm, H - 25*mm, 9.5, LGRAY, max_w=W - 22*mm)

    n     = min(len(sugs), 4)
    cw_s  = (W - 16*mm) / n - 3*mm
    top_y = H - 40*mm

    for i, s in enumerate(sugs[:4]):
        p    = s.get("produto", {})
        cx_s = 8*mm + i * (cw_s + 4*mm)
        cls  = s.get("classe","")
        cor_s= CLS_COR.get(cls, LGRAY)
        card_h = top_y - 14*mm

        card(c, cx_s, 14*mm, cw_s, card_h, CARD1, cor_s)
        # Top accent
        c.setFillColor(cor_s); c.rect(cx_s, 14*mm + card_h - 2, cw_s, 2, fill=1, stroke=0)

        # Badge classe + gap
        bw = badge(c, cx_s + 3*mm, top_y - 5*mm, s.get("label_classe",""), CARD3, cor_s, 8)
        gap_v = s.get("gap", 0)
        cor_g = RED if gap_v < 0 else GREEN
        txt(c, f"Gap: {gap_v:+.1f}%", cx_s + cw_s - 3*mm, top_y - 5*mm, 9, cor_g, bold=True, align="right")

        txt(c, p.get("nome","—"), cx_s + 3*mm, top_y - 16*mm, 11, WHITE, bold=True,
            max_w=cw_s - 6*mm)

        line(c, cx_s + 3*mm, top_y - 24*mm, cx_s + cw_s - 3*mm, GRAY)
        if p.get("taxa"):
            txt(c, p["taxa"], cx_s + 3*mm, top_y - 30*mm, 11, GREEN, bold=True)
        if p.get("emissor"):
            txt(c, p["emissor"], cx_s + 3*mm, top_y - 40*mm, 9, LGRAY)
        if p.get("vencimento"):
            txt(c, f"Vcto: {p['vencimento']}", cx_s + 3*mm, top_y - 50*mm, 8.5, GRAY)

        line(c, cx_s + 3*mm, top_y - 55*mm, cx_s + cw_s - 3*mm, GRAY)
        if p.get("motivo"):
            txt(c, p["motivo"], cx_s + 3*mm, top_y - 62*mm, 8.5, LGRAY,
                max_w=cw_s - 6*mm)

        if p.get("indicado_por"):
            txt(c, f"Indicado: {p['indicado_por']}", cx_s + 3*mm, 19*mm, 7.5, GRAY)

# ══════════════════════════════════════════════════════════════════════════════
# SLIDE — PRÓXIMOS PASSOS
# ══════════════════════════════════════════════════════════════════════════════
def slide_proximos(c, d, ia, pg, total):
    bg(c)
    header(c, "PRÓXIMOS PASSOS", "Encaminhamentos acordados na reunião", pg, total)
    footer(c, d.get("nome_cliente",""), d.get("data_ref",""))

    alertas = d.get("alertas_relevantes", [])
    if alertas:
        ah = 11*mm + len(alertas[:3]) * 8*mm + 6*mm
        card(c, 7*mm, H - 25*mm - ah, W - 14*mm, ah, HexColor("#150808"), RED)
        txt(c, "ALERTAS ATIVOS DO HEAD DE PRODUTOS",
            12*mm, H - 25*mm - 6*mm, 9, RED, bold=True)
        for i, a in enumerate(alertas[:3]):
            txt(c, f"• {a.get('produto','')} — {a.get('mensagem','')}",
                12*mm, H - 34*mm - 6*mm - i * 8*mm, 9, LGRAY,
                max_w=W - 22*mm)
        base_y = H - 25*mm - ah - 8*mm
    else:
        base_y = H - 28*mm

    # Encaminhamentos
    section_title(c, "ENCAMINHAMENTOS", 8*mm, base_y, GOLD)
    line(c, 8*mm, base_y - 3*mm, W - 8*mm, GOLD3, 0.5)

    passos_txt = ia.get("proximos_passos","")
    if passos_txt:
        passos = [l.strip() for l in passos_txt.split("\n") if l.strip()]
    else:
        passos = [
            "Assinar a proposta de realocação apresentada hoje",
            "Agendar revisão de carteira em 60 dias",
            "Verificar documentação para Open Investments (OPIN)",
            "Enviar simulação de IR para ativos a serem resgatados",
        ]

    row_h = 13*mm
    for i, passo in enumerate(passos[:5]):
        py   = base_y - 8*mm - i * row_h
        card(c, 7*mm, py - 9*mm, W - 14*mm, row_h - 1*mm, CARD1, CARD2)
        c.setFillColor(GOLD)
        c.circle(18*mm, py - 1*mm, 4.5*mm, fill=1, stroke=0)
        txt(c, f"0{i+1}", 18*mm, py - 3*mm, 8.5, BLACK, bold=True, align="center")
        txt(c, passo, 26*mm, py - 1*mm, 11, WHITE, max_w=W - 34*mm)

    # Assinatura
    line(c, 8*mm, 19*mm, 80*mm, GRAY)
    txt(c, d.get("assessor","Assessor"), 8*mm, 15*mm, 10, LGRAY)
    txt(c, "Assessor Braúna Investimentos", 8*mm, 11*mm, 7.5, GRAY)

# ══════════════════════════════════════════════════════════════════════════════
# CLAUDE API
# ══════════════════════════════════════════════════════════════════════════════
def chamar_claude(prompt: str, tokens=600) -> str:
    try:
        import anthropic
        key = os.environ.get("ANTHROPIC_API_KEY","")
        if not key: return ""
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=tokens,
            messages=[{"role":"user","content":prompt}]
        )
        return msg.content[0].text.strip()
    except Exception:
        return ""

def enriquecer_com_ia(d: dict) -> dict:
    nome    = d.get("nome_cliente","o cliente")
    pat     = d.get("patrimonio",0)
    perfil  = d.get("perfil","moderado")
    desvios = d.get("desvios",[])
    cenario = d.get("cenario_macro",{})
    sugs    = d.get("sugestoes_produtos",[])
    rent12m = d.get("rent_12m",0)
    cdi12m  = d.get("rent",{}).get("cdi",{}).get("12m",0) if isinstance(d.get("rent"),dict) else 0
    pct_cdi = round(rent12m/cdi12m*100,1) if cdi12m else 0

    fora    = [dv for dv in desvios if dv.get("status")=="fora"]
    acima   = [dv for dv in fora if dv.get("desvio",0)>0]
    abaixo  = [dv for dv in fora if dv.get("desvio",0)<0]

    p_exec = f"""Você é analista sênior da Braúna Investimentos. Escreva 2-3 frases executivas (tom profissional, direto, empático) para apresentar ao cliente {nome} a análise da carteira R$ {pat:,.0f}, perfil {perfil}. Rentabilidade 12M: {rent12m:.2f}% ({pct_cdi:.0f}% do CDI). Principais desvios: {', '.join([dv['label']+(' sobrealocado' if dv['desvio']>0 else ' subalocado') for dv in fora[:3]])}. Sem markdown."""

    p_diag = f"""Em 2 frases, explique ao assessor o impacto dos desvios para {nome} (perfil {perfil}): Sobrealocado: {', '.join([dv['label']+f' (+{dv["desvio"]:.1f}%)' for dv in acima[:3]])}. Subalocado: {', '.join([dv['label']+f' ({dv["desvio"]:.1f}%)' for dv in abaixo[:3]])}. Cenário: {cenario.get('posicionamento','')[:150]}. Foco no impacto prático. Sem markdown."""

    nomes_sug = [s.get("produto",{}).get("nome","") for s in sugs[:3] if s.get("produto")]
    p_sug = f"""2 frases de transição para apresentar as sugestões de realocação ao cliente {nome}. Produtos: {', '.join(nomes_sug) or 'renda fixa e internacional'}. Tom: consultor confiante. Sem markdown."""

    p_prox = f"""Liste 3-4 próximos passos concretos (uma linha cada, começando com verbo no infinitivo) para o assessor propor a {nome} ao final da reunião. Perfil {perfil}, gaps: {', '.join([dv['label'] for dv in fora[:3]])}. Sem markdown, sem numeração."""

    resultados = {}
    for chave, prompt, tokens in [
        ("resumo_exec",     p_exec,  180),
        ("diagnostico",     p_diag,  180),
        ("narrativa_sug",   p_sug,   120),
        ("proximos_passos", p_prox,  200),
    ]:
        r = chamar_claude(prompt, tokens)
        resultados[chave] = r or None
    return resultados

# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT — GERAR APRESENTAÇÃO COMPLETA
# ══════════════════════════════════════════════════════════════════════════════
def gerar_apresentacao(d: dict) -> bytes:
    """
    Gera PDF landscape 297×210mm com slides dinâmicos baseados nos dados do cliente.
    Número de slides varia conforme a riqueza de dados fornecidos.
    """
    ia = enriquecer_com_ia(d)

    # Monta lista de slides dinamicamente
    slides = []

    # 1. Capa (sempre)
    slides.append(("capa", None))

    # 2. Evolução Patrimonial (sempre)
    slides.append(("patrimonio", None))

    # 3. Carteira vs. Modelo (se houver desvios)
    if d.get("desvios"):
        slides.append(("comparativo", None))

    # 4+ Posição detalhada por classe (dinâmico)
    ativos_det = d.get("ativos_detalhe", {})
    ORDEM_CLASSES = ["pos_fixado","inflacao","pre_fixado","alternativos","multimercado","internacional"]
    for cls in ORDEM_CLASSES:
        ativos = ativos_det.get(cls, [])
        if ativos:
            slides.append(("posicao_classe", {"cls": cls, "ativos": ativos}))

    # Ações & FIIs (se houver)
    if d.get("acoes") or d.get("fiis"):
        slides.append(("rv", None))

    # Cenário macro (se houver)
    if d.get("cenario_macro"):
        slides.append(("cenario", None))

    # Sugestões de realocação (se houver)
    if d.get("sugestoes_produtos"):
        slides.append(("sugestoes", None))

    # Próximos passos (sempre)
    slides.append(("proximos", None))

    total = len(slides)

    buf = io.BytesIO()
    cnv = canvas.Canvas(buf, pagesize=(W, H))
    cnv.setTitle(f"Braúna — {d.get('nome_cliente','Cliente')} — {d.get('data_ref','')}")

    fn_map = {
        "capa":           slide_capa,
        "patrimonio":     slide_patrimonio,
        "comparativo":    slide_comparativo,
        "rv":             slide_rv,
        "cenario":        slide_cenario,
        "sugestoes":      slide_sugestoes,
        "proximos":       slide_proximos,
    }

    for pg, (tipo, extra) in enumerate(slides, 1):
        if tipo == "posicao_classe":
            slide_posicao_classe(cnv, d, ia, pg, total,
                                 extra["cls"], extra["ativos"])
        else:
            fn_map[tipo](cnv, d, ia, pg, total)
        cnv.showPage()

    cnv.save()
    return buf.getvalue()
