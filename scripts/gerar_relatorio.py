"""
gerar_relatorio.py
Gera PDF individual de análise de carteira no estilo visual Braúna Investimentos
(fundo escuro, dourado #D6B27A).

Uso:
    python gerar_relatorio.py <composicao.json> <analise.json> <nome_cliente> <perfil> [--output <relatorio.pdf>]
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import date

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    print("Instale dependências: pip install matplotlib reportlab")
    sys.exit(1)

# ── Cores Braúna ──────────────────────────────────────────────────────────────
PRETO       = colors.HexColor("#0D0D0D")
DOURADO     = colors.HexColor("#D6B27A")
DOURADO_ESC = colors.HexColor("#A07840")
CINZA_ESC   = colors.HexColor("#1A1A1A")
CINZA_MED   = colors.HexColor("#2C2C2C")
BRANCO      = colors.white

LABELS_PT = {
    "pos_fixado":   "Pós Fixado",
    "inflacao":     "Inflação",
    "pre_fixado":   "Pré Fixado",
    "acoes":        "Ações",
    "fiis":         "FIIs",
    "multimercado": "Multimercado",
    "internacional":"Internacional",
    "alternativos": "Alternativos",
    "criptomoedas": "Criptomoedas",
}

PERFIL_PT = {
    "conservadora": "Conservadora",
    "moderada":     "Moderada",
    "arrojada":     "Arrojada",
    "agressiva":    "Agressiva",
}


def gerar_grafico_barras(desvios: list[dict], caminho_img: Path):
    categorias  = [d["label"] for d in desvios]
    reais        = [d["real_pct"] for d in desvios]
    alvos        = [d["alvo_pct"] for d in desvios]

    x = np.arange(len(categorias))
    largura = 0.35

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor("#0D0D0D")
    ax.set_facecolor("#1A1A1A")

    barras_real  = ax.bar(x - largura/2, reais,  largura, label="Carteira Atual", color="#D6B27A", zorder=3)
    barras_alvo  = ax.bar(x + largura/2, alvos,  largura, label="Modelo Levante", color="#4A4A4A", zorder=3)

    ax.set_xticks(x)
    ax.set_xticklabels(categorias, rotation=30, ha="right", color="white", fontsize=8)
    ax.set_ylabel("%", color="white", fontsize=9)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("#3A3A3A")
    ax.yaxis.grid(True, color="#2A2A2A", zorder=0)
    ax.set_axisbelow(True)

    for barra in barras_real:
        h = barra.get_height()
        if h > 0:
            ax.text(barra.get_x() + barra.get_width()/2, h + 0.3, f"{h:.1f}%",
                    ha="center", va="bottom", color="#D6B27A", fontsize=7)
    for barra in barras_alvo:
        h = barra.get_height()
        if h > 0:
            ax.text(barra.get_x() + barra.get_width()/2, h + 0.3, f"{h:.1f}%",
                    ha="center", va="bottom", color="#888888", fontsize=7)

    legend = ax.legend(facecolor="#1A1A1A", edgecolor="#D6B27A", labelcolor="white", fontsize=8)
    fig.tight_layout(pad=1.2)
    fig.savefig(str(caminho_img), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def gerar_pdf(
    nome_cliente: str,
    perfil: str,
    desvios: list[dict],
    diagnostico: dict,
    sugestoes: list[str],
    caixa_pct: float,
    caminho_saida: Path,
    data_ref: str,
):
    doc = SimpleDocTemplate(
        str(caminho_saida),
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    def estilo(name, parent="Normal", **kw):
        return ParagraphStyle(name, parent=styles[parent],
                              textColor=kw.pop("textColor", BRANCO),
                              backColor=kw.pop("backColor", None),
                              **kw)

    s_titulo    = estilo("Titulo",    fontSize=18, leading=22, textColor=DOURADO, alignment=TA_CENTER, spaceAfter=4)
    s_subtitulo = estilo("SubTit",    fontSize=10, leading=14, textColor=DOURADO_ESC, alignment=TA_CENTER, spaceAfter=2)
    s_secao     = estilo("Secao",     fontSize=11, leading=14, textColor=DOURADO, spaceBefore=12, spaceAfter=4)
    s_body      = estilo("Body",      fontSize=9,  leading=13, textColor=BRANCO)
    s_rodape    = estilo("Rodape",    fontSize=7,  leading=10, textColor=colors.HexColor("#888888"), alignment=TA_CENTER)
    s_item_frag = estilo("ItemFrag",  fontSize=9,  leading=13, textColor=colors.HexColor("#FF8080"))
    s_item_opor = estilo("ItemOpor",  fontSize=9,  leading=13, textColor=colors.HexColor("#80D6B2"))
    s_item_sug  = estilo("ItemSug",   fontSize=9,  leading=13, textColor=DOURADO)

    elementos = []

    # ── Cabeçalho ──────────────────────────────────────────────────────────────
    elementos.append(Paragraph("BRAÚNA INVESTIMENTOS", s_titulo))
    elementos.append(Paragraph("Análise de Alocação por Indexador", s_subtitulo))
    elementos.append(HRFlowable(width="100%", thickness=1, color=DOURADO, spaceAfter=8))

    # Tabela de metadados
    meta = [
        ["Cliente:", nome_cliente,         "Assessor:", "Denis Kinoshita"],
        ["Perfil:",  PERFIL_PT.get(perfil, perfil), "Data ref.:", data_ref],
        ["Modelo:",  "Levante Asset",       "Caixa:",    f"{caixa_pct:.1f}% (excluído do modelo)"],
    ]
    t_meta = Table(meta, colWidths=[2.5*cm, 7*cm, 2.5*cm, 5*cm])
    t_meta.setStyle(TableStyle([
        ("FONTSIZE",    (0,0), (-1,-1), 8),
        ("TEXTCOLOR",   (0,0), (-1,-1), BRANCO),
        ("TEXTCOLOR",   (0,0), (0,-1), DOURADO),
        ("TEXTCOLOR",   (2,0), (2,-1), DOURADO),
        ("BACKGROUND",  (0,0), (-1,-1), CINZA_MED),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [CINZA_ESC, CINZA_MED]),
        ("GRID",        (0,0), (-1,-1), 0.3, colors.HexColor("#3A3A3A")),
        ("PADDING",     (0,0), (-1,-1), 4),
    ]))
    elementos.append(t_meta)
    elementos.append(Spacer(1, 0.5*cm))

    # ── Gráfico ────────────────────────────────────────────────────────────────
    elementos.append(Paragraph("Composição Atual vs. Modelo", s_secao))
    img_path = caminho_saida.parent / "_chart_tmp.png"
    gerar_grafico_barras(desvios, img_path)
    elementos.append(Image(str(img_path), width=16*cm, height=7*cm))
    elementos.append(Spacer(1, 0.3*cm))

    # ── Tabela de desvios ──────────────────────────────────────────────────────
    elementos.append(Paragraph("Desvios por Indexador (ordenados por relevância)", s_secao))
    cabecalho = [["Indexador", "Carteira Atual (%)", "Modelo (%)", "Desvio (pp)"]]
    linhas = []
    for d in desvios:
        desvio_str = f"{d['desvio_pp']:+.2f}"
        linhas.append([d["label"], f"{d['real_pct']:.2f}", f"{d['alvo_pct']:.2f}", desvio_str])

    t_desvios = Table(cabecalho + linhas, colWidths=[5*cm, 4*cm, 4*cm, 4*cm])
    estilos_td = [
        ("BACKGROUND",   (0,0), (-1,0), DOURADO_ESC),
        ("TEXTCOLOR",    (0,0), (-1,0), PRETO),
        ("FONTSIZE",     (0,0), (-1,-1), 8),
        ("TEXTCOLOR",    (0,1), (-1,-1), BRANCO),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [CINZA_ESC, CINZA_MED]),
        ("GRID",         (0,0), (-1,-1), 0.3, colors.HexColor("#3A3A3A")),
        ("ALIGN",        (1,0), (-1,-1), "CENTER"),
        ("PADDING",      (0,0), (-1,-1), 4),
        ("FONTNAME",     (0,0), (-1,0), "Helvetica-Bold"),
    ]
    # Colorir desvios negativos em vermelho e positivos em verde
    for i, d in enumerate(desvios, start=1):
        if d["desvio_pp"] < -1.5:
            estilos_td.append(("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#FF8080")))
        elif d["desvio_pp"] > 1.5:
            estilos_td.append(("TEXTCOLOR", (3, i), (3, i), colors.HexColor("#80D6B2")))
    t_desvios.setStyle(TableStyle(estilos_td))
    elementos.append(t_desvios)
    elementos.append(Spacer(1, 0.4*cm))

    # ── Fragilidades ───────────────────────────────────────────────────────────
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
    elementos.append(Paragraph("Fragilidades Identificadas", s_secao))
    fragilidades = diagnostico.get("fragilidades", [])
    if fragilidades:
        for f in fragilidades:
            elementos.append(Paragraph(f"▸ {f['mensagem']}", s_item_frag))
    else:
        elementos.append(Paragraph("Nenhuma fragilidade relevante identificada (desvio < 1,5 pp).", s_body))

    elementos.append(Spacer(1, 0.3*cm))

    # ── Oportunidades ──────────────────────────────────────────────────────────
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
    elementos.append(Paragraph("Oportunidades de Realocação", s_secao))
    oportunidades = diagnostico.get("oportunidades_realocacao", [])
    if oportunidades:
        for o in oportunidades:
            elementos.append(Paragraph(f"▸ {o['mensagem']}", s_item_opor))
    else:
        elementos.append(Paragraph("Sem sobrealocações relevantes.", s_body))

    elementos.append(Spacer(1, 0.3*cm))

    # ── Sugestões ──────────────────────────────────────────────────────────────
    if sugestoes:
        elementos.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
        elementos.append(Paragraph("Sugestões de Movimentação", s_secao))
        for s in sugestoes:
            elementos.append(Paragraph(f"→ {s}", s_item_sug))

    elementos.append(Spacer(1, 0.6*cm))

    # ── Rodapé ─────────────────────────────────────────────────────────────────
    elementos.append(HRFlowable(width="100%", thickness=0.5, color=DOURADO_ESC, spaceAfter=4))
    elementos.append(Paragraph(
        "Este relatório é um instrumento de apoio à decisão do assessor e não constitui "
        "recomendação formal de investimento. Rentabilidades passadas não garantem resultados futuros. "
        "Braúna Investimentos — assessoria vinculada à XP Investimentos.",
        s_rodape
    ))

    # ── Build ──────────────────────────────────────────────────────────────────
    def fundo_pagina(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(PRETO)
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(elementos, onFirstPage=fundo_pagina, onLaterPages=fundo_pagina)

    # Remove imagem temporária
    if img_path.exists():
        img_path.unlink()

    print(f"Relatório gerado: {caminho_saida}")


def main():
    parser = argparse.ArgumentParser(description="Gera PDF de análise de carteira — Braúna Investimentos")
    parser.add_argument("composicao",    help="JSON de composição (saída do extrair_composicao.py)")
    parser.add_argument("analise",       help="JSON de análise (saída do comparar_allocation.py)")
    parser.add_argument("nome_cliente",  help="Nome completo do cliente")
    parser.add_argument("perfil",        choices=["conservadora","moderada","arrojada","agressiva"])
    parser.add_argument("--output", "-o", default=None, help="Caminho do PDF de saída")
    parser.add_argument("--data",   "-d", default=str(date.today()), help="Data de referência (AAAA-MM-DD)")
    args = parser.parse_args()

    with open(args.composicao, encoding="utf-8") as f:
        dados_comp = json.load(f)
    with open(args.analise, encoding="utf-8") as f:
        dados_analise = json.load(f)

    caixa_pct  = dados_comp.get("caixa_pct", 0.0)
    desvios    = dados_analise["desvios"]
    diagnostico = dados_analise["diagnostico"]
    sugestoes  = dados_analise.get("sugestoes_movimentacao", [])

    if args.output:
        saida = Path(args.output)
    else:
        slug = args.nome_cliente.lower().replace(" ", "-")
        saida = Path(f"{slug}_{args.data}_analise.pdf")

    gerar_pdf(
        nome_cliente=args.nome_cliente,
        perfil=args.perfil,
        desvios=desvios,
        diagnostico=diagnostico,
        sugestoes=sugestoes,
        caixa_pct=caixa_pct,
        caminho_saida=saida,
        data_ref=args.data,
    )


if __name__ == "__main__":
    main()
