"""
Gerador de Apresentação PPTX — Braúna Investimentos
Mínimo 10 · Máximo 15 slides · Identidade visual Braúna
"""
import io, math
from pptx import Presentation
from pptx.util import Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Paleta ────────────────────────────────────────────────────────────────────
C_BG    = RGBColor(0x07,0x1E,0x17)
C_CARD  = RGBColor(0x0A,0x2A,0x1E)
C_CARD2 = RGBColor(0x0F,0x35,0x25)
C_CARD3 = RGBColor(0x12,0x3A,0x28)
C_GOLD  = RGBColor(0xC9,0xA9,0x6E)
C_GOLD2 = RGBColor(0xD4,0xB4,0x83)
C_GREEN = RGBColor(0x5D,0xCA,0xA5)
C_RED   = RGBColor(0xFF,0x6B,0x6B)
C_AMBER = RGBColor(0xF0,0xA8,0x30)
C_BLUE  = RGBColor(0x7D,0xCF,0xEF)
C_PURP  = RGBColor(0xB0,0x8F,0xCF)
C_WHITE = RGBColor(0xF0,0xF0,0xF0)
C_LGRAY = RGBColor(0x88,0x88,0x80)
C_GRAY  = RGBColor(0x2A,0x5A,0x40)
C_DGRAY = RGBColor(0x18,0x3F,0x2D)

CLS_COR = {
    "pos_fixado":    C_GOLD,
    "inflacao":      C_AMBER,
    "pre_fixado":    RGBColor(0xF0,0x78,0x50),
    "acoes":         C_GREEN,
    "fiis":          C_BLUE,
    "multimercado":  C_PURP,
    "alternativos":  RGBColor(0x4E,0xC9,0xB0),
    "internacional": RGBColor(0x5B,0x9B,0xD5),
    "criptomoedas":  C_LGRAY,
}
CLS_LABEL = {
    "pos_fixado":"Pós Fixado","inflacao":"Inflação","pre_fixado":"Pré Fixado",
    "acoes":"Ações","fiis":"FIIs","multimercado":"Multimercado",
    "alternativos":"Alternativos","internacional":"Internacional","criptomoedas":"Criptomoedas",
}
CATS = ["pos_fixado","inflacao","pre_fixado","acoes","fiis","multimercado","alternativos","internacional","criptomoedas"]

SW = Cm(33.87)
SH = Cm(19.05)
MARGIN = Cm(0.7)

# ── Primitivas ────────────────────────────────────────────────────────────────
def add_rect(slide, x, y, w, h, fill, border=None, bw=0.4, radius=False):
    shp = slide.shapes.add_shape(1, x, y, w, h)
    shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if border:
        shp.line.color.rgb = border; shp.line.width = Pt(bw)
    else:
        shp.line.fill.background()
    return shp

def add_text(slide, text, x, y, w, h, size=11, bold=False, color=C_WHITE,
             align=PP_ALIGN.LEFT, italic=False, wrap=True):
    txb = slide.shapes.add_textbox(x, y, w, h)
    tf  = txb.text_frame; tf.word_wrap = wrap
    p   = tf.paragraphs[0]; p.alignment = align
    run = p.add_run(); run.text = str(text)
    run.font.size = Pt(size); run.font.bold = bold
    run.font.color.rgb = color; run.font.italic = italic
    return txb

def bg(slide):
    add_rect(slide, 0, 0, SW, SH, C_BG)

def header(slide, titulo, sub=""):
    add_rect(slide, 0, 0, SW, Cm(0.07), C_GOLD)
    add_text(slide, "BRAÚNA INVESTIMENTOS", MARGIN, Cm(0.12), Cm(12), Cm(0.6),
             size=7, bold=True, color=C_GOLD)
    add_text(slide, titulo, MARGIN, Cm(0.82), Cm(28), Cm(1.3),
             size=20, bold=True, color=C_WHITE)
    if sub:
        add_text(slide, sub, MARGIN, Cm(2.1), Cm(28), Cm(0.65),
                 size=9.5, color=C_LGRAY)

def footer(slide, nome, data):
    add_rect(slide, 0, SH - Cm(0.58), SW, Cm(0.58), C_CARD2)
    add_text(slide, nome, MARGIN, SH - Cm(0.52), Cm(16), Cm(0.45), size=8, color=C_LGRAY)
    add_text(slide, f"Braúna Investimentos  ·  {data}", SW - Cm(9), SH - Cm(0.52),
             Cm(8.5), Cm(0.45), size=8, color=C_LGRAY, align=PP_ALIGN.RIGHT)

def fmt(v):
    if v >= 1_000_000: return f"R$ {v/1_000_000:.2f}M"
    if v >= 1_000:     return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:.0f}"

def pct_cor(v): return C_GREEN if v >= 0 else C_RED

def add_caixa_texto(slide, texto, y, cor_borda=None, cor_bg=None, tamanho=9.5):
    """Bloco de texto narrativo com fundo semitransparente."""
    bg_c = cor_bg or C_CARD
    bord = cor_borda or C_GRAY
    add_rect(slide, MARGIN, y, SW - Cm(1.4), Cm(0.06), bord)
    box_h = Cm(1.8)
    add_rect(slide, MARGIN, y + Cm(0.06), SW - Cm(1.4), box_h, bg_c, bord, 0.3)
    add_text(slide, texto, MARGIN + Cm(0.4), y + Cm(0.25), SW - Cm(2.2), box_h - Cm(0.3),
             size=tamanho, color=C_WHITE, wrap=True)

def new_slide(prs): return prs.slides.add_slide(prs.slide_layouts[6])

# ── SLIDE 1: CAPA ─────────────────────────────────────────────────────────────
def s_capa(prs, d):
    sl = new_slide(prs); bg(sl)
    add_rect(sl, 0, 0, Cm(0.12), SH, C_GOLD)
    add_rect(sl, 0, 0, Cm(1.3), SH, C_CARD)
    add_text(sl, "BRAÚNA\nINVESTIMENTOS", Cm(1.7), Cm(1.8), Cm(18), Cm(2),
             size=10, bold=True, color=C_GOLD)
    add_text(sl, "APRESENTAÇÃO\nDE REUNIÃO", Cm(1.7), Cm(4.0), Cm(28), Cm(3.5),
             size=30, bold=True, color=C_WHITE)
    add_rect(sl, Cm(1.7), Cm(8.1), Cm(20), Cm(0.07), C_GOLD)
    nome = d.get("nome_cliente","Cliente")
    add_text(sl, nome, Cm(1.7), Cm(8.4), Cm(26), Cm(1.6), size=24, color=C_GOLD)
    pat = d.get("patrimonio",0)
    data= d.get("data_ref","")
    perfil_raw = str(d.get("perfil","")).lower()
    perfil = perfil_raw.capitalize()
    assessor = d.get("assessor","")
    add_text(sl, f"Patrimônio: {fmt(pat)}   ·   Data: {data}", Cm(1.7), Cm(10.3),
             Cm(26), Cm(0.7), size=11, color=C_LGRAY)
    add_text(sl, f"Perfil: {perfil}   ·   Assessor: {assessor}", Cm(1.7), Cm(11.1),
             Cm(26), Cm(0.7), size=10, color=C_LGRAY)

    # Badge de perfil colorido
    _PERFIL_COR = {"conservadora": C_BLUE, "moderada": C_GOLD, "arrojada": C_GREEN, "agressiva": C_RED}
    cor_perfil = _PERFIL_COR.get(perfil_raw, C_LGRAY)
    add_rect(sl, Cm(1.7), Cm(12.0), Cm(4.5), Cm(0.65), cor_perfil)
    add_text(sl, f"PERFIL  {perfil.upper()}", Cm(1.85), Cm(12.08), Cm(4.2), Cm(0.5),
             size=9, bold=True, color=C_BG)

    # Objetivo se disponível
    objetivo = d.get("objetivo","")
    y_obj = Cm(12.0)
    if objetivo:
        add_rect(sl, Cm(6.5), Cm(12.0), Cm(8), Cm(0.65), C_CARD2, C_GRAY, 0.3)
        add_text(sl, f"Objetivo: {objetivo}", Cm(6.75), Cm(12.08), Cm(7.7), Cm(0.5),
                 size=9, color=C_WHITE)

    # Texto descritivo
    descr = (f"Esta apresentação consolida a análise completa da carteira de {nome}, "
             f"cobrindo cenário macro, performance, desvios em relação ao modelo e próximos passos.")
    add_rect(sl, Cm(1.7), Cm(12.9), SW - Cm(2.5), Cm(1.4), C_CARD, C_GRAY, 0.3)
    add_text(sl, descr, Cm(2.0), Cm(13.05), SW - Cm(3.1), Cm(1.1),
             size=10, color=C_LGRAY, wrap=True)

    # Rodapé com assinatura do assessor
    add_rect(sl, 0, SH - Cm(1.5), SW, Cm(1.5), C_CARD)
    add_rect(sl, Cm(1.7), SH - Cm(1.35), Cm(0.04), Cm(1.0), C_GOLD)
    add_text(sl, assessor, Cm(1.95), SH - Cm(1.3), Cm(14), Cm(0.6),
             size=11, bold=True, color=C_GOLD)
    add_text(sl, "Assessor de Investimentos — Braúna Investimentos", Cm(1.95), SH - Cm(0.72),
             Cm(16), Cm(0.5), size=8.5, color=C_LGRAY)
    add_text(sl, "Documento confidencial · Uso exclusivo do cliente · Não constitui recomendação formal de investimento",
             SW - Cm(18), SH - Cm(0.72), Cm(17), Cm(0.5), size=7.5, color=C_GRAY, align=PP_ALIGN.RIGHT)

