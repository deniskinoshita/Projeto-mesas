"""
parse_planejamento_financeiro — terceiro tipo de relatório de cliente (além do
XPerformance e da Posição Consolidada): objetivos, capacidade de aporte e os 3
cenários de projeção patrimonial (atual/consumo/preservação do patrimônio).

O layout testado aqui reproduz o que o pdfplumber extrai do PDF real da XP:
"rótulo valor" colado na mesma linha nas Premissas, mas cada estatística do
bloco de Diagnóstico (3 cenários lado a lado no PDF) vira uma linha de
cabeçalho seguida de uma linha só com os 3 valores.
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


LINHAS = [
    "Conta",
    "999999",
    "Assessor:",
    "Fulano de Tal",
    "Data de Referência:",
    "01/07/2026",
    "Nome Fulano F.",
    "Idade atual 45",
    "Estado Civil Casado(a)",
    "Filhos 2",
    "Expectativa de Vida 95 anos",
    "Política de Investimentos Estrategista",
    "Renda Média Anual / Mensal R$ 120.000,00 / R$ 10.000,00",
    "Despesa Média Anual / Mensal R$ 84.000,00 / R$ 7.000,00",
    "Investimento Inicial Nacional (R$) R$ 200.000,00",
    "Tabela 1: Objetivos",
    "DESCRIÇÃO CATEGORIA IDADE ATINGIMENTO FREQUÊNCIA OCORRÊNCIAS VALOR",
    "Aposentadoria Aposentadoria 65 Mensal 300 R$ 5.000,00/mês",
    "Receita Mensal Outros Fulano R$ 9.000,00 Mensal 01/24 - 01/41 200",
    "Despesa Mensal Outros Fulano R$ 6.500,00 Mensal 01/24 - 01/41 200",
    "CAPACIDADE DE APORTE",
    "APORTE MÉDIO MENSAL APORTE MÉDIO ANUAL",
    "R$2.500,00 R$30.000,00",
    "Tabela 4: Fluxo Financeiro",
    "IDADE ENTRADAS SAÍDAS CAPACIDADE DE APORTE",
    "45 R$ 100.000,00 R$ 80.000,00 R$ 20.000,00",
    "46 R$ 105.000,00 R$ 82.000,00 R$ 23.000,00",
    "BENS MÓVEIS R$ 50.000,00",
    "BENS IMÓVEIS R$ 300.000,00",
    "FGTS R$ 10.000,00",
    "Tabela 6: Projeção Financeira",
    "IDADE PROJEÇÃO ATUAL CONSUMO DO PATRIMÔNIO PRESERVAÇÃO DO PATRIMÔNIO",
    "45 R$ 210.000,00 R$ 215.000,00 R$ 220.000,00",
    "46 R$ 230.000,00 R$ 236.000,00 R$ 245.000,00",
    "Patrimônio projetado aos 65 anos Patrimônio mínimo aos 65 anos Patrimônio necessário aos 65 anos",
    "R$ 1.500.000,00 R$ 1.600.000,00 R$ 2.400.000,00",
    "Capacidade de aporte médio mensal/anual Aporte médio mensal/anual Aporte médio mensal/anual",
    "R$ 2.500,00 / R$ 30.000,00 R$ 2.800,00 / R$ 33.600,00 R$ 4.500,00 / R$ 54.000,00",
]


@pytest.fixture(scope="module")
def resultado():
    return idx.parse_planejamento_financeiro(_fake_pdf(LINHAS))


def test_identificacao_e_premissas(resultado):
    assert resultado["conta"] == "999999"
    assert resultado["assessor"] == "Fulano de Tal"
    assert resultado["data_ref"] == "01/07/2026"
    assert resultado["idade_atual"] == 45
    assert resultado["expectativa_vida"] == 95
    assert resultado["politica_investimentos"] == "Estrategista"
    assert resultado["qtd_filhos"] == 2


def test_renda_despesa_media_e_declarada(resultado):
    assert resultado["renda_media_mensal"] == pytest.approx(10_000.0)
    assert resultado["despesa_media_mensal"] == pytest.approx(7_000.0)
    # valor declarado na entrevista (Tabela 2/3) é distinto da média projetada
    assert resultado["receita_atual_mensal"] == pytest.approx(9_000.0)
    assert resultado["despesa_atual_mensal"] == pytest.approx(6_500.0)


def test_capacidade_de_aporte(resultado):
    assert resultado["capacidade_aporte_mensal"] == pytest.approx(2_500.0)
    assert resultado["capacidade_aporte_anual"] == pytest.approx(30_000.0)


def test_objetivos(resultado):
    assert len(resultado["objetivos"]) == 1
    obj = resultado["objetivos"][0]
    assert obj["idade_atingimento"] == 65
    assert obj["frequencia"] == "Mensal"
    assert obj["ocorrencias"] == 300
    assert obj["valor"] == pytest.approx(5_000.0)


def test_outros_bens(resultado):
    assert resultado["outros_bens"]["Bens Móveis"] == pytest.approx(50_000.0)
    assert resultado["outros_bens"]["Bens Imóveis"] == pytest.approx(300_000.0)
    assert resultado["outros_bens"]["Fgts"] == pytest.approx(10_000.0)


def test_fluxo_financeiro_tabela_4(resultado):
    assert resultado["fluxo_financeiro"] == [
        {"idade": 45, "entradas": 100_000.0, "saidas": 80_000.0, "capacidade_aporte": 20_000.0},
        {"idade": 46, "entradas": 105_000.0, "saidas": 82_000.0, "capacidade_aporte": 23_000.0},
    ]


def test_projecao_tabela_6_nao_se_mistura_com_fluxo(resultado):
    # Mesma forma de linha (idade + 3 R$) que a Tabela 4 — precisa cair na lista certa.
    assert resultado["projecao"] == [
        {"idade": 45, "atual": 210_000.0, "consumo": 215_000.0, "preservacao": 220_000.0},
        {"idade": 46, "atual": 230_000.0, "consumo": 236_000.0, "preservacao": 245_000.0},
    ]


def test_diagnostico_3_cenarios(resultado):
    diag = resultado["diagnostico"]
    assert diag["idade_alvo"] == 65
    assert diag["patrimonio_alvo"] == {
        "atual": pytest.approx(1_500_000.0), "consumo": pytest.approx(1_600_000.0), "preservacao": pytest.approx(2_400_000.0),
    }
    assert diag["aporte_necessario_mensal"] == {
        "atual": pytest.approx(2_500.0), "consumo": pytest.approx(2_800.0), "preservacao": pytest.approx(4_500.0),
    }
    assert diag["aporte_necessario_anual"] == {
        "atual": pytest.approx(30_000.0), "consumo": pytest.approx(33_600.0), "preservacao": pytest.approx(54_000.0),
    }


def test_pdf_ilegivel_nao_quebra():
    r = idx.parse_planejamento_financeiro(b"not a pdf")
    assert r["fonte"] == "planejamento_financeiro"
    assert "erro" in r
