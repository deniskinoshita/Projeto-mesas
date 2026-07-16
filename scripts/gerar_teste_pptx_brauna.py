import sys, os
sys.path.insert(0, 'api')
from pptx_brauna import gerar_pptx_cliente

d = {
    "nome":      "Maria Fernanda Costa",
    "assessor":  "Denis Kinoshita",
    "perfil":    "arrojada",
    "data_ref":  "15/07/2026",
    "patrimonio": 2_350_000,
    "rent": {
        "mes":     -1.20,
        "ano":     6.40,
        "12m":     -2.80,   # negativo de propósito -> testa seta/sinal do card
        "24m":     18.90,
        "cdi_pct": -19.6,
    },
    # 9 classes (todas as chaves de CLS_LABEL) para testar o layout de linhas no limite
    "composicao": {
        "pos_fixado":    18,
        "inflacao":      12,
        "pre_fixado":    6,
        "acoes":         28,   # bem acima do modelo -> desvio grande/vermelho
        "fiis":          4,
        "multimercado":  7,
        "internacional": 14,
        "alternativos":  6,
        "criptomoedas":  5,    # atual > 0, alvo = 0 -> testa marcador no extremo esquerdo
    },
    "modelo": {
        "pos_fixado":    25,
        "inflacao":      15,
        "pre_fixado":    8,
        "acoes":         12,
        "fiis":          5,
        "multimercado":  6,
        "internacional": 15,
        "alternativos":  14,   # atual bem abaixo -> desvio grande negativo
        "criptomoedas":  0,
    },
    "desvios": [
        {"label": "Ações",         "real": 28, "alvo": 12, "desvio": 16},
        {"label": "Alternativos",  "real": 6,  "alvo": 14, "desvio": -8},
        {"label": "Pós Fixado",    "real": 18, "alvo": 25, "desvio": -7},
        {"label": "Criptomoedas",  "real": 5,  "alvo": 0,  "desvio": 5},
    ],
    "acoes": [
        {"ticker": "PETR4", "nome": "Petrobras",          "pct": 9.5},
        {"ticker": "BBAS3", "nome": "Banco do Brasil",    "pct": 7.1},
        {"ticker": "VALE3", "nome": "Vale S.A.",          "pct": 5.4},
        {"ticker": "WEGE3", "nome": "WEG",                "pct": 3.8},
        {"ticker": "ITUB4", "nome": "Itaú Unibanco",      "pct": 2.2},
    ],
    "fiis": [
        {"ticker": "KNRI11", "nome": "Kinea Renda Imobiliária", "pct": 2.5},
        {"ticker": "HGLG11", "nome": "CSHG Logística",          "pct": 1.5},
    ],
    "rf_ativos": [
        {"nome": "Tesouro Selic 2029",        "saldo": 220_000, "classe": "pos_fixado"},
        {"nome": "CDB Banco Inter 115% CDI",  "saldo": 180_000, "classe": "pos_fixado"},
        {"nome": "Tesouro IPCA+ 2035",        "saldo": 150_000, "classe": "inflacao"},
        {"nome": "LCA Santander 96% CDI",     "saldo": 90_000,  "classe": "pos_fixado"},
        {"nome": "Debênture Rumo 2030",       "saldo": 85_000,  "classe": "pre_fixado"},
        {"nome": "CRI Vinci 2028",            "saldo": 60_000,  "classe": "inflacao"},
        {"nome": "Tesouro Prefixado 2027",    "saldo": 55_000,  "classe": "pre_fixado"},
        {"nome": "CDB Nubank 108% CDI",       "saldo": 40_000,  "classe": "pos_fixado"},
        {"nome": "LCI Itaú 95% CDI",          "saldo": 35_000,  "classe": "pos_fixado"},
        {"nome": "CRA Suzano 2029",           "saldo": 20_000,  "classe": "inflacao"},
    ],
    "checklist": {
        "contato_ativo":        True,
        "open_investments":     True,
        "previdencia":          False,
        "seguro_vida":          False,
        "planejamento_sucesso": False,
        "declaracao_ir":        True,
        "consorcio":            False,
        "cambio":               True,
        "credito_estruturado":  False,
        "rebalanceamento":      False,
    },
    "cross_ativos":  ["cambio", "declaracao_ir"],
    "score_servir":  2.4,
    "status":        "critico",   # testa ícone ✕ + cor vermelha no card de status
    "objetivo":      "Preservação de capital com exposição internacional",
    "alertas":       ["Concentração em ações 16pp acima do modelo", "Alternativos 8pp abaixo do modelo"],
    "nota_lider":    "Rebalancear ações e revisar exposição internacional na próxima reunião",
}

data = gerar_pptx_cliente(d)
downloads = os.path.join(os.path.expanduser("~"), "Downloads")
out_dir = downloads if os.path.isdir(downloads) else os.path.expanduser("~")
out = os.path.join(out_dir, "teste_pptx_brauna.pptx")
with open(out, "wb") as f:
    f.write(data)
print(f"OK, {len(data):,} bytes -> {out}")
