"""
calcular_concentracao_emissor — teto institucional XP de 5% do AUC por emissor
de crédito (memória 'limites-alocacao-institucional-xp'), agrupando por
EMISSOR (não por produto).

Motivação: um mesmo emissor pode ter mais de um título na carteira (ex.: uma
CRA e uma CRI da mesma empresa) e nenhuma das duas, isoladamente, estourar o
teto — só a soma por emissor revela a concentração real. Diferente de
calcular_exposicao_fgc: aqui entra qualquer emissor de crédito (não só
instrumentos com garantia do FGC) e o teto é 5% do AUC, não R$250 mil por
conglomerado.
"""
import pytest

import api.index as idx


def test_dois_titulos_do_mesmo_emissor_somam_e_estouram_o_teto():
    auc = 1_000_000.0
    rf_ativos = [
        {"emissor": "BRF", "nome": "CRA BRF - JUL/2030", "valor": 30_000.0, "vencimento": "15/07/2030"},
        {"emissor": "BRF", "nome": "CRI BRF - JAN/2028", "valor": 25_000.0, "vencimento": "18/01/2028"},
    ]
    r = idx.calcular_concentracao_emissor(rf_ativos, auc)

    assert r["emissores_acima_do_limite"] == 1
    brf = r["por_emissor"][0]
    assert brf["emissor"] == "BRF"
    assert brf["exposicao_total"] == pytest.approx(55_000.0, abs=0.01)
    assert brf["pct_auc"] == pytest.approx(5.5, abs=0.01)
    assert brf["status"] == "acima_do_limite"
    assert len(brf["produtos"]) == 2  # os 2 títulos ficam auditáveis, não só a soma


def test_emissor_unico_abaixo_do_teto_fica_ok():
    rf_ativos = [{"emissor": "MARFRIG", "nome": "CRA MARFRIG - JUL/2031", "valor": 20_000.0}]
    r = idx.calcular_concentracao_emissor(rf_ativos, 1_000_000.0)
    assert r["por_emissor"][0]["status"] == "ok"
    assert r["emissores_acima_do_limite"] == 0


def test_proximo_do_teto_fica_em_alerta_intermediario():
    # 4,5% do AUC: abaixo do limite de 5%, mas dentro da faixa de atenção (>=80% do teto).
    rf_ativos = [{"emissor": "JBS", "nome": "CRA JBS - MAI/2044", "valor": 45_000.0}]
    r = idx.calcular_concentracao_emissor(rf_ativos, 1_000_000.0)
    assert r["por_emissor"][0]["status"] == "proximo_do_limite"


def test_sem_auc_nao_calcula_nada():
    r = idx.calcular_concentracao_emissor([{"emissor": "BRF", "valor": 100.0}], 0)
    assert r["por_emissor"] == []


def test_ativos_sem_emissor_ou_valor_sao_ignorados():
    rf_ativos = [
        {"emissor": None, "valor": 50_000.0},
        {"emissor": "BRF", "valor": None},
        {"emissor": "BRF", "valor": 0},
    ]
    r = idx.calcular_concentracao_emissor(rf_ativos, 1_000_000.0)
    assert r["por_emissor"] == []
