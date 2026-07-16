"""
_ir_aliquota_regressiva / _liquido_pct_cdi_equivalente (tributacao.json).

Regra do domínio: nunca comparar taxa bruta de um produto tributável com a
taxa (já líquida) de um produto isento — é preciso levar tudo a %CDI líquido
equivalente antes de rankear. O caso central deste arquivo é o que expunha o
bug antigo: uma LCA isenta de 90% CDI parecia perder para um CDB tributável de
130% CDI olhando o bruto, mas depois do IR regressivo (22,5% em prazo curto)
o CDB líquido (~100,75% CDI) ainda fica acima da LCA (90% CDI) — o ranking
"isento sempre primeiro" erraria esse caso.
"""
import pytest

import api.index as idx


@pytest.mark.parametrize("dias,aliquota_esperada", [
    (30, 0.225),
    (200, 0.20),
    (500, 0.175),
    (1000, 0.15),
])
def test_ir_aliquota_regressiva_por_prazo(dias, aliquota_esperada):
    assert idx._ir_aliquota_regressiva(dias) == aliquota_esperada


def test_ir_aliquota_regressiva_sem_prazo_retorna_none():
    assert idx._ir_aliquota_regressiva(0) is None
    assert idx._ir_aliquota_regressiva(None) is None


def test_isento_liquido_igual_ao_bruto():
    produto = {"isento": True, "tax_max": "93,50% CDI"}
    assert idx._liquido_pct_cdi_equivalente(produto) == pytest.approx(93.5, abs=0.01)


def test_tributavel_desconta_ir_regressivo_do_prazo():
    produto = {"isento": False, "tax_max": "120,00% CDI", "carencia": 90}
    esperado = 120.0 * (1 - 0.225)
    assert idx._liquido_pct_cdi_equivalente(produto) == pytest.approx(esperado, abs=0.01)


def test_tributavel_sem_prazo_nao_da_para_determinar_aliquota():
    produto = {"isento": False, "tax_max": "120,00% CDI"}
    assert idx._liquido_pct_cdi_equivalente(produto) is None


def test_cdb_tributavel_rankeia_acima_de_lca_isenta_quando_liquido_e_maior():
    """Caso que expõe o bug antigo: bruto o CDB (130% CDI) já parece melhor que
    a LCA (90% CDI) — mas o que importa é confirmar que, pelo LÍQUIDO, o CDB
    (130 * (1-0.225) ~= 100,75% CDI) segue à frente da LCA isenta (90% CDI),
    e não o contrário (a suposição "isento sempre primeiro" erraria aqui)."""
    lca = {"ativo": "LCA Isenta 90", "isento": True, "tax_max": "90,00% CDI", "risco": 5}
    cdb = {"ativo": "CDB Tributavel 130", "isento": False, "tax_max": "130,00% CDI",
           "carencia": 90, "risco": 5}

    liq_lca = idx._liquido_pct_cdi_equivalente(lca)
    liq_cdb = idx._liquido_pct_cdi_equivalente(cdb)

    assert liq_lca == pytest.approx(90.0, abs=0.01)
    assert liq_cdb == pytest.approx(130.0 * (1 - 0.225), abs=0.01)
    assert liq_cdb > liq_lca

    def _sort_key(p):
        liq = idx._liquido_pct_cdi_equivalente(p)
        risco_n = float(p.get("risco")) if isinstance(p.get("risco"), (int, float)) else 99.0
        if liq is not None:
            return (0, -liq, risco_n)
        return (1, not p.get("isento"), risco_n)

    ordenado = sorted([lca, cdb], key=_sort_key)
    assert [p["ativo"] for p in ordenado] == ["CDB Tributavel 130", "LCA Isenta 90"]
