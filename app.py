import streamlit as st
import json
import re
import io
import tempfile
from pathlib import Path
from datetime import date

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Análise de Carteiras — Braúna",
    page_icon="📊",
    layout="wide",
)

# ── CSS Braúna ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0D0D0D; color: #F0F0F0; }
    section[data-testid="stSidebar"] { background-color: #1A1A1A; }
    h1, h2, h3 { color: #D6B27A !important; }
    .metric-card {
        background: #1A1A1A;
        border: 1px solid #2C2C2C;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-label { font-size: 12px; color: #888; margin-bottom: 4px; }
    .metric-value { font-size: 22px; font-weight: 600; color: #D6B27A; }
    .metric-value.danger { color: #FF6B6B; }
    .metric-value.ok { color: #5DCAA5; }
    .frag-box {
        background: #2A1010;
        border-left: 3px solid #FF6B6B;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #FFB3B3;
        font-size: 14px;
    }
    .opor-box {
        background: #0F2A1F;
        border-left: 3px solid #5DCAA5;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #9FE1CB;
        font-size: 14px;
    }
    .sug-box {
        background: #1A160A;
        border-left: 3px solid #D6B27A;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0;
        color: #D6B27A;
        font-size: 14px;
    }
    div[data-testid="stFileUploader"] {
        background: #1A1A1A;
        border: 1px dashed #D6B27A;
        border-radius: 10px;
    }
    .stSelectbox label, .stTextInput label { color: #D6B27A !important; }
    .rodape {
        color: #555;
        font-size: 11px;
        text-align: center;
        margin-top: 40px;
        border-top: 1px solid #2C2C2C;
        padding-top: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ── Modelos de alocação ───────────────────────────────────────────────────────
MODELOS = {
    "conservadora": {
        "pos_fixado": 70.00, "inflacao": 16.00, "pre_fixado": 7.00,
        "acoes": 0.00, "fiis": 0.00, "multimercado": 3.00,
        "internacional": 4.00, "alternativos": 0.00, "criptomoedas": 0.00,
    },
    "moderada": {
        "pos_fixado": 44.00, "inflacao": 23.00, "pre_fixado": 10.00,
        "acoes": 5.00, "fiis": 1.50, "multimercado": 6.00,
        "internacional": 9.00, "alternativos": 1.00, "criptomoedas": 0.50,
    },
    "arrojada": {
        "pos_fixado": 28.00, "inflacao": 28.00, "pre_fixado": 12.00,
        "acoes": 8.00, "fiis": 2.50, "multimercado": 9.50,
        "internacional": 10.25, "alternativos": 1.00, "criptomoedas": 0.75,
    },
    "agressiva": {
        "pos_fixado": 13.00, "inflacao": 31.00, "pre_fixado": 13.00,
        "acoes": 14.00, "fiis": 3.50, "multimercado": 10.50,
        "internacional": 13.00, "alternativos": 1.00, "criptomoedas": 1.00,
    },
}

LABELS = {
    "pos_fixado": "Pós Fixado", "inflacao": "Inflação", "pre_fixado": "Pré Fixado",
    "acoes": "Ações", "fiis": "FIIs", "multimercado": "Multimercado",
    "internacional": "Internacional", "alternativos": "Alternativos", "criptomoedas": "Criptomoedas",
}

MAPEAMENTO = {
    "pós fixado": "pos_fixado", "pos fixado": "pos_fixado", "pós-fixado": "pos_fixado",
    "inflação": "inflacao", "inflacao": "inflacao", "ipca": "inflacao",
    "pré fixado": "pre_fixado", "pre fixado": "pre_fixado", "pré-fixado": "pre_fixado",
    "ações": "acoes", "acoes": "acoes", "renda variável": "acoes", "rv brasil": "acoes",
    "renda variável brasil": "acoes",
    "fiis": "fiis", "fii": "fiis", "fundos imobiliários": "fiis",
    "multimercado": "multimercado", "multi mercado": "multimercado",
    "internacional": "internacional", "dólar": "internacional", "exterior": "internacional",
    "renda fixa global": "internacional", "rv exterior": "internacional",
    "criptomoedas": "criptomoedas", "cripto": "criptomoedas",
    "alternativo": "alternativos", "alternativos": "alternativos", "outros": "alternativos",
    "caixa": "caixa", "conta corrente": "caixa",
}

CATS = list(LABELS.keys())


def mapear_categoria(texto):
    t = texto.lower().strip()
    for chave, valor in MAPEAMENTO.items():
        if chave in t:
            return valor
    return None


def extrair_composicao_pdf(arquivo_bytes):
    try:
        import pdfplumber
    except ImportError:
        st.error("pdfplumber não instalado. Rode: pip install pdfplumber")
        return None, 0.0, {}

    texto = ""
    with pdfplumber.open(io.BytesIO(arquivo_bytes)) as pdf:
        for pagina in pdf.pages:
            texto += (pagina.extract_text() or "") + "\n"

    composicao = {cat: 0.0 for cat in CATS}
    composicao["caixa"] = 0.0

    padrao = re.compile(
        r"([A-Za-zÀ-ÿ\s\-\/]+?)\s+"
        r"(?:R\$[\s\d\.,]+\s+)?"
        r"(\d{1,3}(?:[.,]\d{1,3})*(?:[.,]\d{1,2})?)\s*%",
        re.IGNORECASE,
    )
    for linha in texto.splitlines():
        m = padrao.search(linha.strip())
        if m:
            nome = m.group(1).strip()
            try:
                perc = float(m.group(2).replace(".", "").replace(",", "."))
            except ValueError:
                continue
            cat = mapear_categoria(nome)
            if cat and perc > 0:
                composicao[cat] = composicao.get(cat, 0.0) + perc

    # Extrai rentabilidade se disponível
    rent = {}
    m_port = re.search(r"Portf.lio\s+([\d,]+)%\s+([\d,]+)%\s+([\d,]+)%\s+([\d,]+)%", texto)
    m_cdi  = re.search(r"CDI\s+([\d,]+)%\s+([\d,]+)%\s+([\d,]+)%\s+([\d,]+)%", texto)
    if m_port:
        rent["portfolio"] = {
            "mes": float(m_port.group(1).replace(",", ".")),
            "ano": float(m_port.group(2).replace(",", ".")),
            "12m": float(m_port.group(3).replace(",", ".")),
            "24m": float(m_port.group(4).replace(",", ".")),
        }
    if m_cdi:
        rent["cdi"] = {
            "mes": float(m_cdi.group(1).replace(",", ".")),
            "ano": float(m_cdi.group(2).replace(",", ".")),
            "12m": float(m_cdi.group(3).replace(",", ".")),
            "24m": float(m_cdi.group(4).replace(",", ".")),
        }

    # Extrai patrimônio
    patrimonio = 0.0
    m_pat = re.search(r"R\$\s*([\d\.,]+)", texto)
    if m_pat:
        try:
            patrimonio = float(m_pat.group(1).replace(".", "").replace(",", "."))
        except Exception:
            pass

    caixa = composicao.pop("caixa", 0.0)
    total = sum(composicao.values())
    if total > 1:
        fator = 100.0 / total
        composicao = {k: round(v * fator, 2) for k, v in composicao.items()}

    return composicao, caixa, rent, patrimonio


def calcular_desvios(composicao, modelo):
    resultado = []
    for cat in CATS:
        real = composicao.get(cat, 0.0)
        alvo = modelo.get(cat, 0.0)
        resultado.append({
            "cat": cat,
            "label": LABELS[cat],
            "real": round(real, 2),
            "alvo": round(alvo, 2),
            "desvio": round(real - alvo, 2),
        })
    return sorted(resultado, key=lambda x: abs(x["desvio"]), reverse=True)


def gerar_grafico(desvios, nome_cliente):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    labels = [d["label"] for d in desvios]
    reais  = [d["real"]  for d in desvios]
    alvos  = [d["alvo"]  for d in desvios]
    x = np.arange(len(labels))
    w = 0.36

    fig, ax = plt.subplots(figsize=(11, 4.5))
    fig.patch.set_facecolor("#0D0D0D")
    ax.set_facecolor("#1A1A1A")

    b1 = ax.bar(x - w/2, reais, w, color="#D6B27A", label="Atual", zorder=3, linewidth=0)
    b2 = ax.bar(x + w/2, alvos, w, color="#444444", label="Modelo Levante", zorder=3, linewidth=0)

    for b in b1:
        h = b.get_height()
        if h > 0:
            ax.text(b.get_x() + b.get_width()/2, h + 0.4, f"{h:.1f}%",
                    ha="center", va="bottom", color="#D6B27A", fontsize=7.5)
    for b in b2:
        h = b.get_height()
        if h > 0:
            ax.text(b.get_x() + b.get_width()/2, h + 0.4, f"{h:.1f}%",
                    ha="center", va="bottom", color="#888888", fontsize=7.5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=28, ha="right", color="white", fontsize=9)
    ax.set_ylabel("%", color="white", fontsize=9)
    ax.tick_params(colors="white", labelsize=8)
    ax.spines[:].set_color("#2C2C2C")
    ax.yaxis.grid(True, color="#2A2A2A", zorder=0, linewidth=0.5)
    ax.set_axisbelow(True)
    legend = ax.legend(facecolor="#1A1A1A", edgecolor="#D6B27A", labelcolor="white", fontsize=9)
    fig.tight_layout(pad=1.5)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return buf


def gerar_pdf_relatorio(nome, perfil, desvios, rent, patrimonio, caixa, data_ref):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        return None

    PRETO       = colors.HexColor("#0D0D0D")
    DOURADO     = colors.HexColor("#D6B27A")
    DOURADO_ESC = colors.HexColor("#A07840")
    CINZA_ESC   = colors.HexColor("#1A1A1A")
    CINZA_MED   = colors.HexColor("#2C2C2C")
    BRANCO      = colors.white
    VERMELHO    = colors.HexColor("#FF6B6B")
    VERDE       = colors.HexColor("#5DCAA5")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    def S(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=styles[parent],
                              textColor=kw.pop("textColor", BRANCO),
                              **kw)

    s_title  = S("T",  fontSize=18, leading=22, textColor=DOURADO, alignment=TA_CENTER, spaceAfter=4)
    s_sub    = S("S",  fontSize=10, textColor=DOURADO_ESC, alignment=TA_CENTER, spaceAfter=2)
    s_sec    = S("Se", fontSize=11, textColor=DOURADO, spaceBefore=10, spaceAfter=4)
    s_body   = S("B",  fontSize=9,  leading=13)
    s_rod    = S("R",  fontSize=7,  textColor=colors.HexColor("#666666"), alignment=TA_CENTER)
    s_frag   = S("F",  fontSize=9,  leading=13, textColor=VERMELHO)
    s_opor   = S("O",  fontSize=9,  leading=13, textColor=VERDE)
    s_sug    = S("Su", fontSize=9,  leading=13, textColor=DOURADO)

    elems = []

    elems.append(Paragraph("BRAÚNA INVESTIMENTOS", s_title))
    elems.append(Paragraph("Análise de Alocação por Indexador — Modelo Levante Asset", s_sub))
    elems.append(HRFlowable(width="100%", thickness=1, color=DOURADO, spaceAfter=8))

    perfil_pt = {"conservadora":"Conservadora","moderada":"Moderada",
                 "arrojada":"Arrojada","agressiva":"Agressiva"}
    meta = [
        ["Cliente:", nome,              "Assessor:", "Denis Kinoshita"],
        ["Perfil:",  perfil_pt.get(perfil, perfil), "Data ref.:", data_ref],
        ["Patrimônio:", f"R$ {patrimonio:,.2f}".replace(",","X").replace(".",",").replace("X","."),
         "Caixa:", f"{caixa:.1f}% (excluído do modelo)"],
    ]
    tm = Table(meta, colWidths=[2.6*cm, 7*cm, 2.6*cm, 5*cm])
    tm.setStyle(TableStyle([
        ("FONTSIZE", (0,0),(-1,-1), 8),
        ("TEXTCOLOR",(0,0),(-1,-1), BRANCO),
        ("TEXTCOLOR",(0,0),(0,-1), DOURADO),
        ("TEXTCOLOR",(2,0),(2,-1), DOURADO),
        ("ROWBACKGROUNDS",(0,0),(-1,-1),[CINZA_ESC, CINZA_MED]),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#3A3A3A")),
        ("PADDING",(0,0),(-1,-1),4),
    ]))
    elems.append(tm)
    elems.append(Spacer(1, 0.3*cm))

    if rent.get("portfolio") and rent.get("cdi"):
        p = rent["portfolio"]
        c = rent["cdi"]
        pct_cdi_12m = round(p["12m"] / c["12m"] * 100, 1) if c.get("12m") else 0
        rent_data = [
            ["Período", "Portfólio", "CDI", "% do CDI"],
            ["Mês",  f'{p["mes"]:.2f}%', f'{c["mes"]:.2f}%', f'{round(p["mes"]/c["mes"]*100,1)}%'],
            ["Ano",  f'{p["ano"]:.2f}%', f'{c["ano"]:.2f}%', f'{round(p["ano"]/c["ano"]*100,1)}%'],
            ["12M",  f'{p["12m"]:.2f}%', f'{c["12m"]:.2f}%', f'{pct_cdi_12m}%'],
            ["24M",  f'{p["24m"]:.2f}%', f'{c["24m"]:.2f}%', f'{round(p["24m"]/c["24m"]*100,1)}%'],
        ]
        elems.append(Paragraph("Rentabilidade vs. CDI", s_sec))
        tr = Table(rent_data, colWidths=[3*cm,4*cm,4*cm,4*cm])
        tr.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),DOURADO_ESC),
            ("TEXTCOLOR",(0,0),(-1,0),PRETO),
            ("TEXTCOLOR",(0,1),(-1,-1),BRANCO),
            ("FONTSIZE",(0,0),(-1,-1),8),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[CINZA_ESC,CINZA_MED]),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#3A3A3A")),
            ("ALIGN",(1,0),(-1,-1),"CENTER"),
            ("PADDING",(0,0),(-1,-1),4),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ]))
        elems.append(tr)
        elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Composição Atual vs. Modelo", s_sec))

    # Gráfico
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    labels_g = [d["label"] for d in desvios]
    reais_g  = [d["real"]  for d in desvios]
    alvos_g  = [d["alvo"]  for d in desvios]
    x = np.arange(len(labels_g))
    w = 0.35
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#0D0D0D")
    ax.set_facecolor("#1A1A1A")
    ax.bar(x - w/2, reais_g, w, color="#D6B27A", zorder=3, linewidth=0)
    ax.bar(x + w/2, alvos_g, w, color="#444444", zorder=3, linewidth=0)
    ax.set_xticks(x)
    ax.set_xticklabels(labels_g, rotation=28, ha="right", color="white", fontsize=8)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#2C2C2C")
    ax.yaxis.grid(True, color="#2A2A2A", zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylabel("%", color="white")
    fig.tight_layout(pad=1)
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format="png", dpi=150, facecolor="#0D0D0D")
    plt.close(fig)
    img_buf.seek(0)
    elems.append(Image(img_buf, width=15*cm, height=6*cm))
    elems.append(Spacer(1, 0.3*cm))

    elems.append(Paragraph("Desvios por Indexador", s_sec))
    dev_data = [["Indexador","Atual (%)","Modelo (%)","Desvio (pp)"]]
    for d in desvios:
        dev_data.append([d["label"], f'{d["real"]:.2f}', f'{d["alvo"]:.2f}', f'{d["desvio"]:+.2f}'])
    td = Table(dev_data, colWidths=[5*cm,3.5*cm,3.5*cm,3.5*cm])
    estilos_dev = [
        ("BACKGROUND",(0,0),(-1,0),DOURADO_ESC),
        ("TEXTCOLOR",(0,0),(-1,0),PRETO),
        ("TEXTCOLOR",(0,1),(-1,-1),BRANCO),
        ("FONTSIZE",(0,0),(-1,-1),8),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[CINZA_ESC,CINZA_MED]),
        ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#3A3A3A")),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),
        ("PADDING",(0,0),(-1,-1),4),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ]
    for i, d in enumerate(desvios, 1):
        if d["desvio"] < -1.5:
            estilos_dev.append(("TEXTCOLOR",(3,i),(3,i),VERMELHO))
        elif d["desvio"] > 1.5:
            estilos_dev.append(("TEXTCOLOR",(3,i),(3,i),VERDE))
    td.setStyle(TableStyle(estilos_dev))
    elems.append(td)
    elems.append(Spacer(1,0.3*cm))

    fragilidades = [d for d in desvios if d["desvio"] < -1.5]
    oportunidades = [d for d in desvios if d["desvio"] > 1.5]

    elems.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
    elems.append(Paragraph("Fragilidades Identificadas", s_sec))
    if fragilidades:
        for f in fragilidades:
            elems.append(Paragraph(
                f'▸ {f["label"]}: {f["real"]:.1f}% atual vs. alvo {f["alvo"]:.1f}% — falta {abs(f["desvio"]):.1f} pp', s_frag))
    else:
        elems.append(Paragraph("Nenhuma fragilidade relevante (desvio < 1,5 pp).", s_body))

    elems.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
    elems.append(Paragraph("Oportunidades de Realocação", s_sec))
    if oportunidades:
        for o in oportunidades:
            elems.append(Paragraph(
                f'▸ {o["label"]}: {o["real"]:.1f}% atual vs. alvo {o["alvo"]:.1f}% — excesso de {o["desvio"]:.1f} pp', s_opor))
    else:
        elems.append(Paragraph("Sem sobrealocações relevantes.", s_body))

    if fragilidades and oportunidades:
        elems.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
        elems.append(Paragraph("Sugestões de Movimentação", s_sec))
        origens = ", ".join([o["label"] for o in oportunidades])
        for f in fragilidades:
            elems.append(Paragraph(
                f'→ Realocar ~{abs(f["desvio"]):.1f} pp de {origens} para {f["label"]}.', s_sug))

    elems.append(Spacer(1,0.5*cm))
    elems.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
    elems.append(Paragraph(
        "Este relatório é um instrumento de apoio à decisão do assessor e não constitui recomendação formal "
        "de investimento. Rentabilidades passadas não garantem resultados futuros. "
        "Braúna Investimentos — assessoria vinculada à XP Investimentos.", s_rod))

    def fundo(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PRETO)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(elems, onFirstPage=fundo, onLaterPages=fundo)
    buf.seek(0)
    return buf


# ── Interface ─────────────────────────────────────────────────────────────────
st.markdown("## 📊 Análise de Carteiras")
st.markdown("**Braúna Investimentos · Denis Kinoshita**")
st.divider()


# —— Instruções de uso
st.markdown("""
<div style="background:#1A1A1A; border:1px solid #D6B27A44; border-radius:12px; padding:20px; margin:12px 0 20px 0;">
<p style="color:#D6B27A; font-weight:600; margin:0 0 14px 0; font-size:15px;">📋 Como usar esta ferramenta</p>
<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:14px;">
<div style="background:#111; border-radius:8px; padding:14px;">
<p style="color:#D6B27A; margin:0 0 6px 0; font-weight:600;">① XPerformance</p>
<p style="color:#888; margin:0; font-size:13px;">Baixe o PDF de carteira do cliente na plataforma XP</p>
</div>
<div style="background:#111; border-radius:8px; padding:14px;">
<p style="color:#D6B27A; margin:0 0 6px 0; font-weight:600;">② Dados do cliente</p>
<p style="color:#888; margin:0; font-size:13px;">Preencha nome, perfil e data na barra lateral</p>
</div>
<div style="background:#111; border-radius:8px; padding:14px;">
<p style="color:#D6B27A; margin:0 0 6px 0; font-weight:600;">③ Upload do PDF</p>
<p style="color:#888; margin:0; font-size:13px;">Arraste ou selecione o PDF do XPerformance abaixo</p>
</div>
<div style="background:#111; border-radius:8px; padding:14px;">
<p style="color:#D6B27A; margin:0 0 6px 0; font-weight:600;">④ Análise e relatório</p>
<p style="color:#888; margin:0; font-size:13px;">Veja os desvios e exporte o relatório em PDF</p>
</div>
</div>
</div>
""", unsafe_allow_html=True)


# Sidebar — cadastro do cliente
with st.sidebar:
    st.markdown("### Cliente")
    nome_cliente = st.text_input("Nome do cliente", placeholder="Ex: Maria Silva")
    perfil = st.selectbox(
        "Perfil de investidor",
        ["conservadora", "moderada", "arrojada", "agressiva"],
        format_func=lambda x: x.capitalize(),
    )
    data_ref = st.date_input("Data de referência", value=date.today())
    st.divider()
    st.markdown("**Modelo Levante Asset**")
    modelo_sel = MODELOS[perfil]
    for cat, pct in modelo_sel.items():
        if pct > 0:
            st.markdown(f"<span style='color:#888;font-size:12px;'>{LABELS[cat]}</span> "
                        f"<span style='color:#D6B27A;font-size:12px;font-weight:600;'>{pct:.1f}%</span>",
                        unsafe_allow_html=True)

# Upload do PDF
st.markdown("### Relatório XP (PDF)")
pdf_file = st.file_uploader(
    "Arraste o PDF do XPerformance aqui",
    type=["pdf"],
    label_visibility="collapsed",
)

if pdf_file and nome_cliente:
    with st.spinner("Extraindo composição do PDF..."):
        composicao, caixa, rent, patrimonio = extrair_composicao_pdf(pdf_file.read())

    if composicao is None:
        st.error("Não foi possível extrair a composição. Verifique se o PDF é o relatório XPerformance.")
        st.stop()

    desvios = calcular_desvios(composicao, modelo_sel)

    # ── Métricas de rentabilidade ─────────────────────────────────────────────
    if rent.get("portfolio") and rent.get("cdi"):
        p = rent["portfolio"]
        c = rent["cdi"]
        pct_cdi_12m = round(p["12m"] / c["12m"] * 100, 1) if c.get("12m") else 0
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Rentab. mês", f'{p["mes"]:.2f}%', f'{p["mes"]-c["mes"]:+.2f}% vs CDI')
        with col2:
            st.metric("Rentab. 12M", f'{p["12m"]:.2f}%', f'CDI: {c["12m"]:.2f}%')
        with col3:
            st.metric("% do CDI (12M)", f'{pct_cdi_12m:.1f}%',
                      delta="⚠️ Baixo" if pct_cdi_12m < 70 else "OK",
                      delta_color="inverse" if pct_cdi_12m < 70 else "normal")
        with col4:
            pat_fmt = f"R$ {patrimonio:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")
            st.metric("Patrimônio", pat_fmt)
        st.divider()

    # ── Gráfico ───────────────────────────────────────────────────────────────
    st.markdown("### Composição atual vs. Modelo")
    graf_buf = gerar_grafico(desvios, nome_cliente)
    st.image(graf_buf, use_container_width=True)

    # ── Tabela de desvios ─────────────────────────────────────────────────────
    st.markdown("### Desvios por indexador")
    col_tab, col_diag = st.columns([1.1, 1])

    with col_tab:
        for d in desvios:
            cor = "🔴" if d["desvio"] < -1.5 else "🟢" if d["desvio"] > 1.5 else "⚪"
            sinal = "+" if d["desvio"] >= 0 else ""
            st.markdown(
                f"{cor} **{d['label']}** — atual `{d['real']:.2f}%` · alvo `{d['alvo']:.2f}%` · "
                f"desvio **{sinal}{d['desvio']:.2f} pp**"
            )

    with col_diag:
        fragilidades = [d for d in desvios if d["desvio"] < -1.5]
        oportunidades = [d for d in desvios if d["desvio"] > 1.5]

        if fragilidades:
            st.markdown("**Fragilidades**")
            for f in fragilidades:
                st.markdown(
                    f'<div class="frag-box">▸ <b>{f["label"]}</b>: falta {abs(f["desvio"]):.1f} pp '
                    f'({f["real"]:.1f}% atual vs. {f["alvo"]:.1f}% alvo)</div>',
                    unsafe_allow_html=True,
                )

        if oportunidades:
            st.markdown("**Para realocar**")
            for o in oportunidades:
                st.markdown(
                    f'<div class="opor-box">▸ <b>{o["label"]}</b>: excesso de {o["desvio"]:.1f} pp '
                    f'({o["real"]:.1f}% atual vs. {o["alvo"]:.1f}% alvo)</div>',
                    unsafe_allow_html=True,
                )

        if fragilidades and oportunidades:
            st.markdown("**Sugestões**")
            origens = ", ".join([o["label"] for o in oportunidades])
            for f in fragilidades:
                st.markdown(
                    f'<div class="sug-box">→ Realocar ~{abs(f["desvio"]):.1f} pp de {origens} '
                    f'para <b>{f["label"]}</b></div>',
                    unsafe_allow_html=True,
                )

    st.divider()

    # ── Download PDF ──────────────────────────────────────────────────────────
    st.markdown("### Relatório PDF")
    with st.spinner("Gerando PDF..."):
        pdf_buf = gerar_pdf_relatorio(
            nome=nome_cliente,
            perfil=perfil,
            desvios=desvios,
            rent=rent,
            patrimonio=patrimonio,
            caixa=caixa,
            data_ref=str(data_ref),
        )

    if pdf_buf:
        nome_arq = f"{nome_cliente.lower().replace(' ','-')}_{data_ref}_analise.pdf"
        st.download_button(
            label="⬇️ Baixar relatório PDF",
            data=pdf_buf,
            file_name=nome_arq,
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.warning("PDF não gerado. Verifique se reportlab está instalado.")

    st.markdown('<div class="rodape">Braúna Investimentos · Relatório de apoio à decisão · '
                'Não constitui recomendação formal de investimento</div>', unsafe_allow_html=True)

elif not nome_cliente:
    st.info("👈 Preencha o nome do cliente e o perfil na barra lateral para começar.")
elif not pdf_file:
    st.info("📄 Faça o upload do PDF do XPerformance acima.")
