from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import os

W, H = A4
pasta = r'C:/Users/Perfil/OneDrive/Área de Trabalho/analise-carteiras-brauna/clientes/243120_DenisKinoshita'

BG     = HexColor("#0A0A08")
GOLD   = HexColor("#D6B27A")
GOLD2  = HexColor("#E8C96B")
GREEN  = HexColor("#5DCAA5")
RED    = HexColor("#FF6B6B")
AMBER  = HexColor("#F0A830")
DARK1  = HexColor("#141410")
DARK2  = HexColor("#1A1A14")
GRAY   = HexColor("#444440")
LGRAY  = HexColor("#888880")
WHITE  = HexColor("#F0F0F0")
BLACK  = HexColor("#0A0A08")

def draw_bg(c, y_from=0, y_to=None):
    if y_to is None: y_to = H
    c.setFillColor(BG)
    c.rect(0, y_from, W, y_to - y_from, fill=1, stroke=0)

def draw_card(c, x, y, w, h, color=None, stroke=None):
    color = color or DARK1
    c.setFillColor(color)
    c.roundRect(x, y, w, h, 6, fill=1, stroke=0)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(0.8)
        c.roundRect(x, y, w, h, 6, fill=0, stroke=1)

def text(c, txt, x, y, size=10, color=None, bold=False, align="left"):
    color = color or WHITE
    c.setFillColor(color)
    fname = "Helvetica-Bold" if bold else "Helvetica"
    c.setFont(fname, size)
    if align == "center":
        c.drawCentredString(x, y, str(txt))
    elif align == "right":
        c.drawRightString(x, y, str(txt))
    else:
        c.drawString(x, y, str(txt))

def line(c, x1, y1, x2, y2, color=None, width=0.5):
    c.setStrokeColor(color or GRAY)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)

def bar_horiz(c, x, y, w, h, pct, color, bg=None):
    bg = bg or DARK2
    c.setFillColor(bg)
    c.roundRect(x, y, w, h, 2, fill=1, stroke=0)
    bw = w * min(pct / 100.0, 1.0)
    if bw > 0:
        c.setFillColor(color)
        c.roundRect(x, y, bw, h, 2, fill=1, stroke=0)

# ── PAGE 1 ────────────────────────────────────────────────────────────────────
pdf_path = f"{pasta}/relatorio_20260529.pdf"
c = canvas.Canvas(pdf_path, pagesize=A4)

# Background
draw_bg(c)

# Header bar
c.setFillColor(DARK1)
c.rect(0, H - 72*mm, W, 72*mm, fill=1, stroke=0)
c.setFillColor(GOLD)
c.rect(0, H - 72*mm, W, 0.8, fill=1, stroke=0)

# Logo / nome
text(c, "BRAUNA", 18*mm, H - 20*mm, size=22, color=GOLD, bold=True)
text(c, "INVESTIMENTOS", 18*mm, H - 28*mm, size=9, color=LGRAY)

# Divisor vertical
c.setFillColor(GRAY)
c.rect(68*mm, H - 60*mm, 0.5, 50*mm, fill=1, stroke=0)

# Dados do relatório
text(c, "RELATORIO DE CARTEIRA", 75*mm, H - 20*mm, size=14, color=WHITE, bold=True)
text(c, "XPerformance - Conta 243120", 75*mm, H - 29*mm, size=9, color=LGRAY)

text(c, "Assessor", 75*mm, H - 40*mm, size=7, color=LGRAY)
text(c, "Denis Kinoshita", 75*mm, H - 47*mm, size=11, color=GOLD, bold=True)

text(c, "Data de Referencia", 140*mm, H - 40*mm, size=7, color=LGRAY)
text(c, "29/05/2026", 140*mm, H - 47*mm, size=11, color=WHITE, bold=True)

text(c, "Gerado em 19/06/2026  |  Levante Asset - Modelo Junho 2026", 75*mm, H - 60*mm, size=7, color=LGRAY)

# ── Patrimônio cards row ──
cy = H - 88*mm
for i, (lbl, val, sub, color) in enumerate([
    ("PATRIMONIO TOTAL", "R$ 1.357.199,67", "", GOLD),
    ("RENT. MES", "+0,97%", "90,3% CDI", GREEN),
    ("RENT. 12M", "+18,56%", "125,8% CDI", GREEN),
    ("GANHO 24M", "+R$ 249.870", "+26,07%", AMBER),
]):
    x = 14*mm + i * 47*mm
    draw_card(c, x, cy, 44*mm, 20*mm, DARK1, GRAY)
    text(c, lbl, x + 2*mm, cy + 13*mm, size=6, color=LGRAY)
    text(c, val, x + 2*mm, cy + 7*mm, size=10, color=color, bold=True)
    if sub:
        text(c, sub, x + 2*mm, cy + 3*mm, size=7, color=LGRAY)

