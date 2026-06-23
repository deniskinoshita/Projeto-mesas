import sys, os
sys.path.insert(0, 'api')
from apresentacao_pptx import gerar_apresentacao_pptx

d = {
    "nome_cliente": "Cliente Unique",
    "assessor": "Denis Kinoshita",
    "conta": "294954",
    "perfil": "arrojada",
    "objetivo": "crescimento patrimonial com foco em renda variável",
    "data_ref": "29/05/2026",
    "patrimonio": 6065475.02,

    "composicao": {
        "pos_fixado": 5.72,
        "inflacao": 3.07,
        "acoes": 90.65,
        "alternativos": 0.38,
    },

    "desvios": [
        {"cls": "pos_fixado",  "atual": 5.72,  "alvo": 15, "diff": -9.28, "acao": "Aumentar"},
        {"cls": "inflacao",    "atual": 3.07,  "alvo": 10, "diff": -6.93, "acao": "Aumentar"},
        {"cls": "acoes",       "atual": 90.65, "alvo": 70, "diff": 20.65, "acao": "Reduzir"},
        {"cls": "alternativos","atual": 0.38,  "alvo": 5,  "diff": -4.62, "acao": "Aumentar"},
    ],

    "rent": {
        "portfolio": {"mes": -4.29, "ano": -1.43, "12m": 3.19, "24m": 1.57, "cdi_pct": 21.64},
        "cdi":       {"mes": 1.07,  "ano": 5.66,  "12m": 14.76, "24m": 28.28},
        "ibov":      {"mes": -7.22, "ano": 7.86,  "12m": 26.83},
    },

    "checklist": {
        "contato_ativo":          {"nome": "Contato Ativo (30 dias)",    "critico": True,  "feito": True},
        "open_investments":       {"nome": "Open Investments",           "critico": True,  "feito": False},
        "planejamento_financeiro":{"nome": "Planejamento Financeiro",    "critico": False, "feito": False},
        "sucessao":               {"nome": "Planejamento Sucessório",    "critico": False, "feito": False},
        "declaracao_ir":          {"nome": "Declaração de IR",           "critico": False, "feito": True},
        "monitoramento_ativo":    {"nome": "Monitoramento Ativo",        "critico": False, "feito": True},
    },
    "score_servir": 3,

    "cross_ativos_nomes": [],

    "cenario_macro": {
        "global": "Fed mantém postura restritiva. Mercado de trabalho resiliente sustenta consumo americano, mas pressiona juros por mais tempo.",
        "brasil": "Selic em 13,25% com expectativa de cortes graduais a partir do 2º semestre. Ibovespa volátil com pressão cambial e cenário fiscal ainda incerto.",
        "posicionamento": "Levante recomenda redução gradual de renda variável e reforço em renda fixa indexada ao CDI e inflação para perfis arrojados com patrimônio expressivo.",
        "vieses": {"pos_fixado": "positivo", "inflacao": "positivo", "acoes": "neutro", "alternativos": "neutro"},
        "sinais": ["Selic 13,25%", "CDI 14,76% a.a.", "BBAS3 -8,6% mai", "VALE3 +2% mai", "Ibovespa -7,22% mai"],
    },

    "acoes": [
        {"ticker": "BBAS3",  "nome": "Banco do Brasil",    "pct": 50.42, "saldo": 3058195},
        {"ticker": "VALE3",  "nome": "Vale",               "pct": 17.34, "saldo": 1051814},
        {"ticker": "SBSP3",  "nome": "Sabesp",             "pct": 3.33,  "saldo": 201687},
        {"ticker": "NASD11", "nome": "Nasdaq ETF",         "pct": 1.46,  "saldo": 88395},
        {"ticker": "GOGL34", "nome": "Golden Ocean BDR",   "pct": 1.84,  "saldo": 111811},
        {"ticker": "IVVB11", "nome": "S&P 500 ETF",        "pct": 1.28,  "saldo": 77472},
        {"ticker": "COGN3",  "nome": "Cogna",              "pct": 1.13,  "saldo": 68750},
        {"ticker": "SUZB3",  "nome": "Suzano",             "pct": 0.90,  "saldo": 54483},
        {"ticker": "ITLC34", "nome": "Intel BDR",          "pct": 0.81,  "saldo": 49245},
        {"ticker": "TAEE11", "nome": "Taesa",              "pct": 0.71,  "saldo": 43076},
    ],
    "fiis": [],

    "calls": [
        {"ativo": "VALE3",    "tipo": "Manter",  "alvo": "R$ 95",       "prazo": "6 meses",  "upside": "+15%", "risco": "médio", "tese": "Minério sustentado por estímulos chineses"},
        {"ativo": "LCI CDI",  "tipo": "Aplicar", "alvo": "CDI+0.8%",    "prazo": "12 meses", "upside": "CDI+", "risco": "baixo", "tese": "Reduzir concentração em RV com RF isenta"},
        {"ativo": "BBAS3",    "tipo": "Reduzir", "alvo": "Diversificar","prazo": "3 meses",  "upside": "—",    "risco": "alto",  "tese": "50% em um único ativo — concentração crítica"},
    ],

    "estruturadas": [
        {"nome": "COE Ibovespa + Proteção", "tipo": "COE", "retorno": "100% alta Ibov, capital protegido", "vencimento": "Jun/2027", "perfil": "arrojada", "rating": "A"},
    ],

    "sugestoes_produtos": [
        {"classe": "pos_fixado", "label_classe": "Pós Fixado", "gap": -9.28, "produto": {
            "nome": "LCI/LCA CDI+", "taxa": "CDI + 0,8% a.a. (isento IR)", "emissor": "Bancos AAA", "vencimento": "12 meses",
            "motivo": "Aumentar proteção com renda fixa isenta. Reduz dependência de RV e melhora relação risco/retorno.",
            "indicado_por": "Head de Produtos"}},
        {"classe": "inflacao", "label_classe": "Inflação", "gap": -6.93, "produto": {
            "nome": "Tesouro IPCA+ 2029", "taxa": "IPCA + 6,8% a.a.", "emissor": "Tesouro Nacional", "vencimento": "2029",
            "motivo": "Proteção contra inflação e prazo médio adequado ao perfil arrojado com patrimônio de longo prazo.",
            "indicado_por": "Head de Produtos"}},
        {"classe": "alternativos", "label_classe": "Alternativos", "gap": -4.62, "produto": {
            "nome": "BITI11 — Bitcoin ETF", "taxa": "Exposição BTC sem custódia", "emissor": "Hashdex", "vencimento": "ETF Aberto",
            "motivo": "Cliente já possui BITI11 (R$ 23k). Aumentar posição gradualmente para 5% do portfólio.",
            "indicado_por": "Head de Produtos"}},
    ],

    "proximas_acoes": [
        {"acao": "Reduzir BBAS3 — concentração em 50% é risco crítico", "responsavel": "Denis", "prazo": "15 dias", "prioridade": "critica"},
        {"acao": "Aplicar R$ 300k em LCI/LCA CDI+",                     "responsavel": "Denis", "prazo": "30 dias", "prioridade": "alta"},
        {"acao": "Ativar Open Investments",                              "responsavel": "Denis", "prazo": "15 dias", "prioridade": "alta"},
        {"acao": "Agendamento de Planejamento Financeiro",               "responsavel": "Denis", "prazo": "60 dias", "prioridade": "média"},
    ],
    "proximo_contato": "30 dias",
}

data = gerar_apresentacao_pptx(d)
out = os.path.join(os.path.expanduser("~"), "Desktop", "brauna_294954.pptx")
with open(out, "wb") as f:
    f.write(data)
print(f"OK, {len(data)} bytes -> {out}")