# ── SLIDE 2: AGENDA ───────────────────────────────────────────────────────────
def s_agenda(prs, d, agenda_items):
    sl = new_slide(prs); bg(sl)
    header(sl, "AGENDA DA REUNIÃO", f"Apresentação — {d.get('nome_cliente','')} · {d.get('data_ref','')}")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    nome   = d.get("nome_cliente","")
    perfil = str(d.get("perfil","")).capitalize()
    pat    = fmt(d.get("patrimonio",0))
    data_r = d.get("data_ref","")

    # Card de abertura com contexto da reunião
    add_rect(sl, MARGIN, Cm(2.85), SW - Cm(1.4), Cm(0.06), C_GOLD)
    add_rect(sl, MARGIN, Cm(2.91), SW - Cm(1.4), Cm(0.72), C_CARD2, C_GRAY, 0.3)
    add_text(sl, f"Reunião de revisão de carteira  ·  {nome}  ·  Perfil {perfil}  ·  Patrimônio {pat}  ·  Referência {data_r}",
             MARGIN + Cm(0.4), Cm(2.98), SW - Cm(2.2), Cm(0.56),
             size=10, color=C_GOLD, bold=True)

    # Descrições detalhadas por tópico de agenda
    _SUBS = {
        "Cenário Global":    "Panorama macro internacional — Fed, BCE, China e impactos esperados",
        "Brasil & HP":       "Selic, IPCA, juro real e posicionamento do Head de Produtos Levante",
        "Patrimônio":        "Evolução do patrimônio, rentabilidade mensal, anual e em 12/24 meses",
        "Composição":        "Distribuição atual por classe de ativo e valor financeiro alocado",
        "Carteira vs. Modelo": "Aderência ao perfil — quais classes estão dentro, acima ou abaixo",
        "Desvios":           "Classes fora do modelo e o que resgatar ou aportar para realinhar",
        "Renda Variável":    "Ações e FIIs presentes na carteira — tickers e % de alocação",
        "Modelo de Servir":  "Score dos 6 pilares de relacionamento e pilares críticos pendentes",
        "Sugestões":         "Produtos recomendados pelo Head de Produtos para o seu perfil",
        "Cross Sell":        "Soluções Braúna ainda não ativadas — oportunidades de aprofundamento",
        "Resumo Executivo":  "Síntese dos principais indicadores — rentabilidade, desvios e score",
        "Próximos Passos":   "Encaminhamentos acordados com prazos e responsáveis definidos",
    }

    col_w = (SW - Cm(2)) / 2 - Cm(0.3)
    cx1, cx2 = MARGIN, MARGIN + col_w + Cm(0.6)
    mid = math.ceil(len(agenda_items)/2)

    for col, (cx, items) in enumerate([(cx1, agenda_items[:mid]), (cx2, agenda_items[mid:])]):
        for i, (num, lbl, sub) in enumerate(items):
            ry = Cm(3.9) + i * Cm(1.9)
            add_rect(sl, cx, ry, col_w, Cm(1.78), C_CARD, C_GRAY, 0.3)
            add_rect(sl, cx, ry, Cm(1.3), Cm(1.78), C_GOLD)
            add_text(sl, str(num), cx, ry + Cm(0.4), Cm(1.3), Cm(0.9),
                     size=14, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
            add_text(sl, lbl, cx + Cm(1.5), ry + Cm(0.15), col_w - Cm(1.7), Cm(0.72),
                     size=12, bold=True, color=C_WHITE)
            sub_det = _SUBS.get(lbl, sub)
            add_text(sl, sub_det, cx + Cm(1.5), ry + Cm(0.9), col_w - Cm(1.7), Cm(0.65),
                     size=8.5, color=C_LGRAY)

# ── SLIDE 3: CENÁRIO GLOBAL ───────────────────────────────────────────────────
def s_cenario_global(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "CENÁRIO GLOBAL", "Panorama macroeconômico internacional — Levante Asset")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    cenario    = d.get("cenario_macro", {})
    global_txt = cenario.get("global", "Informação não disponível.")
    vieses     = cenario.get("vieses", {})
    sinais     = cenario.get("sinais", [])

    VCOR = {"positivo": C_GREEN, "neutro": C_AMBER, "negativo": C_RED}
    VIC  = {"positivo": "▲ Positivo", "neutro": "→ Neutro", "negativo": "▼ Negativo"}

    # ── Bloco narrativo principal ──────────────────────────────────────────────
    add_rect(sl, MARGIN, Cm(3.0), SW - Cm(1.4), Cm(0.06), C_GOLD)
    add_rect(sl, MARGIN, Cm(3.06), SW - Cm(1.4), Cm(2.7), C_CARD, C_GRAY, 0.3)
    add_text(sl, "ANÁLISE MACROECONÔMICA GLOBAL", MARGIN + Cm(0.4), Cm(3.22),
             Cm(20), Cm(0.5), size=8, bold=True, color=C_GOLD)
    add_text(sl, global_txt, MARGIN + Cm(0.4), Cm(3.82), SW - Cm(2.2), Cm(1.8),
             size=11, color=C_WHITE, wrap=True)

    # ── 3 cards de regiões ────────────────────────────────────────────────────
    regioes = [
        ("Estados Unidos",  "Fed mantém postura restritiva. Mercado de trabalho resiliente sustenta consumo.",  "cautela"),
        ("Europa / BCE",    "BCE inicia cortes graduais. Atividade fraca na Alemanha pressiona zona do euro.",   "neutro"),
        ("Ásia / China",    "China retoma crescimento moderado. Estímulos fiscais suportam demanda interna.",    "positivo"),
    ]
    # Tenta extrair contexto do global_txt para enriquecer
    gtl = global_txt.lower()
    if "fed" in gtl or "estados unidos" in gtl or "americana" in gtl:
        sent_us = "cautela" if any(x in gtl for x in ["hawkish","cautela","restrictiv"]) else "positivo"
    else:
        sent_us = "neutro"
    regioes[0] = (regioes[0][0], regioes[0][1], sent_us)

    VCOR2 = {"positivo": C_GREEN, "cautela": C_AMBER, "neutro": C_LGRAY}
    VIC2  = {"positivo": "▲ Positivo", "cautela": "→ Cautela", "neutro": "→ Neutro"}
    rw = (SW - Cm(1.4)) / 3 - Cm(0.2)
    for i, (reg, desc, sent) in enumerate(regioes):
        rx = MARGIN + i * (rw + Cm(0.2))
        cor_r = VCOR2.get(sent, C_LGRAY)
        add_rect(sl, rx, Cm(6.0), rw, Cm(2.1), C_CARD2, cor_r, 0.4)
        add_rect(sl, rx, Cm(6.0), rw, Cm(0.15), cor_r)
        add_text(sl, reg, rx + Cm(0.3), Cm(6.22), rw - Cm(0.6), Cm(0.55),
                 size=10, bold=True, color=C_WHITE)
        add_text(sl, VIC2.get(sent,"→"), rx + Cm(0.3), Cm(6.82), rw - Cm(0.6), Cm(0.45),
                 size=9, bold=True, color=cor_r)
        add_text(sl, desc, rx + Cm(0.3), Cm(7.32), rw - Cm(0.6), Cm(0.65),
                 size=8.5, color=C_LGRAY, wrap=True)

    # ── Sinais de mercado (badges) ─────────────────────────────────────────────
    if sinais:
        add_text(sl, "SINAIS DE MERCADO", MARGIN, Cm(8.3), SW, Cm(0.5),
                 size=8, bold=True, color=C_LGRAY)
        bx = MARGIN; by = Cm(8.9)
        for sinal in sinais[:8]:
            lbl = str(sinal).strip()
            sw_badge = Cm(len(lbl) * 0.22 + 0.8)
            add_rect(sl, bx, by, sw_badge, Cm(0.55), C_CARD2, C_GRAY, 0.3)
            add_text(sl, lbl, bx + Cm(0.25), by + Cm(0.07), sw_badge - Cm(0.4),
                     Cm(0.42), size=8, color=C_LGRAY)
            bx += sw_badge + Cm(0.2)
            if bx > SW - Cm(3): bx = MARGIN; by += Cm(0.7)
        vieses_y = by + Cm(0.8)
    else:
        vieses_y = Cm(8.9)

    # ── Vieses por classe ─────────────────────────────────────────────────────
    add_text(sl, "VIESES POR CLASSE DE ATIVO — POSICIONAMENTO HP", MARGIN, vieses_y - Cm(0.55),
             SW - Cm(1.4), Cm(0.5), size=8, bold=True, color=C_GOLD)

    items = list(vieses.items())
    n     = max(len(items), 1)
    vw    = (SW - Cm(1.4)) / n - Cm(0.18)
    vcard_h = SH - vieses_y - Cm(0.75)

    for i, (cls, v) in enumerate(items):
        vx  = MARGIN + i * (vw + Cm(0.18))
        cor = VCOR.get(v, C_LGRAY)
        add_rect(sl, vx, vieses_y, vw, vcard_h, C_CARD, cor, 0.5)
        add_rect(sl, vx, vieses_y, vw, Cm(0.18), cor)
        add_text(sl, CLS_LABEL.get(cls, cls), vx + Cm(0.2), vieses_y + Cm(0.32),
                 vw - Cm(0.4), Cm(0.65), size=9, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)
        add_text(sl, VIC.get(v, "→"), vx + Cm(0.2), vieses_y + Cm(1.05),
                 vw - Cm(0.4), Cm(0.6), size=9, bold=True, color=cor, align=PP_ALIGN.CENTER)

# ── SLIDE 4: CENÁRIO BRASIL & HP ─────────────────────────────────────────────
def s_cenario_brasil(prs, d):
    sl = new_slide(prs); bg(sl)
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

    juro_real = round(selic - ipca, 2) if selic and ipca else None

    # ── Linha 1: 4 métricas macro ─────────────────────────────────────────────
    metricas_br = [
        ("SELIC META",  f"{selic:.2f}%"     if selic     else "—",  C_GOLD),
        ("IPCA 12M",    f"{ipca:.2f}%"      if ipca      else "—",  C_AMBER if ipca and ipca > 5 else C_GREEN),
        ("JURO REAL",   f"{juro_real:.2f}%" if juro_real else "—",  C_GREEN if juro_real and juro_real > 6 else C_AMBER),
        ("SPREAD REAL", f"+{max(0,(juro_real or 0)-6):.2f}%p acima NTN-B" if juro_real else "—", C_LGRAY),
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

    # ── Coluna esquerda: CENÁRIO BRASIL ───────────────────────────────────────
    add_rect(sl, cx1, y0, col_w, Cm(0.6), C_DGRAY, C_GRAY, 0.3)
    add_rect(sl, cx1, y0, Cm(0.18), Cm(0.6), C_LGRAY)
    add_text(sl, "🇧🇷  CENÁRIO BRASIL", cx1 + Cm(0.4), y0 + Cm(0.1),
             col_w - Cm(0.6), Cm(0.45), size=10, bold=True, color=C_WHITE)

    add_rect(sl, cx1, y0 + Cm(0.6), col_w, Cm(5.5), C_CARD, C_GRAY, 0.3)

    # Texto principal brasil
    add_text(sl, brasil_txt,
             cx1 + Cm(0.4), y0 + Cm(0.85), col_w - Cm(0.8), Cm(3.5),
             size=11, color=C_WHITE, wrap=True)

    # Sub-bloco: indicadores chave dentro do card
    add_rect(sl, cx1 + Cm(0.3), y0 + Cm(4.55), col_w - Cm(0.6), Cm(0.04), C_GRAY)
    add_text(sl, "INDICADORES CHAVE", cx1 + Cm(0.3), y0 + Cm(4.65),
             col_w - Cm(0.6), Cm(0.4), size=7.5, bold=True, color=C_LGRAY)
    kpis = []
    if selic:   kpis.append(f"Selic: {selic:.2f}%")
    if ipca:    kpis.append(f"IPCA 12M: {ipca:.2f}%")
    if juro_real: kpis.append(f"Juro real: {juro_real:.2f}%")
    kpis += ["Risco fiscal: elevado", "Câmbio: volatilidade moderada"]
    for j, kpi in enumerate(kpis[:4]):
        kx = cx1 + Cm(0.3) + (j % 2) * ((col_w - Cm(0.6)) / 2)
        ky = y0 + Cm(5.15) + (j // 2) * Cm(0.55)
        add_rect(sl, kx, ky, (col_w - Cm(0.8)) / 2, Cm(0.48), C_CARD2, C_GRAY, 0.3)
        add_text(sl, kpi, kx + Cm(0.2), ky + Cm(0.06),
                 (col_w - Cm(0.8)) / 2 - Cm(0.3), Cm(0.38), size=8.5, color=C_LGRAY)

    # ── Coluna direita: POSICIONAMENTO HP ────────────────────────────────────
    add_rect(sl, cx2, y0, col_w, Cm(0.6), C_CARD2, C_GOLD, 0.4)
    add_rect(sl, cx2, y0, col_w, Cm(0.15), C_GOLD)
    add_text(sl, "★  POSICIONAMENTO HEAD DE PRODUTOS", cx2 + Cm(0.3), y0 + Cm(0.12),
             col_w - Cm(0.5), Cm(0.45), size=10, bold=True, color=C_GOLD)

    add_rect(sl, cx2, y0 + Cm(0.6), col_w, Cm(3.0), C_CARD2, C_GOLD, 0.3)
    add_text(sl, pos_txt,
             cx2 + Cm(0.4), y0 + Cm(0.85), col_w - Cm(0.8), Cm(2.65),
             size=11, color=C_WHITE, wrap=True)

    # Tabela de vieses por classe
    add_rect(sl, cx2, y0 + Cm(3.6), col_w, Cm(0.5), C_DGRAY, C_GOLD, 0.3)
    add_text(sl, "VIÉS POR CLASSE DE ATIVO", cx2 + Cm(0.3), y0 + Cm(3.68),
             col_w - Cm(0.5), Cm(0.38), size=8, bold=True, color=C_GOLD)

    items_v = [(c, v) for c, v in vieses.items() if c in CATS]
    n_v = len(items_v)
    if n_v:
        row_h_v = Cm(0.72)
        for j, (cls, v) in enumerate(items_v):
            ry = y0 + Cm(4.15) + j * row_h_v
            cor = VCOR.get(v, C_LGRAY)
            fundo = C_CARD if j % 2 == 0 else C_CARD3
            add_rect(sl, cx2, ry, col_w, row_h_v - Cm(0.05), fundo)
            add_rect(sl, cx2, ry, Cm(0.2), row_h_v - Cm(0.05), cor)
            add_text(sl, CLS_LABEL.get(cls, cls), cx2 + Cm(0.4), ry + Cm(0.1),
                     col_w - Cm(2.2), Cm(0.52), size=10, color=C_WHITE)
            add_text(sl, f"{VIC.get(v,'→')} {v.capitalize()}",
                     cx2 + col_w - Cm(2.0), ry + Cm(0.1), Cm(1.8), Cm(0.52),
                     size=10, bold=True, color=cor, align=PP_ALIGN.RIGHT)

    # ── Barra de implicação para a carteira (largura total) ──────────────────
    vieses_pos = [CLS_LABEL.get(c, c) for c, v in vieses.items() if v == "positivo"]
    vieses_neg = [CLS_LABEL.get(c, c) for c, v in vieses.items() if v == "negativo"]
    partes = []
    if vieses_pos: partes.append(f"Favorecidas: {', '.join(vieses_pos)}")
    if vieses_neg: partes.append(f"Cautela: {', '.join(vieses_neg)}")
    if juro_real and juro_real > 7:
        partes.append(f"Juro real de {juro_real:.1f}% sustenta renda fixa conservadora")
    elif juro_real and juro_real < 5:
        partes.append("Juro real baixo favorece ativos de risco")
    if partes:
        impl = "Implicação para a carteira: " + " · ".join(partes) + "."
        add_caixa_texto(sl, impl, SH - Cm(2.8), cor_borda=C_GOLD, cor_bg=C_CARD2)

# ── SLIDE 5: PATRIMÔNIO & RENTABILIDADE ───────────────────────────────────────
def s_patrimonio(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "PATRIMÔNIO & RENTABILIDADE", "Evolução e desempenho da carteira")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    pat  = d.get("patrimonio", 0)
    rent = d.get("rent", {})
    pr   = rent.get("portfolio", {}) if isinstance(rent, dict) else {}
    cr   = rent.get("cdi", {}) if isinstance(rent, dict) else {}

    # Cards de métricas — linha 1
    metricas = [
        ("PATRIMÔNIO TOTAL", fmt(pat), C_GOLD),
        ("RENTAB. MÊS", f"{pr.get('mes',0):.2f}%", pct_cor(pr.get('mes',0))),
        ("RENTAB. ANO", f"{pr.get('ano',0):.2f}%", pct_cor(pr.get('ano',0))),
        ("RENTAB. 12M", f"{pr.get('12m',0):.2f}%", pct_cor(pr.get('12m',0))),
    ]
    mw = (SW - Cm(1.4)) / 4 - Cm(0.25)
    for i, (lbl, val, cor) in enumerate(metricas):
        mx = MARGIN + i * (mw + Cm(0.25))
        add_rect(sl, mx, Cm(3.1), mw, Cm(2.0), C_CARD, C_GRAY, 0.3)
        add_rect(sl, mx, Cm(3.1), mw, Cm(0.12), cor)
        add_text(sl, lbl, mx + Cm(0.3), Cm(3.35), mw - Cm(0.6), Cm(0.55),
                 size=7.5, color=C_LGRAY)
        add_text(sl, val, mx + Cm(0.3), Cm(3.95), mw - Cm(0.6), Cm(0.9),
                 size=17, bold=True, color=cor)

    # Tabela comparativa Portfolio vs CDI
    periodos = ["Mês","Ano","12 Meses","24 Meses"]
    keys     = ["mes","ano","12m","24m"]
    add_text(sl, "RENTABILIDADE COMPARATIVA", MARGIN, Cm(5.6), SW, Cm(0.55),
             size=9, bold=True, color=C_LGRAY)

    tw = (SW - Cm(1.4)) / (len(periodos)+1) - Cm(0.1)
    hdrs = [""] + periodos
    for i, h in enumerate(hdrs):
        hx = MARGIN + i * (tw + Cm(0.1))
        add_rect(sl, hx, Cm(6.2), tw, Cm(0.7), C_CARD2)
        add_text(sl, h, hx, Cm(6.25), tw, Cm(0.6), size=9, bold=True,
                 color=C_GOLD if i>0 else C_LGRAY, align=PP_ALIGN.CENTER)

    linhas = [
        ("Portfolio", [pr.get(k,0) for k in keys], C_WHITE),
        ("CDI",       [cr.get(k,0) for k in keys], C_LGRAY),
    ]
    if cr.get("12m"):
        pct_12 = round(pr.get("12m",0)/cr.get("12m")*100,1)
        pct_24 = round(pr.get("24m",0)/cr.get("24m")*100,1) if cr.get("24m") else 0
        pct_mes = round(pr.get("mes",0)/cr.get("mes")*100,1) if cr.get("mes") else 0
        pct_ano = round(pr.get("ano",0)/cr.get("ano")*100,1) if cr.get("ano") else 0
        linhas.append(("% CDI", [pct_mes, pct_ano, pct_12, pct_24], C_GOLD))

    for j, (lbl, vals, cor) in enumerate(linhas):
        ry = Cm(6.95) + j * Cm(0.85)
        fundo = C_CARD if j%2==0 else C_CARD3
        add_rect(sl, MARGIN, ry, SW-Cm(1.4), Cm(0.82), fundo)
        lx = MARGIN
        add_text(sl, lbl, lx, ry+Cm(0.12), tw, Cm(0.6), size=10, bold=True,
                 color=cor, align=PP_ALIGN.CENTER)
        for i, v in enumerate(vals):
            vx = MARGIN + (i+1) * (tw + Cm(0.1))
            vc = pct_cor(v) if lbl in ("Portfolio","CDI") else (C_GREEN if v>=80 else (C_AMBER if v>=60 else C_RED))
            add_text(sl, f"{v:.2f}%" if lbl!="% CDI" else f"{v:.0f}%",
                     vx, ry+Cm(0.12), tw, Cm(0.6), size=10, color=vc,
                     align=PP_ALIGN.CENTER)

    # Estatísticas extras
    historico = d.get("historico_resumo", [])
    add_text(sl, "24 MESES", MARGIN, Cm(9.65), SW, Cm(0.55), size=9, bold=True, color=C_LGRAY)
    stats = [
        ("Ganho 24M", fmt(pat * pr.get("24m",0)/100) if pat else "—", C_GREEN),
        ("Meses Positivos", str(d.get("meses_positivos","—")), C_GREEN),
        ("Meses Negativos", str(d.get("meses_negativos","—")), C_RED),
        ("Volatilidade 12M", str(d.get("volatilidade","—")), C_LGRAY),
    ]
    sw2 = (SW - Cm(1.4)) / 4 - Cm(0.25)
    for i, (lbl, val, cor) in enumerate(stats):
        sx = MARGIN + i * (sw2 + Cm(0.25))
        add_rect(sl, sx, Cm(10.2), sw2, Cm(1.6), C_CARD, C_DGRAY, 0.3)
        add_text(sl, lbl, sx+Cm(0.3), Cm(10.3), sw2-Cm(0.6), Cm(0.5), size=8, color=C_LGRAY)
        add_text(sl, val, sx+Cm(0.3), Cm(10.85), sw2-Cm(0.6), Cm(0.7), size=14, bold=True, color=cor)

    # Narrativa de desempenho
    nome = d.get("nome_cliente", "O cliente")
    r_mes = pr.get("mes", 0); r_ano = pr.get("ano", 0); r_12 = pr.get("12m", 0)
    c_12  = cr.get("12m", 1) or 1
    pct_12 = round(r_12 / c_12 * 100, 0)
    perf_txt = "acima" if pct_12 >= 100 else "abaixo"
    q_cdi = "expressivamente acima" if pct_12 >= 110 else ("acima" if pct_12 >= 90 else ("próximo" if pct_12 >= 75 else "abaixo"))
    narrativa = (
        f"{nome} encerrou o período com patrimônio de {fmt(pat)}, registrando rentabilidade de "
        f"{r_mes:.2f}% no mês e {r_ano:.2f}% no ano. Em 12 meses, o portfólio rendeu {r_12:.2f}% — "
        f"equivalente a {pct_12:.0f}% do CDI, desempenho {q_cdi} do referencial. "
        f"{'O resultado demonstra boa aderência à estratégia definida.' if pct_12 >= 80 else 'Este resultado merece atenção e revisão da estratégia de alocação.'}"
    ) if pat else "Sem dados de rentabilidade disponíveis para este período."
    add_caixa_texto(sl, narrativa, Cm(12.1),
                    cor_borda=C_GREEN if pct_12 >= 80 else C_AMBER,
                    cor_bg=C_CARD2)

# ── SLIDE 6: COMPOSIÇÃO DA CARTEIRA ──────────────────────────────────────────
def s_composicao(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "COMPOSIÇÃO DA CARTEIRA", "Alocação atual por classe de ativo")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    comp  = d.get("composicao", {})
    pat   = d.get("patrimonio", 0)

    top_y = Cm(3.1)
    tw_lbl = Cm(5.5)
    tw_val = Cm(2.2)
    tw_rs  = Cm(4.0)
    bar_x  = MARGIN + tw_lbl + tw_val + tw_rs + Cm(0.6)
    bar_w  = SW - bar_x - MARGIN

    # Cabeçalhos
    add_text(sl, "CLASSE", MARGIN, top_y, tw_lbl, Cm(0.5), size=8, bold=True, color=C_LGRAY)
    add_text(sl, "% CARTEIRA", MARGIN+tw_lbl, top_y, tw_val, Cm(0.5), size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.RIGHT)
    add_text(sl, "R$ ALOCADO", MARGIN+tw_lbl+tw_val+Cm(0.3), top_y, tw_rs, Cm(0.5), size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.RIGHT)
    add_text(sl, "PARTICIPAÇÃO VISUAL", bar_x, top_y, bar_w, Cm(0.5), size=8, bold=True, color=C_LGRAY)

    cats_com_valor = [(c, comp.get(c,0)) for c in CATS if comp.get(c,0) > 0]
    max_v = max((v for _,v in cats_com_valor), default=1) or 1
    row_h = Cm(0.92)

    for i, (cat, v) in enumerate(cats_com_valor):
        ry = top_y + Cm(0.65) + i * row_h
        fundo = C_CARD if i%2==0 else C_CARD3
        add_rect(sl, MARGIN, ry, SW-Cm(1.4), row_h - Cm(0.05), fundo)
        cor = CLS_COR.get(cat, C_LGRAY)
        add_rect(sl, MARGIN, ry, Cm(0.18), row_h - Cm(0.05), cor)
        add_text(sl, CLS_LABEL.get(cat,cat), MARGIN+Cm(0.35), ry+Cm(0.2), tw_lbl-Cm(0.4), Cm(0.6), size=10.5, color=C_WHITE)
        add_text(sl, f"{v:.1f}%", MARGIN+tw_lbl, ry+Cm(0.2), tw_val, Cm(0.6), size=10.5, bold=True, color=cor, align=PP_ALIGN.RIGHT)
        val_r = fmt(pat * v / 100) if pat else "—"
        add_text(sl, val_r, MARGIN+tw_lbl+tw_val+Cm(0.3), ry+Cm(0.2), tw_rs, Cm(0.6), size=10, color=C_LGRAY, align=PP_ALIGN.RIGHT)
        # Barra
        add_rect(sl, bar_x, ry+Cm(0.25), bar_w * (v/max_v), Cm(0.42), cor)
        add_text(sl, f"{v:.1f}%", bar_x + bar_w*(v/max_v) + Cm(0.15), ry+Cm(0.22), Cm(1.5), Cm(0.5), size=8, color=C_LGRAY)

    # Narrativa de composição
    if cats_com_valor:
        principal_cat, principal_v = cats_com_valor[0]
        principal_nome = CLS_LABEL.get(principal_cat, principal_cat)
        n_classes = len(cats_com_valor)
        diversificacao = "bem diversificada" if n_classes >= 5 else ("moderadamente diversificada" if n_classes >= 3 else "concentrada")
        narrativa_comp = (
            f"A carteira está {diversificacao}, distribuída em {n_classes} classes de ativos. "
            f"A maior exposição é em {principal_nome} ({principal_v:.1f}%"
            f"{f', equivalente a {fmt(pat * principal_v / 100)}' if pat else ''}"
            f"). {'A diversificação entre classes reduz o risco idiossincrático e amplia as fontes de retorno.' if n_classes >= 4 else 'Recomenda-se avaliar oportunidades de diversificação em outras classes de ativos.'}"
        )
        add_caixa_texto(sl, narrativa_comp, top_y + Cm(0.65) + len(cats_com_valor) * row_h + Cm(0.2),
                        cor_borda=C_GOLD, cor_bg=C_CARD2)

# ── SLIDE 7: CARTEIRA vs MODELO ───────────────────────────────────────────────
def s_vs_modelo(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "CARTEIRA vs. MODELO", "Comparativo entre alocação atual e perfil de investidor")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    comp   = d.get("composicao", {})
    modelo = d.get("modelo_hp", {})

    tw_lbl = Cm(5.0)
    tw_num = Cm(2.2)
    top_y  = Cm(3.1)

    hdrs = ["CLASSE","ATUAL","MODELO","DESVIO","SITUAÇÃO"]
    xs   = [MARGIN, MARGIN+tw_lbl, MARGIN+tw_lbl+tw_num, MARGIN+tw_lbl+tw_num*2,
            MARGIN+tw_lbl+tw_num*3]
    for i, h in enumerate(hdrs):
        add_text(sl, h, xs[i], top_y, tw_lbl if i==0 else tw_num, Cm(0.5),
                 size=8, bold=True, color=C_LGRAY, align=PP_ALIGN.LEFT if i==0 else PP_ALIGN.CENTER)

    cats_visiveis = [c for c in CATS if comp.get(c,0)>0 or modelo.get(c,0)>0]
    row_h = Cm(0.9)
    for i, cat in enumerate(cats_visiveis):
        atual  = comp.get(cat,0)
        mod    = modelo.get(cat,0)
        dev    = round(atual - mod, 1)
        ry     = top_y + Cm(0.65) + i * row_h
        cor_cat= CLS_COR.get(cat, C_LGRAY)
        add_rect(sl, MARGIN, ry, SW-Cm(1.4), row_h-Cm(0.05), C_CARD if i%2==0 else C_CARD3)
        add_rect(sl, MARGIN, ry, Cm(0.18), row_h-Cm(0.05), cor_cat)
        add_text(sl, CLS_LABEL.get(cat,cat), xs[0]+Cm(0.3), ry+Cm(0.2), tw_lbl-Cm(0.4), Cm(0.6), size=10, color=C_WHITE)
        add_text(sl, f"{atual:.1f}%", xs[1], ry+Cm(0.2), tw_num, Cm(0.6), size=10, color=C_WHITE, align=PP_ALIGN.CENTER)
        add_text(sl, f"{mod:.1f}%", xs[2], ry+Cm(0.2), tw_num, Cm(0.6), size=10, color=C_GOLD, align=PP_ALIGN.CENTER)
        cor_d = C_RED if dev < -3 else (C_GREEN if dev > 3 else C_LGRAY)
        add_text(sl, f"{dev:+.1f}%", xs[3], ry+Cm(0.2), tw_num, Cm(0.6),
                 size=10, bold=abs(dev)>3, color=cor_d, align=PP_ALIGN.CENTER)
        sit = "⚠ Abaixo" if dev < -3 else ("⚠ Acima" if dev > 3 else "✓ OK")
        cor_sit = C_RED if dev < -3 else (C_AMBER if dev > 3 else C_GREEN)
        add_text(sl, sit, xs[4], ry+Cm(0.2), tw_num, Cm(0.6),
                 size=9.5, bold=abs(dev)>3, color=cor_sit, align=PP_ALIGN.CENTER)

    # Parágrafo narrativo após a tabela
    n_total  = len(cats_visiveis)
    n_ok     = sum(1 for c in cats_visiveis if abs(comp.get(c,0) - modelo.get(c,0)) <= 3)
    n_acima  = sum(1 for c in cats_visiveis if comp.get(c,0) - modelo.get(c,0) > 3)
    n_abaixo = sum(1 for c in cats_visiveis if comp.get(c,0) - modelo.get(c,0) < -3)
    maiores_dev = sorted(
        [(c, abs(comp.get(c,0) - modelo.get(c,0))) for c in cats_visiveis if abs(comp.get(c,0) - modelo.get(c,0)) > 3],
        key=lambda x: x[1], reverse=True
    )
    maiores_txt = ", ".join(f"{CLS_LABEL.get(c,c)} ({v:+.1f}%p)" for c,v in maiores_dev[:3]) if maiores_dev else "nenhuma"
    narr_vs = (
        f"De {n_total} classes analisadas, {n_ok} estão dentro do modelo, "
        f"{n_acima} {'está acima' if n_acima==1 else 'estão acima'} e "
        f"{n_abaixo} {'está abaixo' if n_abaixo==1 else 'estão abaixo'}. "
        f"As classes com maior desvio são: {maiores_txt}."
    )
    table_bottom = top_y + Cm(0.65) + len(cats_visiveis) * row_h + Cm(0.2)
    add_caixa_texto(sl, narr_vs, table_bottom, cor_borda=C_AMBER if (n_acima+n_abaixo) > 0 else C_GREEN, cor_bg=C_CARD2)

# ── SLIDE 8: DESVIOS — O QUE AJUSTAR ─────────────────────────────────────────
def s_desvios(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "DESVIOS DA CARTEIRA", "O que precisa ser ajustado para atingir o modelo")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    desvios = d.get("desvios", [])
    pat = d.get("patrimonio", 0)

    exc = [x for x in desvios if x.get("desvio_pp",x.get("desvio",0)) > 0]
    def_ = [x for x in desvios if x.get("desvio_pp",x.get("desvio",0)) < 0]

    if not desvios:
        add_rect(sl, MARGIN, Cm(4.0), SW-Cm(1.4), Cm(4.0), C_CARD, C_GREEN, 0.5)
        add_text(sl, "✓  Carteira dentro do modelo", MARGIN+Cm(1), Cm(5.5), SW-Cm(3), Cm(1.5),
                 size=18, bold=True, color=C_GREEN, align=PP_ALIGN.CENTER)
        add_text(sl, "Nenhum desvio significativo identificado. Carteira alinhada ao perfil.",
                 MARGIN+Cm(1), Cm(7.0), SW-Cm(3), Cm(0.8), size=11, color=C_LGRAY, align=PP_ALIGN.CENTER)
        return

    col_w = (SW - Cm(2)) / 2 - Cm(0.3)
    cx1, cx2 = MARGIN, MARGIN + col_w + Cm(0.6)
    row_h = Cm(1.55)

    add_text(sl, "REDUZIR / RESGATAR", cx1, Cm(3.1), col_w, Cm(0.55), size=9, bold=True, color=C_RED)
    add_text(sl, "AUMENTAR / APORTAR", cx2, Cm(3.1), col_w, Cm(0.55), size=9, bold=True, color=C_GREEN)

    for col, items, cor in [(cx1, exc, C_RED), (cx2, def_, C_GREEN)]:
        for i, dev in enumerate(items[:7]):
            ry = Cm(3.75) + i * row_h
            cat   = dev.get("classe","")
            desp  = abs(dev.get("desvio_pp", dev.get("desvio",0)))
            atual = dev.get("atual",0)
            mod   = dev.get("modelo",0)
            val   = pat * desp / 100 if pat else 0
            add_rect(sl, col, ry, col_w, row_h-Cm(0.1), C_CARD, cor, 0.3)
            add_rect(sl, col, ry, Cm(0.18), row_h-Cm(0.1), cor)
            add_text(sl, CLS_LABEL.get(cat,cat), col+Cm(0.4), ry+Cm(0.12),
                     col_w-Cm(2.8), Cm(0.65), size=11, bold=True, color=C_WHITE)
            add_text(sl, f"{desp:.1f}%", col+col_w-Cm(1.6), ry+Cm(0.12),
                     Cm(1.4), Cm(0.65), size=11, bold=True, color=cor, align=PP_ALIGN.RIGHT)
            add_text(sl, f"Atual {atual:.1f}%  →  Modelo {mod:.1f}%  ·  {fmt(val) if val else '—'}",
                     col+Cm(0.4), ry+Cm(0.85), col_w-Cm(0.6), Cm(0.5), size=8.5, color=C_LGRAY)

    # Narrativa de desvios
    n_exc = len(exc); n_def = len(def_)
    if exc or def_:
        maior_exc = f"{CLS_LABEL.get(exc[0].get('classe',''), '')} (+{abs(exc[0].get('desvio_pp', exc[0].get('desvio',0))):.1f}%)" if exc else None
        maior_def = f"{CLS_LABEL.get(def_[0].get('classe',''), '')} (-{abs(def_[0].get('desvio_pp', def_[0].get('desvio',0))):.1f}%)" if def_ else None
        partes = []
        if maior_exc: partes.append(f"A classe com maior excesso é {maior_exc}, que deve ser parcialmente resgatada")
        if maior_def: partes.append(f"{'e a' if partes else 'A'} maior sub-alocação está em {maior_def}, recomendando-se aporte adicional")
        narrativa_dev = ". ".join(partes) + (
            f". No total, {n_exc + n_def} {'ajuste é necessário' if n_exc+n_def==1 else 'ajustes são necessários'} para realinhar a carteira ao perfil do investidor."
            if partes else ""
        )
        add_caixa_texto(sl, narrativa_dev, SH - Cm(2.7),
                        cor_borda=C_AMBER, cor_bg=C_CARD2)

# ── SLIDE 9: AÇÕES & FIIs ─────────────────────────────────────────────────────
def s_rv(prs, d):
    sl = new_slide(prs); bg(sl)
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
            add_text(sl, "Nenhum ativo desta classe na carteira", cx+Cm(0.4), Cm(4.2),
                     col_w-Cm(0.8), Cm(0.7), size=9.5, color=C_LGRAY)
            return
        hdrs = ["TICKER","%"]
        hw   = [col_w*0.55, col_w*0.4]
        hx   = [cx, cx + col_w*0.55]
        add_rect(sl, cx, Cm(3.75), col_w, Cm(0.65), C_CARD2)
        for j, h in enumerate(hdrs):
            add_text(sl, h, hx[j]+Cm(0.2), Cm(3.8), hw[j]-Cm(0.2), Cm(0.55), size=8, bold=True, color=C_LGRAY)
        row_h = Cm(0.75)
        for k, a in enumerate(items[:10]):
            ry = Cm(4.45) + k * row_h
            fundo = C_CARD if k%2==0 else C_CARD3
            add_rect(sl, cx, ry, col_w, row_h, fundo)
            ticker = a.get("ticker","")
            perc   = a.get("perc_carteira", a.get("perc",0))
            add_text(sl, ticker, cx+Cm(0.2), ry+Cm(0.1), hw[0]-Cm(0.2), Cm(0.58), size=10, bold=True, color=cor)
            add_text(sl, f"{perc:.2f}%", cx+col_w*0.55+Cm(0.2), ry+Cm(0.1), hw[1]-Cm(0.2), Cm(0.58), size=10, color=C_LGRAY)

    render_tbl(cx1, "AÇÕES", acoes, C_GREEN)
    render_tbl(cx2, "FUNDOS IMOBILIÁRIOS (FIIs)", fiis, C_BLUE)

    # Parágrafo narrativo — sempre presente
    perfil  = str(d.get("perfil","")).lower()
    modelo  = d.get("modelo_hp", {})
    comp    = d.get("composicao", {})
    meta_rv   = modelo.get("acoes", 0)
    meta_fiis = modelo.get("fiis", 0)
    total_rv   = comp.get("acoes", 0)
    total_fiis = comp.get("fiis", 0)
    partes_rv = []
    if acoes:
        partes_rv.append(
            f"A carteira possui exposição em {len(acoes)} {'ação' if len(acoes)==1 else 'ações'}, "
            f"com alocação total de {total_rv:.1f}% em Renda Variável."
        )
    else:
        partes_rv.append(
            f"O cliente não possui exposição a Renda Variável no momento. "
            f"O modelo {perfil.capitalize()} prevê {meta_rv:.1f}% em ações — oportunidade de alocação gradual."
        )
    if fiis:
        partes_rv.append(
            f"Fundos Imobiliários representam {total_fiis:.1f}% da carteira, "
            f"com {len(fiis)} {'fundo' if len(fiis)==1 else 'fundos'} na posição."
        )
    else:
        partes_rv.append(
            f"Sem FIIs na carteira. O modelo prevê {meta_fiis:.1f}% — "
            f"oportunidade de diversificação com geração de renda."
        )
    narr_rv = " ".join(partes_rv)
    add_caixa_texto(sl, narr_rv, SH - Cm(2.7),
                    cor_borda=C_GREEN if (acoes or fiis) else C_AMBER,
                    cor_bg=C_CARD2)

# ── SLIDE 10: MODELO DE SERVIR ────────────────────────────────────────────────
def s_modelo_servir(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "MODELO DE SERVIR", "Trilha de relacionamento e engajamento do cliente")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    checklist = d.get("checklist", {})
    score     = d.get("score_servir", 0)
    total     = 6

    PILARES = [
        ("open_investments",      "Open Investments",       "CRÍTICA", "🔗"),
        ("financial_planning",    "Financial Planning",     "CRÍTICA", "🎯"),
        ("ordem_enviada",         "Ordem Enviada",          "ALTA",    "📋"),
        ("conta_acessada",        "Conta Acessada",         "ALTA",    "📱"),
        ("xperformance",          "X-Performance",          "MÉDIA",   "📊"),
        ("atividade_relacionamento","Atividade Relacionamento","ALTA",  "🤝"),
    ]
    IMP_COR = {"CRÍTICA": C_RED, "ALTA": C_AMBER, "MÉDIA": C_LGRAY}

    # Score gauge
    pct_score = score / total if total else 0
    cor_score = C_GREEN if pct_score >= 0.8 else (C_AMBER if pct_score >= 0.5 else C_RED)
    add_rect(sl, MARGIN, Cm(3.1), SW-Cm(1.4), Cm(1.8), C_CARD, C_GRAY, 0.3)
    add_rect(sl, MARGIN, Cm(3.1), (SW-Cm(1.4)) * pct_score, Cm(1.8), cor_score)
    add_text(sl, f"Score: {score}/{total} pilares completos",
             MARGIN+Cm(0.5), Cm(3.4), SW-Cm(2), Cm(1.1), size=14, bold=True, color=C_BG if pct_score>0.3 else C_WHITE)

    # Cards de pilares
    n_cols = 3
    col_w  = (SW - Cm(1.4)) / n_cols - Cm(0.25)
    row_h  = Cm(2.5)
    for i, (pid, nome, imp, icone) in enumerate(PILARES):
        col = i % n_cols; row = i // n_cols
        cx  = MARGIN + col * (col_w + Cm(0.25))
        ry  = Cm(5.3) + row * (row_h + Cm(0.2))
        feito = bool(checklist.get(pid))
        cor_borda = C_GREEN if feito else IMP_COR.get(imp, C_GRAY)
        add_rect(sl, cx, ry, col_w, row_h, C_CARD, cor_borda, 0.5)
        if feito:
            add_rect(sl, cx, ry, col_w, Cm(0.15), C_GREEN)
        add_text(sl, icone+" "+nome, cx+Cm(0.3), ry+Cm(0.3), col_w-Cm(0.6), Cm(0.75),
                 size=11, bold=True, color=C_WHITE)
        add_text(sl, imp, cx+Cm(0.3), ry+Cm(1.1), col_w-Cm(0.6), Cm(0.5),
                 size=8, color=IMP_COR.get(imp, C_LGRAY))
        status_txt = "✓ Concluído" if feito else "Pendente"
        add_text(sl, status_txt, cx+Cm(0.3), ry+Cm(1.7), col_w-Cm(0.6), Cm(0.5),
                 size=9, bold=feito, color=C_GREEN if feito else C_RED)

    # Narrativa do modelo de servir
    pendentes = [nome for pid, nome, imp, icone in PILARES if not checklist.get(pid)]
    criticos  = [nome for pid, nome, imp, icone in PILARES if not checklist.get(pid) and imp == "CRÍTICA"]
    if score == 6:
        narrativa_ms = (
            f"Excelente! Todos os 6 pilares do Modelo de Servir estão concluídos. "
            f"O cliente está com engajamento máximo — menor risco de ruptura e maior potencial de cross sell. "
            f"Foco agora em manter a regularidade e aprofundar o relacionamento."
        )
        cor_ms = C_GREEN
    elif criticos:
        narrativa_ms = (
            f"{score}/6 pilares concluídos. Ainda pendentes: {', '.join(pendentes)}. "
            f"ATENÇÃO: {' e '.join(criticos)} {'é pilar crítico' if len(criticos)==1 else 'são pilares críticos'} — "
            f"sem {'ele' if len(criticos)==1 else 'eles'}, o assessor tem visão incompleta do patrimônio e dos objetivos do cliente. "
            f"Prioridade máxima na próxima interação."
        )
        cor_ms = C_RED
    else:
        narrativa_ms = (
            f"{score}/6 pilares concluídos. Itens pendentes: {', '.join(pendentes)}. "
            f"Completar esses pilares fortalece o vínculo com o cliente e reduz o risco de portabilidade."
        )
        cor_ms = C_AMBER
    add_caixa_texto(sl, narrativa_ms, SH - Cm(2.7), cor_borda=cor_ms, cor_bg=C_CARD2)

# ── SLIDE 11: SUGESTÕES ───────────────────────────────────────────────────────
def s_sugestoes(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "SUGESTÕES DE REALOCAÇÃO",
           "Produtos recomendados pelo Head de Produtos — Levante Asset")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    sugs = d.get("sugestoes_produtos", [])
    if not sugs:
        add_rect(sl, MARGIN, Cm(4.0), SW-Cm(1.4), Cm(3.5), C_CARD, C_GRAY, 0.3)
        add_text(sl, "Sem sugestões publicadas para este perfil no momento",
                 SW/2 - Cm(8), Cm(5.2), Cm(16), Cm(1), size=12, color=C_LGRAY, align=PP_ALIGN.CENTER)
        add_text(sl, "O Head de Produtos atualiza as sugestões periodicamente para cada perfil de investidor.",
                 SW/2 - Cm(10), Cm(6.4), Cm(20), Cm(0.7), size=9.5, color=C_GRAY, align=PP_ALIGN.CENTER)
        return

    n  = min(len(sugs), 4)
    cw = (SW - Cm(1.4)) / n - Cm(0.25)
    top_y = Cm(3.2)
    card_h = SH - top_y - Cm(0.75)

    for i, s in enumerate(sugs[:4]):
        p   = s.get("produto", {})
        cx  = MARGIN + i * (cw + Cm(0.25))
        cls = s.get("classe","")
        cor = CLS_COR.get(cls, C_LGRAY)
        add_rect(sl, cx, top_y, cw, card_h, C_CARD, cor, 0.5)
        add_rect(sl, cx, top_y, cw, Cm(0.18), cor)

        add_rect(sl, cx+Cm(0.3), top_y+Cm(0.35), Cm(3.5), Cm(0.55), C_CARD2)
        add_text(sl, s.get("label_classe", CLS_LABEL.get(cls,cls)), cx+Cm(0.4), top_y+Cm(0.38),
                 Cm(3.3), Cm(0.48), size=7.5, bold=True, color=cor)
        gap = s.get("gap",0)
        add_text(sl, f"Gap {gap:+.1f}%", cx+cw-Cm(2.0), top_y+Cm(0.38), Cm(1.8), Cm(0.48),
                 size=8, bold=True, color=C_RED if gap<0 else C_GREEN, align=PP_ALIGN.RIGHT)

        add_text(sl, p.get("nome","—"), cx+Cm(0.3), top_y+Cm(1.05),
                 cw-Cm(0.6), Cm(1.5), size=12, bold=True, color=C_WHITE, wrap=True)
        add_rect(sl, cx+Cm(0.3), top_y+Cm(2.7), cw-Cm(0.6), Cm(0.04), C_GRAY)
        if p.get("taxa"):
            add_text(sl, p["taxa"], cx+Cm(0.3), top_y+Cm(2.85), cw-Cm(0.6), Cm(0.65),
                     size=13, bold=True, color=C_GREEN)
        if p.get("emissor"):
            add_text(sl, p["emissor"], cx+Cm(0.3), top_y+Cm(3.6), cw-Cm(0.6), Cm(0.5), size=9, color=C_LGRAY)
        if p.get("vencimento"):
            add_text(sl, f"Venc: {p['vencimento']}", cx+Cm(0.3), top_y+Cm(4.2), cw-Cm(0.6), Cm(0.5), size=8.5, color=C_GRAY)
        add_rect(sl, cx+Cm(0.3), top_y+Cm(4.8), cw-Cm(0.6), Cm(0.04), C_GRAY)
        if p.get("motivo"):
            add_text(sl, p["motivo"], cx+Cm(0.3), top_y+Cm(4.95), cw-Cm(0.6), Cm(2.8),
                     size=8.5, color=C_LGRAY, wrap=True)
        if p.get("indicado_por"):
            add_text(sl, f"Indicado: {p['indicado_por']}", cx+Cm(0.3), top_y+card_h-Cm(0.85),
                     cw-Cm(0.6), Cm(0.6), size=7.5, color=C_GRAY, italic=True)

# ── SLIDE 12: CROSS SELL ──────────────────────────────────────────────────────
def s_cross_sell(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "CROSS SELL", "Oportunidades de produtos e serviços Braúna")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    cross_ativos = d.get("cross_ativos_nomes", d.get("cross_ativos", []))
    AREAS = [
        ("Aquisição de Bens",              "🏠", "Financiamento imobiliário e consórcio"),
        ("Gestão Discricionária Prunus",   "🌿", "Carteira administrada pela Prunus Asset"),
        ("Planejamento Patrimonial",        "🏛️", "Estruturação patrimonial e sucessória"),
        ("Planejamento Financeiro",         "🎯", "Financial Planning completo"),
        ("Investimentos Internacionais",    "🌎", "Ativos no exterior e dolarização"),
    ]
    col_w = (SW - Cm(1.4)) / len(AREAS) - Cm(0.25)
    top_y = Cm(3.2)
    card_h = SH - top_y - Cm(0.75)

    for i, (nome, icone, desc) in enumerate(AREAS):
        ativo = nome in cross_ativos
        cx = MARGIN + i * (col_w + Cm(0.25))
        cor = C_GREEN if ativo else C_GRAY
        add_rect(sl, cx, top_y, col_w, card_h, C_CARD, cor, 0.5)
        add_rect(sl, cx, top_y, col_w, Cm(0.18), cor)
        add_text(sl, icone, cx + col_w/2 - Cm(1), top_y + Cm(0.5), Cm(2), Cm(1.4),
                 size=28, align=PP_ALIGN.CENTER)
        add_text(sl, nome, cx+Cm(0.3), top_y+Cm(2.1), col_w-Cm(0.6), Cm(1.4),
                 size=10, bold=True, color=C_WHITE, wrap=True, align=PP_ALIGN.CENTER)
        add_text(sl, desc, cx+Cm(0.3), top_y+Cm(3.6), col_w-Cm(0.6), Cm(1.8),
                 size=8.5, color=C_LGRAY, wrap=True, align=PP_ALIGN.CENTER)
        status = "✓  ATIVO" if ativo else "○  Oportunidade"
        add_text(sl, status, cx+Cm(0.3), top_y+card_h-Cm(1.0), col_w-Cm(0.6), Cm(0.65),
                 size=9, bold=ativo, color=cor, align=PP_ALIGN.CENTER)

    # Parágrafo de oportunidade
    cross_n   = sum(1 for nome_a, _, _ in AREAS if nome_a in cross_ativos)
    n_inativos = len(AREAS) - cross_n
    if cross_n >= 4:
        narr_cross = (
            f"Cliente bem engajado nos produtos Braúna ({cross_n}/5 ativos). "
            f"Foco em manutenção, satisfação e aprofundamento dos serviços já contratados."
        )
    else:
        narr_cross = (
            f"{n_inativos} de 5 produtos ainda sem ativação — potencial de aprofundamento do "
            f"relacionamento e geração de receita recorrente. "
            f"Produtos ativos: {cross_n}/5."
        )
    add_caixa_texto(sl, narr_cross, top_y + card_h + Cm(0.3),
                    cor_borda=C_GREEN if cross_n >= 4 else C_AMBER,
                    cor_bg=C_CARD2)

# ── SLIDE 13: RESUMO EXECUTIVO ────────────────────────────────────────────────
def s_resumo(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "RESUMO EXECUTIVO", "Principais indicadores desta reunião")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    comp    = d.get("composicao", {})
    pat     = d.get("patrimonio", 0)
    rent    = d.get("rent", {})
    pr      = rent.get("portfolio", {}) if isinstance(rent, dict) else {}
    cr      = rent.get("cdi", {}) if isinstance(rent, dict) else {}
    score   = d.get("score_servir", 0)
    cross_n = len(d.get("cross_ativos", []))
    desvios = d.get("desvios", [])
    n_fora  = len([x for x in desvios if abs(x.get("desvio_pp",x.get("desvio",0)))>3])
    r12     = pr.get("12m",0)
    c12     = cr.get("12m",0)
    pct_cdi = round(r12/c12*100,0) if c12 else 0

    cards = [
        ("Patrimônio", fmt(pat), "Total sob gestão", C_GOLD),
        ("Rentab. 12M", f"{r12:.2f}%", f"{pct_cdi:.0f}% do CDI", pct_cor(r12)),
        ("Modelo Servir", f"{score}/6", "Pilares concluídos", C_GREEN if score>=5 else (C_AMBER if score>=3 else C_RED)),
        ("Cross Sell", f"{cross_n}/5", "Produtos ativos", C_GREEN if cross_n>=3 else C_AMBER),
        ("Desvios", str(n_fora), "Classes fora do modelo", C_GREEN if n_fora==0 else (C_AMBER if n_fora<=2 else C_RED)),
    ]
    cw = (SW - Cm(1.4)) / len(cards) - Cm(0.25)
    for i, (lbl, val, sub, cor) in enumerate(cards):
        cx = MARGIN + i*(cw+Cm(0.25))
        add_rect(sl, cx, Cm(3.2), cw, Cm(3.2), C_CARD, cor, 0.5)
        add_rect(sl, cx, Cm(3.2), cw, Cm(0.18), cor)
        add_text(sl, lbl, cx+Cm(0.3), Cm(3.5), cw-Cm(0.6), Cm(0.6), size=9, color=C_LGRAY)
        add_text(sl, val, cx+Cm(0.3), Cm(4.1), cw-Cm(0.6), Cm(1.3), size=20, bold=True, color=cor)
        add_text(sl, sub, cx+Cm(0.3), Cm(5.5), cw-Cm(0.6), Cm(0.6), size=8, color=C_LGRAY)

    # Composição resumida visual
    add_text(sl, "COMPOSIÇÃO ATUAL", MARGIN, Cm(7.2), SW, Cm(0.55), size=9, bold=True, color=C_LGRAY)
    cats_v = [(c, comp.get(c,0)) for c in CATS if comp.get(c,0)>0]
    bar_total = sum(v for _,v in cats_v) or 1
    bar_w_total = SW - Cm(1.4)
    bx = MARGIN; by = Cm(7.9)
    for cat, v in cats_v:
        bw_seg = bar_w_total * (v/bar_total)
        add_rect(sl, bx, by, bw_seg - Cm(0.05), Cm(1.0), CLS_COR.get(cat, C_LGRAY))
        bx += bw_seg

    # Legenda
    bx2 = MARGIN; ly = Cm(9.15)
    for cat, v in cats_v:
        if v < 1: continue
        add_rect(sl, bx2, ly, Cm(0.4), Cm(0.4), CLS_COR.get(cat, C_LGRAY))
        lbl_txt = f"{CLS_LABEL.get(cat,cat)} {v:.0f}%"
        add_text(sl, lbl_txt, bx2+Cm(0.55), ly, Cm(4.0), Cm(0.45), size=8, color=C_LGRAY)
        bx2 += Cm(4.3)
        if bx2 > SW - Cm(5): bx2 = MARGIN; ly += Cm(0.6)

    # Narrativa do resumo executivo
    nome_cli = d.get("nome_cliente", "O cliente")
    perfil   = d.get("perfil", "")
    pontos_positivos = []
    pontos_atencao   = []
    if pct_cdi >= 90: pontos_positivos.append(f"rentabilidade saudável ({pct_cdi:.0f}% do CDI em 12M)")
    else:             pontos_atencao.append(f"rentabilidade abaixo do esperado ({pct_cdi:.0f}% do CDI)")
    if score >= 5:    pontos_positivos.append(f"Modelo de Servir bem estruturado ({score}/6 pilares)")
    elif score <= 2:  pontos_atencao.append(f"Modelo de Servir crítico ({score}/6 pilares — risco de ruptura)")
    else:             pontos_atencao.append(f"Modelo de Servir parcial ({score}/6 pilares)")
    if n_fora == 0:   pontos_positivos.append("carteira alinhada ao modelo")
    elif n_fora >= 3: pontos_atencao.append(f"{n_fora} classes fora do modelo — realocação necessária")
    if cross_n >= 3:  pontos_positivos.append(f"cross sell ativo ({cross_n}/5 produtos)")
    else:             pontos_atencao.append(f"oportunidade de cross sell ({cross_n}/5 produtos ativos)")

    partes_resumo = []
    if pontos_positivos: partes_resumo.append("Pontos positivos: " + "; ".join(pontos_positivos))
    if pontos_atencao:   partes_resumo.append("Atenção: " + "; ".join(pontos_atencao))
    narrativa_resumo = f"{nome_cli} ({perfil}): " + ". ".join(partes_resumo) + "." if partes_resumo else ""
    if narrativa_resumo:
        add_caixa_texto(sl, narrativa_resumo, SH - Cm(2.7),
                        cor_borda=C_GREEN if not pontos_atencao else (C_AMBER if len(pontos_atencao)<=1 else C_RED),
                        cor_bg=C_CARD2)

# ── SLIDE 14: PRÓXIMOS PASSOS ─────────────────────────────────────────────────
def s_proximos(prs, d):
    sl = new_slide(prs); bg(sl)
    header(sl, "PRÓXIMOS PASSOS", "Encaminhamentos acordados nesta reunião")
    footer(sl, d.get("nome_cliente",""), d.get("data_ref",""))

    passos_default = [
        ("Assinar a proposta de realocação apresentada hoje",
         "Assessor encaminha modelo por e-mail · Prazo: 5 dias úteis"),
        ("Agendar revisão de carteira em 60 dias",
         "Assessor agenda contato de acompanhamento · Prazo: 60 dias"),
        ("Verificar documentação para Open Investments (OPIN)",
         "Cliente acessa app e autoriza conexão · Prazo: 7 dias"),
        ("Enviar simulação de IR para ativos a serem resgatados",
         "Assessor prepara planilha de ganho de capital · Prazo: 3 dias"),
        ("Confirmar interesse nos produtos de Cross Sell apresentados",
         "Cliente retorna confirmação ao assessor · Prazo: 10 dias"),
    ]
    passos_ia = d.get("ia_proximos_passos","")
    if passos_ia:
        linhas = [l.strip("•- ") for l in passos_ia.split("\n") if l.strip()]
        passos = [(l, "Assessor responsável · Prazo: conforme acordado") for l in linhas]
    else:
        passos = passos_default

    row_h = Cm(2.0)
    for i, (p, sub) in enumerate(passos[:5]):
        ry = Cm(3.1) + i * (row_h + Cm(0.1))
        add_rect(sl, MARGIN, ry, SW-Cm(1.4), row_h, C_CARD, C_CARD2, 0.3)
        add_rect(sl, MARGIN, ry, Cm(1.5), row_h, C_GOLD)
        add_text(sl, f"0{i+1}", MARGIN, ry+Cm(0.5), Cm(1.5), Cm(0.9),
                 size=15, bold=True, color=C_BG, align=PP_ALIGN.CENTER)
        add_text(sl, p, MARGIN+Cm(1.8), ry+Cm(0.28), SW-Cm(3.5), Cm(0.85), size=12, bold=True, color=C_WHITE)
        add_text(sl, sub, MARGIN+Cm(1.8), ry+Cm(1.18), SW-Cm(3.5), Cm(0.6), size=9, color=C_LGRAY, italic=True)

    # Próxima revisão sugerida
    import datetime
    try:
        dr = d.get("data_ref","")
        partes_d = dr.split("/")
        if len(partes_d) == 3:
            base_dt = datetime.date(int(partes_d[2]), int(partes_d[1]), int(partes_d[0]))
        else:
            base_dt = datetime.date.today()
        proxima = base_dt + datetime.timedelta(days=60)
        proxima_str = proxima.strftime("%d/%m/%Y")
    except Exception:
        proxima_str = "em 60 dias"

    add_rect(sl, MARGIN, SH-Cm(1.55), SW-Cm(1.4), Cm(0.04), C_GRAY)
    add_text(sl, f"Próxima revisão sugerida em 60 dias — {proxima_str}",
             MARGIN, SH-Cm(1.45), SW-Cm(1.4), Cm(0.5), size=9, bold=True, color=C_GOLD)
    add_text(sl, d.get("assessor","Assessor Braúna"), MARGIN, SH-Cm(0.95), Cm(9), Cm(0.5), size=9, color=C_LGRAY)
    add_text(sl, "Assessor de Investimentos — Braúna Investimentos", MARGIN, SH-Cm(0.52), Cm(12), Cm(0.42), size=8, color=C_GRAY)

# ── SLIDE 15: ENCERRAMENTO ────────────────────────────────────────────────────
def s_encerramento(prs, d):
    sl = new_slide(prs); bg(sl)
    add_rect(sl, 0, 0, Cm(0.12), SH, C_GOLD)
    add_rect(sl, 0, 0, Cm(1.3), SH, C_CARD)
    add_rect(sl, 0, SH/2 - Cm(0.04), SW, Cm(0.08), C_GOLD)

    add_text(sl, "OBRIGADO", Cm(1.7), SH/2 - Cm(4.5), SW-Cm(2), Cm(3),
             size=44, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)

    # Texto de encerramento
    add_text(sl, "Estamos comprometidos com a realização dos seus objetivos financeiros.",
             Cm(1.7), SH/2 - Cm(1.3), SW-Cm(2), Cm(0.8),
             size=12, color=C_LGRAY, align=PP_ALIGN.CENTER)
    add_text(sl, "Nosso time está à disposição.",
             Cm(1.7), SH/2 - Cm(0.5), SW-Cm(2), Cm(0.65),
             size=11, color=C_LGRAY, align=PP_ALIGN.CENTER)

    # Nome e email do assessor em destaque
    assessor = d.get("assessor","Assessor Braúna")
    email_assessor = d.get("email_assessor", d.get("assessor_email", "contato@braunainvestimentos.com.br"))
    add_text(sl, assessor, Cm(1.7), SH/2 + Cm(0.5), SW-Cm(2), Cm(0.95),
             size=18, bold=True, color=C_GOLD, align=PP_ALIGN.CENTER)
    add_text(sl, email_assessor, Cm(1.7), SH/2 + Cm(1.5), SW-Cm(2), Cm(0.65),
             size=11, color=C_LGRAY, align=PP_ALIGN.CENTER)
    add_text(sl, "Assessor de Investimentos — Braúna Investimentos", Cm(1.7), SH/2 + Cm(2.2),
             SW-Cm(2), Cm(0.6), size=9.5, color=C_GRAY, align=PP_ALIGN.CENTER)

    # 3 cards pequenos no rodapé
    cards_enc = [
        ("Contato direto",             "Fale com seu assessor a qualquer momento"),
        ("Proxima reuniao em 60 dias", "Revisao periodica da carteira agendada"),
        ("Relatorio mensal XPerformance", "Acompanhe sua carteira pelo portal"),
    ]
    cw_enc = (SW - Cm(2.8)) / 3 - Cm(0.2)
    for i, (titulo_enc, desc_enc) in enumerate(cards_enc):
        cx_enc = Cm(1.7) + i * (cw_enc + Cm(0.2))
        add_rect(sl, cx_enc, SH - Cm(3.0), cw_enc, Cm(1.8), C_CARD2, C_GRAY, 0.3)
        add_text(sl, titulo_enc, cx_enc + Cm(0.3), SH - Cm(2.85), cw_enc - Cm(0.6), Cm(0.7),
                 size=9.5, bold=True, color=C_GOLD, wrap=True)
        add_text(sl, desc_enc, cx_enc + Cm(0.3), SH - Cm(2.15), cw_enc - Cm(0.6), Cm(0.75),
                 size=8.5, color=C_LGRAY, wrap=True)

    add_text(sl, "Documento confidencial · Não constitui recomendação formal de investimento",
             Cm(1.7), SH - Cm(0.75), SW-Cm(2), Cm(0.55), size=7.5, color=C_GRAY, align=PP_ALIGN.CENTER)

# ── GERADOR PRINCIPAL ─────────────────────────────────────────────────────────
def gerar_apresentacao_pptx(d: dict) -> bytes:
    """
    Gera PPTX com identidade Braúna.
    Base: 10 slides fixos (1,2,3,4,5,6,7,10,13,14,15)
    Opcionais até 15: 8-desvios, 9-rv, 11-sugestoes, 12-cross, extra-histórico
    """
    prs = Presentation()
    prs.slide_width  = SW
    prs.slide_height = SH

    tem_desvios  = bool(d.get("desvios"))
    tem_rv       = bool(d.get("acoes") or d.get("fiis"))
    tem_sugs     = bool(d.get("sugestoes_produtos"))
    tem_cross    = bool(d.get("cross_ativos") or d.get("cross_ativos_nomes"))

    # Monta agenda dinamicamente
    agenda_items = [
        (1, "Cenário Global",       "Panorama macroeconômico internacional"),
        (2, "Brasil & HP",          "Visão Head de Produtos — Levante Asset"),
        (3, "Patrimônio",           "Evolução e rentabilidade da carteira"),
        (4, "Composição",           "Alocação por classe de ativo"),
        (5, "Carteira vs. Modelo",  "Comparativo e desvios do perfil"),
    ]
    n = 6
    if tem_desvios:   agenda_items.append((n, "Desvios",          "O que ajustar para atingir o modelo")); n+=1
    if tem_rv:        agenda_items.append((n, "Renda Variável",   "Ações e FIIs na carteira")); n+=1
    agenda_items.append((n, "Modelo de Servir", "Trilha de relacionamento")); n+=1
    if tem_sugs:      agenda_items.append((n, "Sugestões",        "Produtos recomendados pelo Head de Produtos")); n+=1
    if tem_cross:     agenda_items.append((n, "Cross Sell",       "Oportunidades de produtos e serviços")); n+=1
    agenda_items.append((n, "Resumo Executivo", "Principais indicadores da reunião")); n+=1
    agenda_items.append((n, "Próximos Passos",  "Encaminhamentos acordados")); n+=1

    # Slides fixos base
    s_capa(prs, d)                      # 1
    s_agenda(prs, d, agenda_items)      # 2
    s_cenario_global(prs, d)            # 3
    s_cenario_brasil(prs, d)            # 4
    s_patrimonio(prs, d)                # 5
    s_composicao(prs, d)                # 6
    s_vs_modelo(prs, d)                 # 7

    # Slides opcionais
    if tem_desvios:   s_desvios(prs, d)    # 8
    if tem_rv:        s_rv(prs, d)         # 9

    s_modelo_servir(prs, d)             # 10

    if tem_sugs:      s_sugestoes(prs, d)  # 11
    if tem_cross:     s_cross_sell(prs, d) # 12

    s_resumo(prs, d)                    # 13
    s_proximos(prs, d)                  # 14
    s_encerramento(prs, d)              # 15

    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()