# ── Seção: Composição atual ──
cy2 = H - 120*mm
text(c, "COMPOSICAO DA CARTEIRA", 14*mm, cy2 + 4*mm, size=8, color=GOLD, bold=True)
line(c, 14*mm, cy2 + 1*mm, W - 14*mm, cy2 + 1*mm, GRAY)

classes = [
    ("Pos Fixado (CDI)",    56.81, GOLD),
    ("Inflacao (IPCA)",     23.16, AMBER),
    ("Acoes / RV Brasil",    9.39, GREEN),
    ("FIIs / Fundos List.",  4.51, HexColor("#7DCFEF")),
    ("Alternativo",          2.18, HexColor("#B08FCF")),
    ("Pre Fixado",           2.45, HexColor("#F07850")),
    ("Multimercado",         0.00, LGRAY),
    ("Internacional",        0.00, LGRAY),
    ("Caixa",                1.38, GRAY),
]

row_h = 8.5*mm
start_y = cy2 - 2*mm
saldo_map = {
    "Pos Fixado (CDI)": 771030.04,
    "Inflacao (IPCA)": 314349.42,
    "Acoes / RV Brasil": 127408.00,
    "FIIs / Fundos List.": 61200.40,
    "Alternativo": 29542.54,
    "Pre Fixado": 33186.66,
    "Multimercado": 0,
    "Internacional": 0,
    "Caixa": 18756.30,
}

for i, (lbl, pct, color) in enumerate(classes):
    ry = start_y - i * row_h
    # dot
    c.setFillColor(color)
    c.circle(17*mm, ry - 2.5*mm, 1.5*mm, fill=1, stroke=0)
    text(c, lbl, 21*mm, ry - 5*mm, size=8.5, color=WHITE)
    # bar
    bar_horiz(c, 70*mm, ry - 6*mm, 90*mm, 4*mm, pct, color)
    text(c, f"{pct:.2f}%", 163*mm, ry - 5*mm, size=8.5, color=color, bold=True)
    saldo = saldo_map.get(lbl, 0)
    text(c, f"R$ {saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
         182*mm, ry - 5*mm, size=7.5, color=LGRAY)

c.showPage()

# ── PAGE 2: Comparativo com Modelo ──────────────────────────────────────────
draw_bg(c)
c.setFillColor(DARK1)
c.rect(0, H - 20*mm, W, 20*mm, fill=1, stroke=0)
text(c, "BRAUNA INVESTIMENTOS", 14*mm, H - 13*mm, size=9, color=GOLD, bold=True)
text(c, "Conta 243120  |  Ref. 29/05/2026", W - 14*mm, H - 13*mm, size=8, color=LGRAY, align="right")

text(c, "ANALISE COMPARATIVA - CARTEIRA vs MODELO LEVANTE (MODERADO)", 14*mm, H - 28*mm, size=10, color=GOLD, bold=True)
text(c, "Modelo de referencia: Levante Asset - Junho 2026  |  Perfil: Moderado (inferido)", 14*mm, H - 35*mm, size=7.5, color=LGRAY)

# Tabela comparativa
comparativo = [
    ("Pos Fixado (CDI)",    56.81, 44.0, +12.81, "Fora do perfil"),
    ("Inflacao (IPCA)",     23.16, 23.0,  +0.16, "Adequado"),
    ("Pre Fixado",           2.45, 10.0,  -7.55, "Fora do perfil"),
    ("Acoes / RV Brasil",    9.39,  5.0,  +4.39, "Atencao"),
    ("FIIs / Fund. List.",   4.51,  1.5,  +3.01, "Atencao"),
    ("Multimercado",         0.00,  6.0,  -6.00, "Fora do perfil"),
    ("Alternativos",         2.18,  1.0,  +1.18, "Adequado"),
    ("Internacional",        0.00,  9.0,  -9.00, "Fora do perfil"),
    ("Criptomoedas",         0.00,  0.5,  -0.50, "Adequado"),
]

STATUS_COLOR = {
    "Adequado":      GREEN,
    "Atencao":       AMBER,
    "Fora do perfil": RED,
}
STATUS_ICON = {
    "Adequado":      "OK",
    "Atencao":       "(!)",
    "Fora do perfil": "X",
}

