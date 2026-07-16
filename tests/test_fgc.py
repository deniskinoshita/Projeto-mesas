"""
calcular_exposicao_fgc — exposição unificada por conglomerado (fgc.json).

Cobre os casos que motivaram a unificação (antes havia duas heurísticas
divergentes, nenhuma agrupando por conglomerado nem projetando vencimento):
  - dois CDBs de emissores diferentes do MESMO grupo devem consolidar sob o
    mesmo teto de R$250 mil e estourar (ESTOURO_ATUAL) mesmo que nenhum, sozinho,
    ultrapasse o limite;
  - instrumentos sem garantia do FGC (CRA/CRI/Tesouro/LIG/LF) são ignorados;
  - compatibilidade com o formato do parser da Posição Consolidada
    (chaves "tipo"/"valor"/"vencimento", em vez de "nome"/"saldo").
"""
import pytest

import api.index as idx


def test_conglomerado_explicito_agrega_emissores_diferentes_e_estoura():
    ativos = [
        {"nome": "CDB Banco BBC (Grupo Simpar) - JUN/2028", "valor": 150_000.0},
        {"nome": "CDB Simpar Financeira (Grupo Simpar) - JUN/2029", "valor": 150_000.0},
    ]
    r = idx.calcular_exposicao_fgc(ativos)

    assert len(r["por_conglomerado"]) == 1  # os 2 emissores viram 1 conglomerado
    g = r["por_conglomerado"][0]
    assert g["conglomerado"] == "GRUPO SIMPAR"
    assert g["exposicao_atual"] == pytest.approx(300_000.0, abs=0.01)
    assert g["status"] == "ESTOURO_ATUAL"  # 300k > teto de 250k/conglomerado
    assert g["excesso_atual"] == pytest.approx(50_000.0, abs=0.01)


def test_emissor_unico_dentro_do_limite_fica_ok():
    ativos = [{"nome": "CDB Banco XP - JUN/2027", "valor": 100_000.0}]
    r = idx.calcular_exposicao_fgc(ativos)
    g = r["por_conglomerado"][0]
    assert g["status"] == "OK"
    assert g["excesso_atual"] == 0.0


@pytest.mark.parametrize("nome", [
    "CRA Raizen - JUN/2028",
    "NTN-B - AGO/2035",
    "LIG Banco Itau - JUN/2030",   # patrimônio de afetação, não FGC
    "LF Banco Bradesco - JUN/2030",  # Letra Financeira, sem cobertura FGC
])
def test_instrumentos_sem_fgc_sao_excluidos(nome):
    r = idx.calcular_exposicao_fgc([{"nome": nome, "valor": 500_000.0}])
    assert r["por_conglomerado"] == []
    assert r["exposicao_total_fgc"] == 0.0


def test_sem_dados_de_vencimento_ou_taxa_nao_inventa_projecao():
    ativos = [{"nome": "CDB Banco Original - JUN/2027", "valor": 100_000.0}]
    r = idx.calcular_exposicao_fgc(ativos)
    g = r["por_conglomerado"][0]
    assert g["projecao_confiavel"] is False
    assert g["exposicao_projetada"] == g["exposicao_atual"]


def test_formato_posicao_consolidada_tipo_valor_vencimento():
    """Compatibilidade com o parser da Posição Consolidada: chaves
    'tipo'/'valor'/'vencimento' (em vez de 'nome'/'saldo' do XPerformance)."""
    ativos = [
        {"tipo": "CDB", "nome": "CDB BANCO SOFISA - JUN/2027",
         "valor": 260_000.0, "vencimento": "25/06/2027"},
    ]
    r = idx.calcular_exposicao_fgc(ativos)
    assert r["por_conglomerado"][0]["status"] == "ESTOURO_ATUAL"
    assert r["por_conglomerado"][0]["exposicao_atual"] == pytest.approx(260_000.0, abs=0.01)
