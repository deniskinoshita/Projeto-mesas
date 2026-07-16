"""
extrair_xperformance — soma (não max) de linhas duplicadas na composição.

Bug original: quando o XPerformance tem duas linhas de percentual que mapeiam
para a MESMA categoria interna (ex.: "Pós Fixado" + "Previdência" -> pos_fixado;
"Alternativo" + "Fundos Estruturados" -> alternativos), o parser usava max()
e descartava uma das duas parcelas, subestimando a classe. A correção soma as
parcelas. Este teste gera um PDF sintético (via reportlab) reproduzindo esse
cenário e confere a soma exata por classe.
"""
import io

import pytest
from reportlab.pdfgen import canvas

import api.index as idx


def _fake_pdf(linhas):
    """PDF simples com uma linha de texto por posição vertical."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(600, 50 + 14 * len(linhas)))
    y = 40 + 14 * len(linhas)
    for l in linhas:
        c.drawString(30, y, l)
        y -= 14
    c.showPage()
    c.save()
    return buf.getvalue()


LINHAS_BASE = [
    "Conta Assessor Data",
    "123456 Fulano de Tal 01/07/2026",
    "TOTAL BRUTO",
    "R$ 1.000.000,00",
    "Referencias (%)",
    "Portfolio 1,00% 10,00% 15,00% 20,00%",
    "CDI 1,00% 10,00% 15,00% 20,00%",
    "Pos Fixado (50,00%)",
    "Previdencia (10,00%)",
    "Inflacao (20,00%)",
    "Alternativo (5,00%)",
    "Fundos Estruturados (3,00%)",
    "Renda Variavel Brasil (7,00%)",
    "Caixa (5,00%)",
]


@pytest.fixture(scope="module")
def resultado():
    return idx.extrair_xperformance(_fake_pdf(LINHAS_BASE))


def test_pos_fixado_soma_pos_fixado_mais_previdencia(resultado):
    # 50% (Pós Fixado) + 10% (Previdência) = 60% — não max(50, 10) = 50.
    assert resultado["comp"]["pos_fixado"] == pytest.approx(60.0, abs=0.01)


def test_alternativos_soma_alternativo_mais_fundos_estruturados(resultado):
    # 5% (Alternativo) + 3% (Fundos Estruturados) = 8% — não max(5, 3) = 5.
    assert resultado["comp"]["alternativos"] == pytest.approx(8.0, abs=0.01)


def test_categorias_sem_duplicidade_mantem_valor_unico(resultado):
    assert resultado["comp"]["inflacao"] == pytest.approx(20.0, abs=0.01)
    assert resultado["comp"]["acoes"] == pytest.approx(7.0, abs=0.01)


def test_composicao_mais_caixa_soma_100_por_cento(resultado):
    total = sum(resultado["comp"].values()) + resultado["caixa"]
    assert total == pytest.approx(100.0, abs=0.5)


def test_metadados_de_cabecalho(resultado):
    assert resultado["conta"] == "123456"
    assert resultado["data_ref"] == "01/07/2026"
    assert resultado["patrimonio"] == pytest.approx(1_000_000.0, abs=0.01)
