"""
Simula 1 cliente por assessor (16 assessores) e salva diretamente
no Redis (e /tmp fallback), sem precisar de PDF.
"""
import sys, os, json, uuid
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from index import (
    _load, _save, _DATA_FILE, _HIST_FILE, _FICHA_FILE,
    load_clientes, save_clientes, load_hist, save_hist,
    load_fichas, save_fichas,
)

ASSESSORES = [
    {"nome": "Alex Alves dos Santos",                        "perfil": "moderada",     "patrimonio": 350_000},
    {"nome": "Andre Guilherme Leite Figueiredo",             "perfil": "arrojada",     "patrimonio": 850_000},
    {"nome": "Bruno Seiji Ito",                              "perfil": "conservadora", "patrimonio": 220_000},
    {"nome": "Carlos Fernando Victor Bolivar Moreira Neto",  "perfil": "moderada",     "patrimonio": 480_000},
    {"nome": "Carolina Custodio Siqueira",                   "perfil": "arrojada",     "patrimonio": 610_000},
    {"nome": "Denis Albertino dos Santos Kinoshita",         "perfil": "agressiva",    "patrimonio": 6_065_475},
    {"nome": "Felipe Fraga",                                 "perfil": "arrojada",     "patrimonio": 1_200_000},
    {"nome": "Felipe Santos Nishio",                         "perfil": "agressiva",    "patrimonio": 3_400_000},
    {"nome": "Giuseppe Hilario Neto",                        "perfil": "moderada",     "patrimonio": 520_000},
    {"nome": "Lucas Landroni Cozzi",                         "perfil": "arrojada",     "patrimonio": 1_800_000},
    {"nome": "Marcelo Ramos Dias",                           "perfil": "arrojada",     "patrimonio": 2_100_000},
    {"nome": "Matheus Escoza Milani",                        "perfil": "conservadora", "patrimonio": 190_000},
    {"nome": "Michael Ademilson Santos da Silva",            "perfil": "moderada",     "patrimonio": 980_000},
    {"nome": "Paulo Roberto Negreiros Sobrinho",             "perfil": "moderada",     "patrimonio": 740_000},
    {"nome": "Tatiane Cristina da Silva Cecchetti",          "perfil": "arrojada",     "patrimonio": 870_000},
    {"nome": "Thiago Brunelli Borba",                        "perfil": "conservadora", "patrimonio": 145_000},
]

COMPOSICOES = {
    "conservadora": {"pos_fixado": 65, "inflacao": 18, "pre_fixado": 8, "acoes": 0, "fiis": 2, "multimercado": 4, "internacional": 3, "alternativos": 0},
    "moderada":     {"pos_fixado": 40, "inflacao": 22, "pre_fixado": 8, "acoes": 6, "fiis": 4, "multimercado": 8, "internacional": 10, "alternativos": 2},
    "arrojada":     {"pos_fixado": 20, "inflacao": 25, "pre_fixado": 10, "acoes": 20, "fiis": 5, "multimercado": 10, "internacional": 8, "alternativos": 2},
    "agressiva":    {"pos_fixado": 8,  "inflacao": 12, "pre_fixado": 5,  "acoes": 55, "fiis": 3, "multimercado": 8, "internacional": 7, "alternativos": 2},
}

RENTABILIDADES = {
    "conservadora": {"mes": 0.95, "ano": 5.40, "12m": 13.80, "24m": 26.50, "cdi_pct": 93.5},
    "moderada":     {"mes": 0.72, "ano": 4.10, "12m": 11.20, "24m": 22.80, "cdi_pct": 75.9},
    "arrojada":     {"mes": -1.20, "ano": 3.60, "12m": 14.50, "24m": 20.10, "cdi_pct": 98.2},
    "agressiva":    {"mes": -4.29, "ano": -1.43, "12m": 3.19, "24m": 1.57, "cdi_pct": 21.6},
}

CHECKLISTS = {
    "conservadora": {
        "contato_ativo":          {"nome": "Contato Ativo (30d)",       "critico": True,  "feito": True},
        "open_investments":       {"nome": "Open Investments",           "critico": True,  "feito": True},
        "planejamento_financeiro":{"nome": "Planejamento Financeiro",    "critico": False, "feito": True},
        "declaracao_ir":          {"nome": "Declaração de IR",           "critico": False, "feito": True},
        "monitoramento_ativo":    {"nome": "Monitoramento Ativo",        "critico": False, "feito": True},
    },
    "moderada": {
        "contato_ativo":          {"nome": "Contato Ativo (30d)",       "critico": True,  "feito": True},
        "open_investments":       {"nome": "Open Investments",           "critico": True,  "feito": False},
        "planejamento_financeiro":{"nome": "Planejamento Financeiro",    "critico": False, "feito": True},
        "declaracao_ir":          {"nome": "Declaração de IR",           "critico": False, "feito": False},
        "monitoramento_ativo":    {"nome": "Monitoramento Ativo",        "critico": False, "feito": True},
    },
    "arrojada": {
        "contato_ativo":          {"nome": "Contato Ativo (30d)",       "critico": True,  "feito": True},
        "open_investments":       {"nome": "Open Investments",           "critico": True,  "feito": False},
        "planejamento_financeiro":{"nome": "Planejamento Financeiro",    "critico": False, "feito": False},
        "declaracao_ir":          {"nome": "Declaração de IR",           "critico": False, "feito": True},
        "monitoramento_ativo":    {"nome": "Monitoramento Ativo",        "critico": False, "feito": True},
        "sucessao":               {"nome": "Planejamento Sucessório",    "critico": False, "feito": False},
    },
    "agressiva": {
        "contato_ativo":          {"nome": "Contato Ativo (30d)",       "critico": True,  "feito": True},
        "open_investments":       {"nome": "Open Investments",           "critico": True,  "feito": False},
        "planejamento_financeiro":{"nome": "Planejamento Financeiro",    "critico": False, "feito": False},
        "declaracao_ir":          {"nome": "Declaração de IR",           "critico": False, "feito": True},
        "monitoramento_ativo":    {"nome": "Monitoramento Ativo",        "critico": False, "feito": True},
        "sucessao":               {"nome": "Planejamento Sucessório",    "critico": False, "feito": False},
    },
}