row_y = H - 48*mm
# Header
c.setFillColor(DARK2)
c.rect(14*mm, row_y - 7*mm, W - 28*mm, 7*mm, fill=1, stroke=0)
for x, lbl in [(16*mm,"CLASSE"), (80*mm,"ATUAL"), (104*mm,"MODELO"), (128*mm,"DESVIO"), (152*mm,"STATUS")]:
    text(c, lbl, x, row_y - 5*mm, size=7, color=GOLD, bold=True)

for i, (lbl, atual, modelo, desvio, st) in enumerate(comparativo):
    ry = row_y - 14*mm - i * 10*mm
    bg = DARK1 if i % 2 == 0 else HexColor("#0E0E0C")
    c.setFillColor(bg)
    c.rect(14*mm, ry - 3*mm, W - 28*mm, 10*mm, fill=1, stroke=0)

    sc = STATUS_COLOR.get(st, LGRAY)
    text(c, lbl,           16*mm, ry + 2*mm, size=8.5, color=WHITE)
    text(c, f"{atual:.2f}%", 80*mm, ry + 2*mm, size=8.5, color=WHITE)
    text(c, f"{modelo:.1f}%", 104*mm, ry + 2*mm, size=8.5, color=LGRAY)
    dev_color = RED if desvio < -2 or desvio > 2 else GREEN
    text(c, f"{desvio:+.2f}%", 128*mm, ry + 2*mm, size=8.5, color=dev_color, bold=True)

    # Status pill
    c.setFillColor(sc)
    c.setFillAlpha(0.15)
    c.roundRect(150*mm, ry - 1*mm, 44*mm, 6*mm, 3, fill=1, stroke=0)
    c.setFillAlpha(1.0)
    text(c, STATUS_ICON[st] + " " + st, 152*mm, ry + 1*mm, size=7.5, color=sc, bold=True)

# ── Legenda de gaps ──
gap_y = row_y - 14*mm - 9 * 10*mm - 8*mm
text(c, "GAPS CRITICOS IDENTIFICADOS", 14*mm, gap_y, size=8, color=RED, bold=True)
line(c, 14*mm, gap_y - 2*mm, W - 14*mm, gap_y - 2*mm, GRAY)

gaps = [
    (RED,   "Pos Fixado (+12,81%)",    "Carteira 56,81% vs modelo 44%. Excesso de caixa/CDI reduz potencial de retorno a longo prazo."),
    (RED,   "Internacional (-9,00%)",  "Zero exposicao externa vs modelo 9%. Sem hedge cambial nem diversificacao geografica."),
    (RED,   "Multimercado (-6,00%)",   "Zero em multimercado vs modelo 6%. Perde descorrelacao e alpha de gestores especializados."),
    (RED,   "Pre Fixado (-7,55%)",     "2,45% vs modelo 10%. Oportunidade de travar taxas elevadas antes de cortes da Selic."),
    (AMBER, "Acoes (+4,39%)",          "9,39% vs modelo 5%. Levemente acima. Monitorar - volatilidade de COGN3 e RDOR3 preocupa."),
    (AMBER, "FIIs (+3,01%)",           "4,51% vs modelo 1,5%. Excesso de FIIs em cenario de juros altos (headwind para o segmento)."),
]
for i, (color, titulo, desc) in enumerate(gaps):
    gy = gap_y - 10*mm - i * 13*mm
    c.setFillColor(color)
    c.circle(17*mm, gy - 1*mm, 1.5*mm, fill=1, stroke=0)
    text(c, titulo, 21*mm, gy + 1*mm, size=8.5, color=color, bold=True)
    text(c, desc,   21*mm, gy - 4*mm, size=7.5, color=LGRAY)

c.showPage()

# ── PAGE 3: Sugestões de Realocação ─────────────────────────────────────────
draw_bg(c)
c.setFillColor(DARK1)
c.rect(0, H - 20*mm, W, 20*mm, fill=1, stroke=0)
text(c, "BRAUNA INVESTIMENTOS", 14*mm, H - 13*mm, size=9, color=GOLD, bold=True)
text(c, "Conta 243120  |  Ref. 29/05/2026", W - 14*mm, H - 13*mm, size=8, color=LGRAY, align="right")

