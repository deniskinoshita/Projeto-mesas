"""
avaliar_oportunidades_planejamento — cruza idade, objetivos e composição
familiar do Planejamento Financeiro (idade, filhos, estado civil, objetivos)
com a posição atual para gerar oportunidades de Cross Sell PERSONALIZADAS
(previdência, seguro de vida) em vez do pitch genérico do CROSS_SELL, e lista
de onde pode vir o recurso para bancar essas alocações.

Regra de ouro do módulo: nunca afirma que o cliente NÃO tem seguro/previdência
em outra instituição (o app só enxerga a XP) — sempre como necessidade/gap
PROVÁVEL, nunca como fato.
"""
import pytest

import api.index as idx


def _plano(idade=50, filhos=0, estado_civil="Solteiro(a)", renda_anual=500_000.0,
           aporte_mensal=9_000.0, objetivos=None):
    return {
        "idade_atual": idade, "qtd_filhos": filhos, "estado_civil": estado_civil,
        "renda_media_anual": renda_anual, "capacidade_aporte_mensal": aporte_mensal,
        "objetivos": objetivos if objetivos is not None else [
            {"label": "Aposentadoria", "idade_atingimento": idade + 15}],
    }


def test_sem_idade_retorna_vazio_nunca_inventa():
    assert idx.avaliar_oportunidades_planejamento({}, None) == {}
    assert idx.avaliar_oportunidades_planejamento(None, None) == {}


# ── Previdência ────────────────────────────────────────────────────────────

def test_previdencia_gap_confirmado_quando_posicao_sem_previdencia():
    posicao = {"fundos": [{"classe": "Fundos RF", "valor": 10_000.0}]}
    r = idx.avaliar_oportunidades_planejamento(_plano(idade=50), posicao)
    prev = r["previdencia"]
    assert prev["gap_confirmado"] is True
    assert prev["anos_ate_aposentadoria"] == 15
    assert prev["tabela_recomendada"] == "regressiva"  # >=10 anos
    assert prev["teto_pgbl_anual"] == pytest.approx(60_000.0)  # 12% de 500k
    assert prev["aporte_mensal_sugerido"] == pytest.approx(9_000.0)


def test_previdencia_nao_e_gap_quando_ja_tem_alocacao():
    posicao = {"fundos": [{"classe": "Previdência", "valor": 50_000.0}]}
    r = idx.avaliar_oportunidades_planejamento(_plano(), posicao)
    assert "previdencia" not in r


def test_previdencia_sem_posicao_fica_como_hipotese_nao_confirmada():
    r = idx.avaliar_oportunidades_planejamento(_plano(), posicao=None)
    assert r["previdencia"]["gap_confirmado"] is False


def test_previdencia_prazo_curto_recomenda_tabela_progressiva():
    r = idx.avaliar_oportunidades_planejamento(
        _plano(idade=60, objetivos=[{"label": "Aposentadoria", "idade_atingimento": 65}]))
    assert r["previdencia"]["anos_ate_aposentadoria"] == 5
    assert r["previdencia"]["tabela_recomendada"] == "progressiva"


def test_previdencia_sem_objetivo_de_aposentadoria_fica_sem_prazo():
    r = idx.avaliar_oportunidades_planejamento(
        _plano(objetivos=[{"label": "Comprar uma casa", "idade_atingimento": 55}]))
    assert r["previdencia"]["anos_ate_aposentadoria"] is None
    assert r["previdencia"]["tabela_recomendada"] == "progressiva"  # None não é >=10


# ── Seguro de vida ───────────────────────────────────────────────────────────

def test_seguro_vida_necessidade_provavel_com_filhos():
    r = idx.avaliar_oportunidades_planejamento(_plano(filhos=2, estado_civil="Solteiro(a)"))
    seg = r["seguro_vida"]
    assert seg["necessidade_provavel"] is True
    assert seg["motivo"] == "filhos"
    assert seg["capital_sugerido_10x_renda"] == pytest.approx(5_000_000.0)
    assert seg["capital_sugerido_5x_renda"] == pytest.approx(2_500_000.0)


def test_seguro_vida_necessidade_provavel_por_estado_civil_sem_filhos():
    r = idx.avaliar_oportunidades_planejamento(_plano(filhos=0, estado_civil="Casado(a)"))
    assert r["seguro_vida"]["necessidade_provavel"] is True
    assert r["seguro_vida"]["motivo"] == "estado_civil"


def test_seguro_vida_sem_dependente_provavel_nao_e_urgente_mas_ainda_aparece():
    r = idx.avaliar_oportunidades_planejamento(_plano(filhos=0, estado_civil="Solteiro(a)"))
    seg = r["seguro_vida"]
    assert seg["necessidade_provavel"] is False
    assert seg["motivo"] is None
    # capital ainda é calculado, só a prioridade muda (decisão fica com o assessor)
    assert seg["capital_sugerido_10x_renda"] > 0


def test_seguro_vida_nunca_afirma_que_cliente_nao_tem_seguro():
    r = idx.avaliar_oportunidades_planejamento(_plano())
    # A chave é sempre sobre "necessidade provável", nunca sobre posse real do seguro
    assert "tem_seguro" not in r["seguro_vida"]
    assert "nao_tem_seguro" not in r["seguro_vida"]


# ── Fontes de recurso ────────────────────────────────────────────────────────

def test_fontes_de_recurso_combina_aporte_caixa_e_vencimentos():
    posicao = {"saldo_conta": 5_000.0, "resumo": {"venc_90d": 20_000.0}}
    r = idx.avaliar_oportunidades_planejamento(_plano(aporte_mensal=3_000.0), posicao)
    fontes = {f["fonte"]: f for f in r["fontes_recurso"]}
    assert fontes["capacidade_aporte"]["valor_mensal"] == pytest.approx(3_000.0)
    assert fontes["caixa_parado"]["valor"] == pytest.approx(5_000.0)
    assert fontes["vencimentos_90d"]["valor"] == pytest.approx(20_000.0)


def test_caixa_pequeno_nao_vira_fonte_de_recurso():
    posicao = {"saldo_conta": 200.0}  # abaixo do piso de R$1.000
    r = idx.avaliar_oportunidades_planejamento(_plano(aporte_mensal=None), posicao)
    fontes = [f["fonte"] for f in r["fontes_recurso"]]
    assert "caixa_parado" not in fontes


def test_sem_posicao_fontes_de_recurso_so_tem_aporte():
    r = idx.avaliar_oportunidades_planejamento(_plano(aporte_mensal=1_500.0), posicao=None)
    assert [f["fonte"] for f in r["fontes_recurso"]] == ["capacidade_aporte"]
