"""
Cruzamento "aporte real x aporte necessário": diagnosticar_aporte compara o
aporte REAL do cliente (movimentações do XPerformance, resumo dos últimos 12M)
com o aporte NECESSÁRIO do Planejamento Financeiro. Nenhum dos dois relatórios
mostra essa divergência sozinho — o Planejamento não sabe o que aconteceu na
conta, o XPerformance não sabe que existe uma meta por trás do número.

Também cobre a extração da tabela de movimentações mensais e do resumo
MÊS/ANO/12M/24M dentro de extrair_xperformance (_parse_movimentacoes_mensais /
_parse_resumo_periodo), que diagnosticar_aporte consome.
"""
import io

import pytest
from reportlab.pdfgen import canvas

import api.index as idx


def _fake_pdf(linhas):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(700, 50 + 14 * len(linhas)))
    y = 40 + 14 * len(linhas)
    for l in linhas:
        c.drawString(30, y, l)
        y -= 14
    c.showPage()
    c.save()
    return buf.getvalue()


# ── diagnosticar_aporte: puro, sem PDF ────────────────────────────────────────

def _xp(mov_12m):
    return {"resumo_periodo": {"12m": {"movimentacoes": mov_12m}}}


def _plano(aporte_atual, consumo=None, preservacao=None):
    return {"diagnostico": {"aporte_necessario_mensal": {
        "atual": aporte_atual, "consumo": consumo, "preservacao": preservacao}}}


def test_retirada_liquida_e_critico():
    r = idx.diagnosticar_aporte(_xp(-13_431.52), _plano(9_239.73, 10_080.58, 17_774.49))
    assert r["status"] == "critico"
    assert r["real_mensal_12m"] == pytest.approx(-1_119.29, abs=0.01)
    assert r["divergencia_mensal"] < 0


def test_aporte_positivo_mas_abaixo_do_necessario():
    r = idx.diagnosticar_aporte(_xp(3_000.0), _plano(9_239.73))  # 250/mês < 9.239,73
    assert r["status"] == "abaixo_do_necessario"


def test_aporte_dentro_ou_acima_do_necessario_fica_ok():
    r = idx.diagnosticar_aporte(_xp(120_000.0), _plano(9_239.73))  # 10.000/mês >= necessário
    assert r["status"] == "ok"


@pytest.mark.parametrize("xp_parsed,planejamento", [
    (None, _plano(9_239.73)),
    (_xp(None), _plano(9_239.73)),
    (_xp(-1_000.0), None),
    (_xp(-1_000.0), {"diagnostico": {}}),
])
def test_sem_dado_suficiente_retorna_none_nunca_inventa(xp_parsed, planejamento):
    assert idx.diagnosticar_aporte(xp_parsed, planejamento) is None


def test_gerar_diagnosticos_sem_planejamento_nao_quebra_e_nao_gera_alerta():
    xp_parsed = {"rf_ativos": [], "acoes": [], "fiis": [], "comp": {},
                 "resumo_periodo": {"12m": {"movimentacoes": -1_000.0}}}
    diag = idx.gerar_diagnosticos(xp_parsed)  # planejamento omitido (default None)
    assert diag["aporte_diagnostico"] is None
    assert not any(a["tipo"] == "aporte_divergente" for a in diag["alertas"])


def test_gerar_diagnosticos_com_planejamento_gera_alerta_critico():
    xp_parsed = {"rf_ativos": [], "acoes": [], "fiis": [], "comp": {},
                 "resumo_periodo": {"12m": {"movimentacoes": -13_431.52}}}
    planejamento = _plano(9_239.73, 10_080.58, 17_774.49)
    diag = idx.gerar_diagnosticos(xp_parsed, planejamento=planejamento)
    assert diag["aporte_diagnostico"]["status"] == "critico"
    alerta = next(a for a in diag["alertas"] if a["tipo"] == "aporte_divergente")
    assert alerta["nivel"] == "alto"


# ── extrair_xperformance: movimentações mensais + resumo (via PDF sintético) ──

LINHAS_XP = [
    "Conta Assessor Data",
    "123456 Fulano de Tal 01/07/2026",
    "TOTAL BRUTO",
    "R$ 100.000,00",
    "Referencias (%)",
    "Portfolio 1,00% 10,00% 15,00% 20,00%",
    "CDI 1,00% 10,00% 15,00% 20,00%",
    "Pos Fixado (100,00%)",
    "RESUMO DE INFORMAÇÕES DA CARTEIRA",
    "MÊS R$ 500,00 0,50% 100,00% -R$ 200,00",
    "ANO R$ 3.000,00 3,00% 90,00% -R$ 5.000,00",
    "12M R$ 6.000,00 6,00% 85,00% -R$ 8.000,00",
    "24M R$ 12.000,00 12,00% 92,00% -R$ 3.000,00",
    "jun./26 R$ 99.500,00 -R$ 200,00 -R$ 10,00 R$ 0,00 R$ 100.000,00 R$ 710,00 0,71% 110,00%",
    "mai./26 R$ 99.000,00 R$ 300,00 R$ 0,00 R$ 0,00 R$ 99.500,00 R$ 200,00 0,20% 50,00%",
]


@pytest.fixture(scope="module")
def xp_resultado():
    return idx.extrair_xperformance(_fake_pdf(LINHAS_XP))


def test_movimentacoes_mensais_ordem_cronologica_e_sinal(xp_resultado):
    movs = xp_resultado["movimentacoes_mensais"]
    assert [m["mes"] for m in movs] == ["mai", "jun"]  # mais antigo primeiro
    jun = movs[1]
    assert jun["ano"] == 2026
    assert jun["movimentacoes"] == pytest.approx(-200.0)
    assert jun["patrimonio_final"] == pytest.approx(100_000.0)


def test_resumo_periodo_agregados(xp_resultado):
    resumo = xp_resultado["resumo_periodo"]
    assert resumo["12m"]["movimentacoes"] == pytest.approx(-8_000.0)
    assert resumo["24m"]["movimentacoes"] == pytest.approx(-3_000.0)
    assert resumo["ano"]["ganho_financeiro"] == pytest.approx(3_000.0)


def test_diagnosticar_aporte_com_dados_reais_do_xperformance(xp_resultado):
    planejamento = _plano(500.0)  # necessário: 500/mês; real 12M: -8.000/12 = -666,67/mês
    r = idx.diagnosticar_aporte(xp_resultado, planejamento)
    assert r["status"] == "critico"
    assert r["real_mensal_12m"] == pytest.approx(-666.67, abs=0.01)