text(c, "SUGESTOES DE REALOCACAO", 14*mm, H - 28*mm, size=10, color=GOLD, bold=True)
text(c, "Priorizando menor impacto tributario e adequacao ao perfil Moderado", 14*mm, H - 35*mm, size=7.5, color=LGRAY)

sugestoes = [
    {
        "numero": "01",
        "titulo": "Reduzir Pos Fixado | Migrar para Internacional",
        "cor": RED,
        "atual": "Trend Pos-Fixado FIC FIRF Simples RL — R$ 230.386,43 (16,98%)",
        "problema": "O Trend Pos-Fixado e o SulAmerica Premium acumulam ~21% em CDI basico. Com Selic em queda esperada, o retorno futuro tende a comprimir.",
        "sugestao": "Resgatar gradualmente R$ 80.000 - R$ 100.000 e alocar em fundos com exposicao internacional (IVVB11, fundos com BDRs ou fundos hedge cambial da XP).",
        "impacto": "Adiciona hedge cambial, diversificacao geografica e exposicao ao S&P500. Reequilibra Internacional de 0% para ~7%.",
        "fiscal": "Fundos RF curto prazo: IR progressivo (22,5% se resgate antes de 180 dias). Aguardar minimo 181 dias para reduzir a 20% (ou 365 para 17,5%).",
    },
    {
        "numero": "02",
        "titulo": "Iniciar posicao em Multimercado",
        "cor": RED,
        "atual": "Multimercado: 0% (zero exposicao)",
        "problema": "Ausencia de multimercado reduz a descorrelacao da carteira e perde o potencial de alpha de gestores macro em periodos de volatilidade.",
        "sugestao": "Alocar R$ 50.000 - R$ 80.000 em fundos multiestratégia com track record solido: Kinea Chronos, SPX Raptor, Adam Macro ou Ibiuna Long Biased.",
        "impacto": "Reequilibra Multimercado de 0% para ~4-6%. Adiciona gestao ativa macro descorrelacionada com renda fixa.",
        "fiscal": "Fundos multimercado: come-cotas 2x/ano (31 mai e 30 nov) - IR de 15% no longo prazo. Fator a considerar no timing de entrada.",
    },
    {
        "numero": "03",
        "titulo": "Aumentar Pre Fixado aproveitando taxas elevadas",
        "cor": AMBER,
        "atual": "Pre Fixado: 2,45% (R$ 33.186,66) — muito abaixo do modelo 10%",
        "problema": "Com Selic ainda elevada (projeccao queda em 2026-2027), ha janela para travar taxas prefixadas acima de 13% ao ano antes do ciclo de cortes.",
        "sugestao": "Comprar NTN-F 2029 ou 2031 via Tesouro Direto, ou CDBs prefixados de bancos medios (14-15% a.a.) com vencimento 2027-2028.",
        "impacto": "Eleva Pre Fixado de 2,45% para ~7-8%. Trava rentabilidade real positiva caso Selic caia abaixo de 12% a.a.",
        "fiscal": "Tesouro Direto e CDBs: IR regressivo. Priorizar titulos com vencimento alem de 720 dias (aliquota 15%).",
    },
    {
        "numero": "04",
        "titulo": "Revisar COGN3 — acao de alta volatilidade fora do perfil moderado",
        "cor": AMBER,
        "atual": "COGN3 — R$ 32.250,00 (2,38%) | Rent. ano: -19,42%",
        "problema": "COGN3 acumula -19,42% no ano e -10,07% no mes. Alta volatilidade e fundamentos frágeis inconsistentes com perfil moderado.",
        "sugestao": "Avaliar reducao ou zeragem de COGN3. Eventualmente migrar para VALE3 (maior posicao com 3,05%, fundamentos mais solidos) ou ativo do setor de saude.",
        "impacto": "Reduz volatilidade da parcela de RV. Melhora qualidade da carteira de acoes sem reduzir exposicao total ao indexador.",
        "fiscal": "COGN3 em prejuizo: zerar gera prejuizo abativel em ganhos futuros de RV (ate 5 anos). Timing estrategico para compensar ganhos.",
    },
    {
        "numero": "05",
        "titulo": "Reduzir FIIs — headwind em cenario de juros altos",
        "cor": AMBER,
        "atual": "FIIs Listados: 4,51% (HTMX11, KNHY11, KOPA11) vs modelo 1,5%",
        "problema": "FIIs tendem a perder valor em cenarios de juros altos (alta de juros eleva o custo de oportunidade). HTMX11 acumula -7,61% no ano.",
        "sugestao": "Reduzir HTMX11 (maior posicao, -7,61% no ano). Manter exposicao residual em FIIs de papel com boa distribuicao (KNHY11 em linha com CDI).",
        "impacto": "Reduz FIIs de 4,51% para ~2%. Libera capital para realocar em Internacional ou Multimercado.",
        "fiscal": "Ganho de capital em FIIs: IR 20% para pessoa fisica. HTMX11 em queda: zerar pode gerar prejuizo compensavel.",
    },
]