NOMES_CLIENTES = [
    "Roberto Almeida da Silva", "Maria Fernanda Costa", "João Paulo Machado",
    "Ana Carolina Ferreira", "Carlos Eduardo Santos", "Luciana Oliveira Mendes",
    "Pedro Henrique Lima", "Gabriela Rodrigues", "Fernando Souza Neto",
    "Patricia Vieira Gomes", "André Luis Martins", "Camila Pereira",
    "Ricardo Teixeira Borges", "Juliana Nascimento", "Marcio Cavalcanti",
    "Beatriz Alves Moreira",
]

def calcular_score(checklist):
    total = len(checklist)
    feitos = sum(1 for v in checklist.values() if isinstance(v, dict) and v.get("feito"))
    pendentes_criticos = sum(1 for v in checklist.values() if isinstance(v, dict) and v.get("critico") and not v.get("feito"))
    pendentes_altos = total - feitos - pendentes_criticos
    score = round(feitos / total * 5, 1) if total > 0 else 0
    return score, pendentes_criticos, pendentes_altos

def calcular_status(score, rent_pct_cdi, pendentes_criticos):
    if pendentes_criticos > 0 or rent_pct_cdi < 70:
        return "critico"
    elif rent_pct_cdi < 85 or score < 3:
        return "atencao"
    return "ok"

hoje = datetime.now()
clientes = load_clientes()
hist = load_hist()
fichas = load_fichas()

# Remove simulados anteriores para não duplicar
clientes = [c for c in clientes if not c.get("simulado")]

adicionados = 0
for i, ass in enumerate(ASSESSORES):
    nome_cli = NOMES_CLIENTES[i]
    assessor  = ass["nome"]
    perfil    = ass["perfil"]
    patrimonio= ass["patrimonio"]
    comp      = dict(COMPOSICOES[perfil])
    rent_p    = RENTABILIDADES[perfil]
    checklist = CHECKLISTS[perfil]

    score, pend_crit, pend_alto = calcular_score(checklist)
    rent12_pct_cdi = rent_p["cdi_pct"]
    status = calcular_status(score, rent12_pct_cdi, pend_crit)

    fkey = f"{assessor}|{nome_cli}".lower().strip()
    data_hoje = hoje.strftime("%d/%m/%Y")

    resumo = {
        "id": str(uuid.uuid4())[:8],
        "assessor": assessor,
        "nome": nome_cli,
        "perfil": perfil,
        "data": data_hoje,
        "patrimonio": patrimonio,
        "score_servir": score,
        "pendentes_criticos": pend_crit,
        "pendentes_altos": pend_alto,
        "cross_ativos": 0,
        "rent12_pct_cdi": rent12_pct_cdi,
        "alertas_count": 0,
        "status": status,
        "nota_lider": "",
        "analisado_em": hoje.strftime("%d/%m/%Y %H:%M"),
        "simulado": True,
    }
    clientes.insert(0, resumo)

    entrada_hist = {
        "data": data_hoje,
        "hora": hoje.strftime("%H:%M"),
        "patrimonio": patrimonio,
        "perfil": perfil,
        "composicao": comp,
        "score_servir": score,
        "cross_ativos": 0,
        "status": status,
        "rent12_pct_cdi": rent12_pct_cdi,
        "objetivo": f"Crescimento patrimonial — perfil {perfil}",
    }
    # Adiciona entrada anterior (simula histórico com 2 análises)
    entrada_anterior = dict(entrada_hist)
    entrada_anterior["data"] = (hoje - timedelta(days=30)).strftime("%d/%m/%Y")
    entrada_anterior["patrimonio"] = int(patrimonio * 0.97)
    entrada_anterior["rent12_pct_cdi"] = rent12_pct_cdi - 2

    reg_hist = hist.get(fkey, {
        "assessor": assessor, "nome": nome_cli,
        "perfil": perfil, "objetivo": f"Crescimento patrimonial — perfil {perfil}",
        "entradas": [],
    })
    reg_hist["entradas"] = ([entrada_hist, entrada_anterior] + reg_hist.get("entradas", []))[:4]
    hist[fkey] = reg_hist

    fichas[fkey] = {
        "nome": nome_cli, "assessor": assessor, "perfil": perfil,
        "objetivo": f"Crescimento patrimonial — perfil {perfil}",
        "checklist": checklist,
        "cross_ativos": [],
        "atualizado_em": hoje.strftime("%d/%m/%Y %H:%M"),
    }

    adicionados += 1
    status_icon = "[CRIT]" if status=="critico" else "[ATEN]" if status=="atencao" else "[OK]  "
    print(f"{status_icon} {assessor[:35]:<35} | {nome_cli[:25]:<25} | {perfil:<12} | R${patrimonio/1e6:.2f}M | Score {score} | CDI {rent12_pct_cdi}%")

save_clientes(clientes[:500])
save_hist(hist)
save_fichas(fichas)

print(f"\nOK: {adicionados} clientes simulados criados e salvos no Redis!")
print(f"   Total clientes: {len(clientes)}")
print(f"   Total registros hist: {len(hist)}")
