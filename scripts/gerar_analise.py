import os, json
from datetime import datetime

pasta = r'C:/Users/Perfil/OneDrive/Área de Trabalho/analise-carteiras-brauna/clientes/243120_DenisKinoshita'
os.makedirs(pasta, exist_ok=True)

dados_cliente = {
    "codigo_cliente": "243120",
    "nome_cliente": "Não identificado no PDF",
    "assessor": "Denis Kinoshita",
    "data_referencia": "29/05/2026",
    "patrimonio_total_bruto": 1357199.67,
    "perfil_suitability": "Moderado (inferido pela composição)",
    "rentabilidade_mes": "0,97%",
    "rentabilidade_ano": "6,95%",
    "rentabilidade_12m": "18,56%",
    "rentabilidade_24m": "26,07%",
    "ganho_mes": 13160.31,
    "ganho_24m": 249870.39,
    "gerado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
}

carteira = {
    "data_referencia": "29/05/2026",
    "patrimonio_total": 1357199.67,
    "estrategias": {
        "pos_fixado": {
            "label": "Pos Fixado (CDI)",
            "saldo": 771030.04,
            "percentual": 56.81,
            "ativos": [
                {"nome": "Trend Pos-Fixado FIC FIRF Simples RL", "saldo": 230386.43, "perc": 16.98, "indexador": "CDI"},
                {"nome": "ARX Fuji FIC de FIF RF CP RL", "saldo": 145530.42, "perc": 10.72, "indexador": "CDI"},
                {"nome": "Sparta Debentures Incentivadas FIC FIF-Infra RF", "saldo": 107500.57, "perc": 7.92, "indexador": "CDI"},
                {"nome": "A1 CP High Grade FIF CIC RF CP RL", "saldo": 71661.78, "perc": 5.28, "indexador": "CDI"},
                {"nome": "SulAmerica Premium Plus FIRF Ref DI CP", "saldo": 57314.37, "perc": 4.22, "indexador": "CDI"},
                {"nome": "DEB SIMPAR JAN/2031 CDI+2,55%", "saldo": 48440.57, "perc": 3.57, "indexador": "CDI+spread"},
                {"nome": "Kinea Incentivado RF CP LP FIF Deb Infra", "saldo": 41744.86, "perc": 3.08, "indexador": "CDI"},
                {"nome": "RAM Cash FIF", "saldo": 30625.32, "perc": 2.26, "indexador": "CDI"},
                {"nome": "CRI JHSF MAR/2028 101% CDI", "saldo": 22597.03, "perc": 1.66, "indexador": "CDI"},
                {"nome": "Riza Lotus FIF RF Ref DI CP", "saldo": 15228.69, "perc": 1.12, "indexador": "CDI"},
            ]
        },
        "inflacao": {
            "label": "Inflacao (IPCA)",
            "saldo": 314349.42,
            "percentual": 23.16,
            "ativos": [
                {"nome": "Itau Janeiro Distribuidores FIF CIC RF LP", "saldo": 88720.28, "perc": 6.54, "indexador": "IPCA"},
                {"nome": "LF BANCO BRADESCO AGO/2031 IPCA+5,36%", "saldo": 84179.74, "perc": 6.20, "indexador": "IPCA+spread"},
                {"nome": "LF BANCO BRADESCO AGO/2031 IPCA+6,60%", "saldo": 79237.75, "perc": 5.84, "indexador": "IPCA+spread"},
                {"nome": "DEB SIMPAR SET/2031 IPCA+8,04%", "saldo": 51076.13, "perc": 3.76, "indexador": "IPCA+spread"},
                {"nome": "DEB ENAUTA SET/2029 IPCA+7,11%", "saldo": 11135.52, "perc": 0.82, "indexador": "IPCA+spread"},
            ]
        },
        "pre_fixado": {
            "label": "Pre Fixado",
            "saldo": 33186.66,
            "percentual": 2.45,
            "ativos": [
                {"nome": "CRI Habitasec NOV/2027 12,84%", "saldo": 23069.66, "perc": 1.70, "indexador": "Prefixado"},
                {"nome": "DEB ENAUTA SET/2029 13,97%", "saldo": 10117.01, "perc": 0.75, "indexador": "Prefixado"},
            ]
        },
        "acoes": {
            "label": "Acoes / RV Brasil",
            "saldo": 127408.00,
            "percentual": 9.39,
            "ativos": [
                {"nome": "VALE3", "saldo": 41410.00, "perc": 3.05, "indexador": "RV", "qtd": 500},
                {"nome": "COGN3", "saldo": 32250.00, "perc": 2.38, "indexador": "RV", "qtd": 12900},
                {"nome": "AURA33", "saldo": 26358.00, "perc": 1.94, "indexador": "RV", "qtd": 200},
                {"nome": "RAPT4", "saldo": 10360.00, "perc": 0.76, "indexador": "RV", "qtd": 2000},
                {"nome": "RDOR3", "saldo": 10206.00, "perc": 0.75, "indexador": "RV", "qtd": 300},
                {"nome": "USIM5", "saldo": 5540.00, "perc": 0.41, "indexador": "RV", "qtd": 500},
                {"nome": "ITSA4", "saldo": 2584.00, "perc": 0.19, "indexador": "RV", "qtd": 200},
                {"nome": "BBASR221 (Opcoes)", "saldo": -1300.00, "perc": -0.10, "indexador": "Opcoes", "obs": "Posicao negativa"},
            ]
        },
        "fiis": {
            "label": "FIIs / Fundos Listados",
            "saldo": 61200.40,
            "percentual": 4.51,
            "ativos": [
                {"nome": "HTMX11", "saldo": 36448.00, "perc": 2.69, "indexador": "FII", "qtd": 272},
                {"nome": "KNHY11", "saldo": 16892.40, "perc": 1.24, "indexador": "FII", "qtd": 168},
                {"nome": "KOPA11", "saldo": 7860.00, "perc": 0.58, "indexador": "FII", "qtd": 20},
            ]
        },
        "alternativos": {
            "label": "Alternativo",
            "saldo": 29542.54,
            "percentual": 2.18,
            "ativos": [
                {"nome": "Aqua Capital PE Agro FIP Multi Classe A", "saldo": 15137.69, "perc": 1.12, "indexador": "Alternativo"},
                {"nome": "Aqua PE Agro Trend PE IX FIC RF Simples RL", "saldo": 14404.85, "perc": 1.06, "indexador": "Alternativo"},
            ]
        },
        "multimercado": {"label": "Multimercado", "saldo": 0, "percentual": 0.0, "ativos": []},
        "internacional": {"label": "Internacional", "saldo": 0, "percentual": 0.0, "ativos": []},
        "criptomoedas": {"label": "Criptomoedas", "saldo": 0, "percentual": 0.0, "ativos": []},
        "caixa": {"label": "Caixa", "saldo": 18756.30, "percentual": 1.38, "ativos": []},
    }
}