sy = H - 42*mm
for sg in sugestoes:
    ch = 38*mm
    sc = sg["cor"]
    # Card background
    draw_card(c, 14*mm, sy - ch, W - 28*mm, ch, DARK1, sc)
    # numero badge
    c.setFillColor(sc)
    c.circle(21*mm, sy - 7*mm, 4*mm, fill=1, stroke=0)
    text(c, sg["numero"], 21*mm, sy - 9*mm, size=7.5, color=BLACK, bold=True, align="center")
    # titulo
    text(c, sg["titulo"], 28*mm, sy - 5*mm, size=9, color=sc, bold=True)
    # conteudo
    labels_row = [("Produto Atual:", sg["atual"]), ("Problema:", sg["problema"]),
                  ("Sugestao:", sg["sugestao"]), ("Fiscal:", sg["fiscal"])]
    for j, (lbl, val) in enumerate(labels_row):
        ry2 = sy - 11*mm - j * 6.5*mm
        text(c, lbl, 17*mm, ry2, size=6.5, color=GOLD, bold=True)
        # truncate long text
        max_chars = 120
        val_show = val[:max_chars] + ("..." if len(val) > max_chars else "")
        text(c, val_show, 42*mm, ry2, size=6.5, color=LGRAY)

    sy -= (ch + 4*mm)
    if sy < 20*mm:
        c.showPage()
        draw_bg(c)
        c.setFillColor(DARK1)
        c.rect(0, H - 20*mm, W, 20*mm, fill=1, stroke=0)
        text(c, "BRAUNA INVESTIMENTOS", 14*mm, H - 13*mm, size=9, color=GOLD, bold=True)
        text(c, "Conta 243120  |  Ref. 29/05/2026", W - 14*mm, H - 13*mm, size=8, color=LGRAY, align="right")
        text(c, "SUGESTOES DE REALOCACAO (continuacao)", 14*mm, H - 28*mm, size=10, color=GOLD, bold=True)
        sy = H - 38*mm

# ── Página final: carteira detalhada de ações e FIIs ──
c.showPage()
draw_bg(c)
c.setFillColor(DARK1)
c.rect(0, H - 20*mm, W, 20*mm, fill=1, stroke=0)
text(c, "BRAUNA INVESTIMENTOS", 14*mm, H - 13*mm, size=9, color=GOLD, bold=True)
text(c, "Conta 243120  |  Ref. 29/05/2026", W - 14*mm, H - 13*mm, size=8, color=LGRAY, align="right")

text(c, "CARTEIRA DETALHADA — ACOES E FIIS", 14*mm, H - 28*mm, size=10, color=GOLD, bold=True)

# Ações
text(c, "ACOES / RENDA VARIAVEL BRASIL  —  R$ 127.408,00  (9,39%)", 14*mm, H - 38*mm, size=8, color=GREEN, bold=True)
line(c, 14*mm, H - 40*mm, W - 14*mm, H - 40*mm, GREEN, 0.4)

acoes_hdr = ["Ticker", "Qtd.", "Saldo (R$)", "% Carteira", "Rent. Ano", "Rent. 12M", "Situacao"]
acoes_data = [acoes_hdr] + [
    ["VALE3",       "500",   "41.410,00", "3,05%", "+16,85%", "+51,73%", "OK"],
    ["COGN3",       "12.900","32.250,00", "2,38%", "-19,42%", "--",       "REVISAR"],
    ["AURA33",      "200",   "26.358,00", "1,94%", "+59,11%", "--",       "OK"],
    ["RAPT4",       "2.000", "10.360,00", "0,76%", "-10,26%", "--",       "MONITORAR"],
    ["RDOR3",       "300",   "10.206,00", "0,75%", "-16,26%", "--",       "MONITORAR"],
    ["USIM5",       "500",   "5.540,00",  "0,41%", "+88,34%", "--",       "OK"],
    ["ITSA4",       "200",   "2.584,00",  "0,19%", "-2,07%",  "--",       "OK"],
    ["BBASR221(Op.","--",    "-1.300,00", "-0,10%","--",       "--",       "OPCAO"],
]

