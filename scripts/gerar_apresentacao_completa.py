"""
Gerador de apresentação completa — Conta 243120
Todos os dados extraídos do XPerformance 29/05/2026
"""
import sys, os
sys.path.insert(0, r"C:/Users/Perfil/OneDrive/Área de Trabalho/analise-carteiras-brauna/api")

from apresentacao import gerar_apresentacao

# ── DADOS COMPLETOS DO XPERFORMANCE 29/05/2026 ────────────────────────────────
dados = {
    # Identificação
    "nome_cliente":   "Denis Kinoshita",
    "conta":          "243120",
    "assessor":       "Denis Kinoshita",
    "perfil":         "moderada",
    "data_ref":       "29/05/2026",
    "patrimonio":     1_357_199.67,

    # Rentabilidade
    "rent": {
        "portfolio": {"mes": 0.97, "ano": 6.95, "12m": 18.56, "24m": 26.07},
        "cdi":       {"mes": 1.07, "ano": 5.66, "12m": 14.76, "24m": 28.28},
        "ibovespa":  {"mes":-7.22, "ano": 7.86, "12m": 26.83, "24m": 42.33},
        "ipca":      {"mes": 0.58, "ano": 3.20, "12m":  4.72, "24m": 10.30},
    },
    "rent_12m":  18.56,
    "pct_cdi":   125.8,

    # Estatísticas históricas (24M)
    "estatisticas": {
        "ganho_mes":            13_160.31,
        "ganho_24m":           249_870.39,
        "meses_positivos":      19,
        "meses_negativos":       5,
        "retorno_max_mensal":    4.26,
        "retorno_min_mensal":   -2.66,
        "meses_acima_cdi":      14,
        "meses_abaixo_cdi":     10,
        "volatilidade_12m":      4.66,
        "volatilidade_24m":      5.36,
        "movimentacoes_mes":   -58_033.21,
    },

    # Composição por estratégia
    "composicao": {
        "pos_fixado":  56.81,
        "inflacao":    23.16,
        "pre_fixado":   2.45,
        "acoes":        9.39,
        "fiis":         4.51,
        "multimercado": 0.00,
        "alternativos": 2.18,
        "internacional":0.00,
        "criptomoedas": 0.00,
    },
    "caixa": 1.38,

    # ── POSIÇÃO DETALHADA COMPLETA ────────────────────────────────────────────
    "ativos_detalhe": {
        "pos_fixado": [
            {"nome": "Trend Pós-Fixado FIC FIRF Simples RL",          "saldo": 230_386.43, "perc": 16.98, "rent_mes": 1.06, "rent_ano": 5.65, "rent_24m": 17.74, "indexador": "CDI"},
            {"nome": "ARX Fuji FIC de FIF RF CP RL",                  "saldo": 145_530.42, "perc": 10.72, "rent_mes": 1.09, "rent_ano": 5.72, "rent_24m": 19.39, "indexador": "CDI"},
            {"nome": "Sparta Deb. Incentivadas FIC FIF-Infra RF RL",  "saldo": 107_500.57, "perc":  7.92, "rent_mes": 0.90, "rent_ano": 3.65, "rent_24m":  8.82, "indexador": "CDI"},
            {"nome": "A1 CP High Grade FIF CIC RF CP RL",             "saldo":  71_661.78, "perc":  5.28, "rent_mes": 1.21, "rent_ano": 5.83, "rent_24m":  6.52, "indexador": "CDI"},
            {"nome": "SulAmérica Premium Plus FIRF Ref. DI CP",       "saldo":  57_314.37, "perc":  4.22, "rent_mes": 1.08, "rent_ano": 5.67, "rent_24m":  8.15, "indexador": "CDI"},
            {"nome": "DEB SIMPAR — JAN/2031 — CDI+2,55%",            "saldo":  48_440.57, "perc":  3.57, "rent_mes": 3.81, "rent_ano":14.69, "rent_24m": 11.67, "indexador": "CDI+2,55%"},
            {"nome": "Kinea Incentivado RF CP LP FIF Deb Infra",      "saldo":  41_744.86, "perc":  3.08, "rent_mes": 1.07, "rent_ano": 2.94, "rent_24m":  4.19, "indexador": "CDI"},
            {"nome": "RAM Cash FIF",                                   "saldo":  30_625.32, "perc":  2.26, "rent_mes": 1.08, "rent_ano": 2.66, "rent_24m":  2.66, "indexador": "CDI"},
            {"nome": "CRI JHSF — MAR/2028 — 101% CDI",               "saldo":  22_597.03, "perc":  1.66, "rent_mes": 1.28, "rent_ano": 5.93, "rent_24m": 21.36, "indexador": "CDI"},
            {"nome": "Riza Lotus FIF RF Ref. DI CP RL",               "saldo":  15_228.69, "perc":  1.12, "rent_mes": 1.17, "rent_ano": 5.75, "rent_24m":  9.94, "indexador": "CDI"},
        ],
        "inflacao": [
            {"nome": "Itaú Janeiro Distrib. FIF CIC RF LP",           "saldo":  88_720.28, "perc":  6.54, "rent_mes": 1.36, "rent_ano": 3.93, "rent_24m": 18.50, "indexador": "IPCA"},
            {"nome": "LF BRADESCO — AGO/2031 — IPCA+5,36%",          "saldo":  84_179.74, "perc":  6.20, "rent_mes": 1.14, "rent_ano": 4.88, "rent_24m": 22.26, "indexador": "IPCA+5,36%"},
            {"nome": "LF BRADESCO — AGO/2031 — IPCA+6,60%",          "saldo":  79_237.75, "perc":  5.84, "rent_mes": 1.23, "rent_ano": 5.37, "rent_24m": 25.16, "indexador": "IPCA+6,60%"},
            {"nome": "DEB SIMPAR — SET/2031 — IPCA+8,04%",           "saldo":  51_076.13, "perc":  3.76, "rent_mes": 4.91, "rent_ano":11.19, "rent_24m": 12.30, "indexador": "IPCA+8,04%"},
            {"nome": "DEB ENAUTA — SET/2029 — IPCA+7,11%",           "saldo":  11_135.52, "perc":  0.82, "rent_mes": 0.96, "rent_ano": 5.64, "rent_24m": 32.18, "indexador": "IPCA+7,11%"},
        ],
        "pre_fixado": [
            {"nome": "CRI Habitasec — NOV/2027 — 12,84% a.a.",       "saldo":  23_069.66, "perc":  1.70, "rent_mes": 1.29, "rent_ano": 4.53, "rent_24m": 33.84, "indexador": "Prefixado 12,84%"},
            {"nome": "DEB ENAUTA — SET/2029 — 13,97% a.a.",          "saldo":  10_117.01, "perc":  0.75, "rent_mes": 0.32, "rent_ano": 5.12, "rent_24m": 31.52, "indexador": "Prefixado 13,97%"},
        ],
        "alternativos": [
            {"nome": "Aqua Capital PE Agro FIP Multi — Classe A",     "saldo":  15_137.69, "perc":  1.12, "rent_mes":-2.00, "rent_ano":-1.14, "rent_24m": -0.81, "indexador": "Alternativo"},
            {"nome": "Aqua PE Agro — Trend PE IX FIC RF Simples RL", "saldo":  14_404.85, "perc":  1.06, "rent_mes": 1.07, "rent_ano": 5.69, "rent_24m": 28.41, "indexador": "Alternativo"},
        ],
    },

    # Ações individuais
    "acoes": [
        {"ticker": "VALE3",  "saldo":  41_410.00, "perc": 3.05, "qtd":   500, "rent_mes":  2.05, "rent_ano": 16.85, "rent_24m": 60.47},
        {"ticker": "COGN3",  "saldo":  32_250.00, "perc": 2.38, "qtd": 12900, "rent_mes":-10.07, "rent_ano":-19.42, "rent_24m":  9.70},
        {"ticker": "AURA33", "saldo":  26_358.00, "perc": 1.94, "qtd":   200, "rent_mes": -1.34, "rent_ano": 59.11, "rent_24m": 59.11},
        {"ticker": "RAPT4",  "saldo":  10_360.00, "perc": 0.76, "qtd":  2000, "rent_mes": -2.45, "rent_ano":-10.26, "rent_24m":-33.23},
        {"ticker": "RDOR3",  "saldo":  10_206.00, "perc": 0.75, "qtd":   300, "rent_mes":-11.34, "rent_ano":-16.26, "rent_24m": 16.79},
        {"ticker": "USIM5",  "saldo":   5_540.00, "perc": 0.41, "qtd":   500, "rent_mes": 33.05, "rent_ano": 88.34, "rent_24m": 64.28},
        {"ticker": "ITSA4",  "saldo":   2_584.00, "perc": 0.19, "qtd":   200, "rent_mes": -6.43, "rent_ano": -2.07, "rent_24m": -2.07},
    ],

    # FIIs individuais
    "fiis": [
        {"ticker": "HTMX11", "saldo": 36_448.00, "perc": 2.69, "qtd": 272, "rent_mes": -2.05, "rent_ano": -7.61, "rent_24m":  9.24},
        {"ticker": "KNHY11", "saldo": 16_892.40, "perc": 1.24, "qtd": 168, "rent_mes":  0.60, "rent_ano":  5.72, "rent_24m": 12.87},
        {"ticker": "KOPA11", "saldo":  7_860.00, "perc": 0.58, "qtd":  20, "rent_mes":  2.41, "rent_ano": 17.51, "rent_24m": 29.50},
    ],

    # Movimentações relevantes do mês
    "movimentacoes": [
        {"data":"29/05/2026", "desc":"Resgate CDB Banco Volkswagen MAI/2027",         "valor": 18_087.77},
        {"data":"29/05/2026", "desc":"Retirada TED (C/C 220962)",                    "valor":-18_025.16},
        {"data":"26/05/2026", "desc":"Compra Trend Pós-Fixado (aporte)",              "valor": -8_800.00},
        {"data":"22/05/2026", "desc":"Amortização KOPA11",                           "valor":  2_440.00},
        {"data":"19/05/2026", "desc":"Vencimento LCI POUPEX — MAI/2026",             "valor": 20_299.76},
        {"data":"18/05/2026", "desc":"Compra CDB Banco Volkswagen MAI/2027",         "valor":-34_000.00},
        {"data":"18/05/2026", "desc":"Recebimento TED (aporte)",                     "valor": 34_000.00},
        {"data":"14/05/2026", "desc":"Rendimento KNHY11 (168 cotas)",                "valor":    193.20},
        {"data":"08/05/2026", "desc":"Rendimento HTMX11 (272 cotas)",                "valor":    326.40},
        {"data":"05/05/2026", "desc":"Dividendos FLRY3 (500 ações)",                 "valor":    201.82},
        {"data":"29/05/2026", "desc":"Dividendos COGN3 (12.900 ações)",              "valor":    184.43},
    ],

    # Desvios vs modelo Levante Moderada
    "desvios": [
        {"cls":"pos_fixado",  "label":"Pós Fixado (CDI)",  "atual":56.81,"alvo":44.0, "desvio":+12.81,"status":"fora"},
        {"cls":"inflacao",    "label":"Inflação (IPCA)",   "atual":23.16,"alvo":23.0, "desvio": +0.16,"status":"ok"},
        {"cls":"pre_fixado",  "label":"Pré Fixado",        "atual": 2.45,"alvo":10.0, "desvio": -7.55,"status":"fora"},
        {"cls":"acoes",       "label":"Ações / RV Brasil", "atual": 9.39,"alvo": 5.0, "desvio": +4.39,"status":"atencao"},
        {"cls":"fiis",        "label":"FIIs",              "atual": 4.51,"alvo": 1.5, "desvio": +3.01,"status":"atencao"},
        {"cls":"multimercado","label":"Multimercado",      "atual": 0.00,"alvo": 6.0, "desvio": -6.00,"status":"fora"},
        {"cls":"alternativos","label":"Alternativos",      "atual": 2.18,"alvo": 1.0, "desvio": +1.18,"status":"ok"},
        {"cls":"internacional","label":"Internacional",    "atual": 0.00,"alvo": 9.0, "desvio": -9.00,"status":"fora"},
        {"cls":"criptomoedas","label":"Criptomoedas",      "atual": 0.00,"alvo": 0.5, "desvio": -0.50,"status":"ok"},
    ],

    # Rentabilidade por classe (do XPerformance)
    "rent_por_classe": {
        "pos_fixado":   {"mes": 1.23, "ano": 5.85, "12m": 14.69, "24m":  4.00},
        "inflacao":     {"mes": 1.81, "ano": 5.73, "12m": 12.07, "24m": 30.25},
        "pre_fixado":   {"mes": 0.99, "ano": 4.58, "12m": 15.68, "24m": 33.01},
        "acoes":        {"mes":-0.09, "ano":22.56, "12m": 51.73, "24m": 73.84},
        "fiis":         {"mes":-0.76, "ano":-0.45, "12m":  6.12, "24m": 13.46},
        "alternativos": {"mes":-0.52, "ano": 2.19, "12m":  8.06, "24m":  5.79},
        "multimercado": {"mes": 0.00, "ano": 0.00, "12m":  0.00, "24m":  0.00},
        "internacional":{"mes": 0.00, "ano": 0.00, "12m":  0.00, "24m":  0.00},
        "criptomoedas": {"mes": 0.00, "ano": 0.00, "12m":  0.00, "24m":  0.00},
    },

    # Histórico mensal de rentabilidade (do XPerformance páginas 3-4)
    "historico_mensal": {
        2024: {
            "meses": [-0.15, 0.62, 1.57, 0.20, 2.05, 1.24, 1.28, 1.14, 0.97, 0.74, -0.96, -2.13],
            "ano": 6.70,
        },
        2025: {
            "meses": [-2.66, 0.86, 1.44, 1.55, 2.83, 1.37, -0.30, 1.17, 1.77, 2.88, 1.90, 1.63],
            "ano": 15.28,
        },
        2026: {
            "meses": [4.26, 0.68, -0.06, 0.97, 0.97, None, None, None, None, None, None, None],
            "ano": 6.95,
        },
    },

    # Evolução patrimonial mensal (do XPerformance página 4)
    "evolucao_patrimonial": [
        {"periodo":"mai/26","patrim_inicial":1_407_242.24,"movimentacoes":-58_033.21,"ir":-5_081.46,"iof":-88.21,"patrim_final":1_357_199.67,"ganho":13_160.31,"rent":0.97,"pct_cdi":90.29},
        {"periodo":"abr/26","patrim_inicial":1_394_222.29,"movimentacoes":0.00,"ir":-303.48,"iof":0.00,"patrim_final":1_407_242.24,"ganho":13_323.43,"rent":0.97,"pct_cdi":89.09},
        {"periodo":"mar/26","patrim_inicial":1_395_823.36,"movimentacoes":99.50,"ir":-518.59,"iof":0.00,"patrim_final":1_394_222.29,"ganho":-1_181.98,"rent":-0.06,"pct_cdi":-4.63},
        {"periodo":"fev/26","patrim_inicial":1_361_079.41,"movimentacoes":26_443.59,"ir":-218.88,"iof":0.00,"patrim_final":1_395_823.36,"ganho":8_519.24,"rent":0.68,"pct_cdi":68.20},
        {"periodo":"jan/26","patrim_inicial":1_313_554.52,"movimentacoes":-7_229.42,"ir":-722.18,"iof":0.00,"patrim_final":1_361_079.41,"ganho":55_476.49,"rent":4.26,"pct_cdi":365.55},
        {"periodo":"dez/25","patrim_inicial":1_292_692.04,"movimentacoes":187.47,"ir":-28.65,"iof":0.00,"patrim_final":1_313_554.52,"ganho":20_703.67,"rent":1.63,"pct_cdi":133.31},
        {"periodo":"nov/25","patrim_inicial":1_297_371.94,"movimentacoes":-24_872.00,"ir":-3_453.00,"iof":0.00,"patrim_final":1_292_692.04,"ganho":23_645.09,"rent":1.90,"pct_cdi":180.02},
        {"periodo":"out/25","patrim_inicial":1_142_173.06,"movimentacoes":121_378.39,"ir":-14.54,"iof":0.00,"patrim_final":1_297_371.94,"ganho":33_835.03,"rent":2.88,"pct_cdi":226.05},
        {"periodo":"set/25","patrim_inicial":830_355.39,"movimentacoes":293_362.30,"ir":-146.47,"iof":0.00,"patrim_final":1_142_173.06,"ganho":18_601.84,"rent":1.77,"pct_cdi":145.38},
        {"periodo":"ago/25","patrim_inicial":781_423.29,"movimentacoes":40_000.00,"ir":-302.97,"iof":0.00,"patrim_final":830_355.39,"ganho":9_235.07,"rent":1.17,"pct_cdi":100.19},
        {"periodo":"jul/25","patrim_inicial":784_531.60,"movimentacoes":-400.00,"ir":-77.79,"iof":0.00,"patrim_final":781_423.29,"ganho":-2_630.52,"rent":-0.30,"pct_cdi":-23.72},
        {"periodo":"jun/25","patrim_inicial":946_270.49,"movimentacoes":-171_600.25,"ir":-325.59,"iof":0.00,"patrim_final":784_531.60,"ganho":10_186.95,"rent":1.37,"pct_cdi":124.93},
    ],

    # Sugestões de produtos HP (exemplo — será substituído pelo que o Head cadastrar)
    "sugestoes_produtos": [
        {
            "classe": "internacional", "label_classe": "Internacional", "gap": -9.0,
            "produto": {
                "nome": "IVVB11 — ETF S&P 500", "taxa": "Variável (S&P 500)",
                "emissor": "BlackRock", "vencimento": "Aberto",
                "motivo": "Exposição ao mercado americano em BRL com liquidez diária. Hedge cambial natural.",
                "indicado_por": "Head de Produtos", "indicado_em": "19/06/2026",
            }
        },
        {
            "classe": "multimercado", "label_classe": "Multimercado", "gap": -6.0,
            "produto": {
                "nome": "Kinea Chronos Advisory FIC FIM", "taxa": "CDI+4% (alvo)",
                "emissor": "Kinea Investimentos", "vencimento": "D+30",
                "motivo": "Multiestratégia macro com track record sólido. Descorrelacionado de renda fixa.",
                "indicado_por": "Head de Produtos", "indicado_em": "19/06/2026",
            }
        },
        {
            "classe": "pre_fixado", "label_classe": "Pré Fixado", "gap": -7.55,
            "produto": {
                "nome": "Tesouro Prefixado 2029 (NTN-F)", "taxa": "≈ 13,8% a.a.",
                "emissor": "Tesouro Nacional", "vencimento": "2029",
                "motivo": "Trava taxa antes do ciclo de corte da Selic. Rentabilidade real positiva mesmo com IPCA em 5%.",
                "indicado_por": "Head de Produtos", "indicado_em": "19/06/2026",
            }
        },
    ],

    # Cenário macro — Levante Asset Junho 2026
    "cenario_macro": {
        "global": "Persistência inflacionária global impulsionada por conflito no Oriente Médio (Brent US$ 92,5/barril). Fed hawkish: juros elevados por mais tempo. PCE abril 3,8% a/a. Dólar forte. S&P500 +5,1% e Nasdaq +8,3% em maio puxados por IA.",
        "brasil": "Selic deve encerrar ciclo de corte na próxima reunião. IPCA-15 maio 0,62% acima do esperado, núcleos pressionados. Risco fiscal relevante. Ibovespa -7,2% em maio por saída de estrangeiro — precificação atraente para médio/longo prazo.",
        "posicionamento": "Reduzindo FIIs e Multimercados. Aumentando Renda Variável Brasil (correção recente gera valor). Crédito: spreads estabilizando. Duration curta em renda fixa. Inflação implícita em alta em toda extensão da curva.",
        "vieses": {
            "pos_fixado": "neutro",
            "inflacao": "positivo",
            "pre_fixado": "neutro",
            "acoes": "positivo",
            "fiis": "negativo",
            "multimercado": "negativo",
            "internacional": "positivo",
        }
    },

    "alertas_relevantes": [
        {
            "produto": "COGN3",
            "tipo": "atencao",
            "mensagem": "COGN3 acumula -19,42% no ano. Alta volatilidade inconsistente com perfil moderado. Avaliar redução.",
            "data": "19/06/2026",
        },
        {
            "produto": "HTMX11",
            "tipo": "atencao",
            "mensagem": "FIIs sob pressão com juros elevados. HTMX11 -7,61% no ano. Head recomenda redução da posição.",
            "data": "19/06/2026",
        },
    ],
}

# Gerar PDF
print("Gerando apresentação completa...")
pdf_bytes = gerar_apresentacao(dados)

saida = r"C:/Users/Perfil/OneDrive/Área de Trabalho/analise-carteiras-brauna/clientes/243120_DenisKinoshita/apresentacao_243120_29-05-2026.pdf"
with open(saida, "wb") as f:
    f.write(pdf_bytes)

print(f"PDF gerado: {saida}")
print(f"Tamanho: {len(pdf_bytes):,} bytes  ({len(pdf_bytes)//1024} KB)")
print("Slides: Capa · Patrimônio · Comparativo · Ações/FIIs · Cenário · Sugestões · Próximos Passos")