modelo_moderada = {
    "pos_fixado": 44, "inflacao": 23, "pre_fixado": 10,
    "acoes": 5, "fiis": 1.5, "multimercado": 6,
    "alternativos": 1, "internacional": 9, "criptomoedas": 0.5
}

atual = {
    "pos_fixado": 56.81, "inflacao": 23.16, "pre_fixado": 2.45,
    "acoes": 9.39, "fiis": 4.51, "multimercado": 0.0,
    "alternativos": 2.18, "internacional": 0.0, "criptomoedas": 0.0
}

labels = {
    "pos_fixado":"Pos Fixado (CDI)", "inflacao":"Inflacao (IPCA)", "pre_fixado":"Pre Fixado",
    "acoes":"Acoes / RV Brasil", "fiis":"FIIs / Fundos Listados", "multimercado":"Multimercado",
    "alternativos":"Alternativos", "internacional":"Internacional", "criptomoedas":"Criptomoedas"
}

def status_cls(a, m):
    d = abs(a - m)
    if d <= 2: return "Adequado"
    elif d <= 5: return "Atencao"
    else: return "Fora do perfil"

analise = {
    "perfil_utilizado": "Moderado (Levante Asset Junho 2026)",
    "data_analise": datetime.now().strftime("%d/%m/%Y %H:%M"),
    "classes": {}
}
for cls in modelo_moderada:
    a = atual.get(cls, 0)
    m = modelo_moderada[cls]
    desvio = round(a - m, 2)
    analise["classes"][cls] = {
        "label": labels[cls],
        "atual": a,
        "modelo": m,
        "desvio": desvio,
        "status": status_cls(a, m)
    }

with open(f"{pasta}/dados_cliente.json", "w", encoding="utf-8") as f:
    json.dump(dados_cliente, f, ensure_ascii=False, indent=2)
with open(f"{pasta}/carteira_atual.json", "w", encoding="utf-8") as f:
    json.dump(carteira, f, ensure_ascii=False, indent=2)
with open(f"{pasta}/analise_perfil.json", "w", encoding="utf-8") as f:
    json.dump(analise, f, ensure_ascii=False, indent=2)

print("JSONs salvos com sucesso em:", pasta)
for cls, v in analise["classes"].items():
    print(f"  {v['label']:30s} atual={v['atual']:5.1f}% modelo={v['modelo']:4.1f}% desvio={v['desvio']:+.2f}%  [{v['status']}]")