tbl_x = 14*mm
tbl_y = H - 43*mm
col_ws = [22*mm, 18*mm, 28*mm, 22*mm, 22*mm, 22*mm, 24*mm]

for ri, row in enumerate(acoes_data):
    ry = tbl_y - ri * 9*mm
    bg = DARK2 if ri == 0 else (DARK1 if ri % 2 == 0 else HexColor("#0C0C0A"))
    c.setFillColor(bg)
    c.rect(tbl_x, ry - 7*mm, sum(col_ws), 8*mm, fill=1, stroke=0)
    cx = tbl_x + 2*mm
    for ci, cell in enumerate(row):
        if ri == 0:
            cell_color = GOLD
            bold = True
        else:
            # colorir células de situação
            if ci == 6:
                if cell == "OK": cell_color = GREEN
                elif cell == "REVISAR": cell_color = RED
                else: cell_color = AMBER
                bold = True
            elif ci in (4, 5) and ri > 0:
                if cell.startswith("-"): cell_color = RED
                elif cell.startswith("+"): cell_color = GREEN
                else: cell_color = LGRAY
                bold = False
            else:
                cell_color = WHITE if ci == 0 else LGRAY
                bold = ci == 0
        text(c, cell, cx, ry - 4.5*mm, size=7.5, color=cell_color, bold=bold)
        cx += col_ws[ci]

# FIIs
fii_y = tbl_y - 9 * 9*mm - 8*mm
text(c, "FIIS / FUNDOS LISTADOS  —  R$ 61.200,40  (4,51%)", 14*mm, fii_y + 4*mm, size=8, color=HexColor("#7DCFEF"), bold=True)
line(c, 14*mm, fii_y + 1*mm, W - 14*mm, fii_y + 1*mm, HexColor("#7DCFEF"), 0.4)

fiis_hdr = ["Ticker", "Qtd.", "Saldo (R$)", "% Carteira", "Rent. Ano", "Rent. 12M", "Rend./mes", "Situacao"]
fiis_data = [fiis_hdr] + [
    ["HTMX11", "272", "36.448,00", "2,69%", "-7,61%",  "+6,12%",  "R$1,20/cota", "REDUZIR"],
    ["KNHY11", "168", "16.892,40", "1,24%", "+5,72%",  "+12,87%", "R$0,115/cota","OK"],
    ["KOPA11", "20",  "7.860,00",  "0,58%", "+17,51%", "+29,50%", "R$0,80/cota", "OK"],
]

fii_col_ws = [20*mm, 15*mm, 26*mm, 20*mm, 20*mm, 20*mm, 24*mm, 20*mm]
for ri, row in enumerate(fiis_data):
    ry = fii_y - 4*mm - ri * 9*mm
    bg = DARK2 if ri == 0 else (DARK1 if ri % 2 == 0 else HexColor("#0C0C0A"))
    c.setFillColor(bg)
    c.rect(tbl_x, ry - 7*mm, sum(fii_col_ws), 8*mm, fill=1, stroke=0)
    cx = tbl_x + 2*mm
    for ci, cell in enumerate(row):
        if ri == 0:
            cell_color = GOLD; bold = True
        elif ci == 7:
            cell_color = RED if cell == "REDUZIR" else GREEN; bold = True
        elif ci in (4, 5) and ri > 0:
            cell_color = RED if cell.startswith("-") else GREEN; bold = False
        else:
            cell_color = WHITE if ci == 0 else LGRAY; bold = ci == 0
        text(c, cell, cx, ry - 4.5*mm, size=7.5, color=cell_color, bold=bold)
        cx += fii_col_ws[ci]

# Rodapé
c.setFillColor(DARK1)
c.rect(0, 0, W, 14*mm, fill=1, stroke=0)
c.setFillColor(GOLD)
c.rect(0, 14*mm, W, 0.5, fill=1, stroke=0)
text(c, "Brauna Investimentos  |  Relatorio gerado em 19/06/2026  |  Codigo 243120  |  Assessor: Denis Kinoshita",
     W / 2, 8*mm, size=7, color=LGRAY, align="center")
text(c, "Material informativo. Nao constitui recomendacao formal de investimento. Verifique o suitability do cliente antes de qualquer movimentacao.",
     W / 2, 3*mm, size=6, color=GRAY, align="center")

c.save()
print(f"PDF gerado em: {pdf_path}")
print(f"Tamanho: {os.path.getsize(pdf_path):,} bytes")
