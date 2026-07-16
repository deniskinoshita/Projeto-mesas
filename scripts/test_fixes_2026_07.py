"""
test_fixes_2026_07.py
Testes isolados (sem subir o Flask) para as 3 correções pedidas em jul/2026:
  1) soma (não max) na composição do XPerformance (extrair_xperformance)
  2) FGC unificado por conglomerado (calcular_exposicao_fgc)
  3) tributacao.json aplicado na prateleira de RF (_sug_rf / _liquido_pct_cdi_equivalente)

Uso:
    python scripts/test_fixes_2026_07.py
"""
import io
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.pdfgen import canvas

import api.index as idx


def _fake_pdf(linhas):
    """Gera um PDF simples com uma linha de texto por linha (uma por posição vertical)."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(600, 50 + 14 * len(linhas)))
    y = 40 + 14 * len(linhas)
    for l in linhas:
        c.drawString(30, y, l)
        y -= 14
    c.showPage()
    c.save()
    return buf.getvalue()


def teste_1_soma_composicao():
    print("\n=== Teste 1: soma (não max) na composição do XPerformance ===")
    linhas = [
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
    pdf_bytes = _fake_pdf(linhas)
    r = idx.extrair_xperformance(pdf_bytes)
    comp = r["comp"]
    print("comp:", comp)
    print("caixa:", r["caixa"])

    # pos_fixado deve ser a SOMA de "Pos Fixado" (50) + "Previdencia" (10) = 60
    assert abs(comp["pos_fixado"] - 60.0) < 0.01, f"esperado 60, veio {comp['pos_fixado']}"
    # alternativos deve ser a SOMA de "Alternativo" (5) + "Fundos Estruturados" (3) = 8
    assert abs(comp["alternativos"] - 8.0) < 0.01, f"esperado 8, veio {comp['alternativos']}"
    assert abs(comp["inflacao"] - 20.0) < 0.01
    assert abs(comp["acoes"] - 7.0) < 0.01

    total = sum(comp.values()) + r["caixa"]
    print("soma comp + caixa:", total)
    assert abs(total - 100.0) < 0.5, f"composição deveria somar ~100%, deu {total}"
    print("OK — soma composição bate com o esperado (bug do max() corrigido).")


def teste_2_fgc_conglomerado():
    print("\n=== Teste 2: FGC agrupado por conglomerado + tetos ===")

    # 2a) Dois emissores DIFERENTES anotados como o mesmo grupo devem ser somados
    #     e estourar o teto de 250k mesmo que nenhum sozinho ultrapasse.
    ativos_grupo = [
        {"nome": "CDB Banco BBC (Grupo Simpar) - JUN/2028", "valor": 150000.0},
        {"nome": "CDB Simpar Financeira (Grupo Simpar) - JUN/2029", "valor": 150000.0},
    ]
    r = idx.calcular_exposicao_fgc(ativos_grupo)
    print(r["por_conglomerado"])
    assert len(r["por_conglomerado"]) == 1, "deveria consolidar os 2 emissores em 1 conglomerado"
    g = r["por_conglomerado"][0]
    assert g["conglomerado"] == "GRUPO SIMPAR"
    assert abs(g["exposicao_atual"] - 300000.0) < 0.01
    assert g["status"] == "ESTOURO_ATUAL", f"deveria estourar (300k > 250k), status={g['status']}"
    print("OK — grupo explícito no nome agrega emissores diferentes sob o mesmo teto.")

    # 2b) Emissor único, dentro do limite -> status OK, sem estouro.
    ativos_ok = [{"nome": "CDB Banco XP - JUN/2027", "valor": 100000.0}]
    r2 = idx.calcular_exposicao_fgc(ativos_ok)
    g2 = r2["por_conglomerado"][0]
    assert g2["status"] == "OK", f"não deveria estourar, status={g2['status']}"
    assert g2["excesso_atual"] == 0.0
    print("OK — dentro do limite não dispara estouro (sanidade).")

    # 2c) Instrumentos SEM FGC (CRA/CRI/Tesouro/LIG/LF) não devem entrar na exposição.
    ativos_sem_fgc = [
        {"nome": "CRA Raizen - JUN/2028", "valor": 500000.0},
        {"nome": "NTN-B - AGO/2035", "valor": 500000.0},
        {"nome": "LIG Banco Itau - JUN/2030", "valor": 500000.0},   # LIG: garantia por patrimônio de afetação, não FGC
        {"nome": "LF Banco Bradesco - JUN/2030", "valor": 500000.0},  # LF: sem cobertura FGC
    ]
    r3 = idx.calcular_exposicao_fgc(ativos_sem_fgc)
    assert r3["por_conglomerado"] == [], f"CRA/Tesouro/LIG/LF não têm FGC, não deveriam aparecer: {r3['por_conglomerado']}"
    assert r3["exposicao_total_fgc"] == 0.0
    print("OK — instrumentos sem FGC (CRA/Tesouro/LIG/LF) corretamente excluídos.")

    # 2d) Projeção: sem vencimento/taxa, projecao_confiavel deve ser False (não inventa).
    ativos_sem_dados = [{"nome": "CDB Banco Original - JUN/2027", "valor": 100000.0}]
    r4 = idx.calcular_exposicao_fgc(ativos_sem_dados)
    assert r4["por_conglomerado"][0]["projecao_confiavel"] is False
    assert r4["por_conglomerado"][0]["exposicao_projetada"] == r4["por_conglomerado"][0]["exposicao_atual"]
    print("OK — sem dado de taxa/vencimento, projeção não inventa (cai no valor atual).")

    # 2e) Compatibilidade com o parser da Posição Consolidada: campo "tipo" já
    #     estruturado, valor via "valor" (não "saldo").
    ativos_posicao_consolidada = [
        {"tipo": "CDB", "nome": "CDB BANCO SOFISA - JUN/2027", "valor": 260000.0, "vencimento": "25/06/2027"},
    ]
    r5 = idx.calcular_exposicao_fgc(ativos_posicao_consolidada)
    assert r5["por_conglomerado"][0]["status"] == "ESTOURO_ATUAL"
    print("OK — formato da Posição Consolidada (tipo/valor/vencimento) funciona igual.")


def teste_3_tributacao_liquida():
    print("\n=== Teste 3: tributacao.json na prateleira de RF (líquido vs bruto) ===")

    # IR regressivo por prazo
    assert idx._ir_aliquota_regressiva(30) == 0.225
    assert idx._ir_aliquota_regressiva(200) == 0.20
    assert idx._ir_aliquota_regressiva(500) == 0.175
    assert idx._ir_aliquota_regressiva(1000) == 0.15
    print("OK — alíquota regressiva bate com tributacao.json (22,5/20/17,5/15%).")

    # Isento: líquido == bruto (já não tem IR)
    p_isento = {"isento": True, "tax_max": "93,50% CDI"}
    liq_isento = idx._liquido_pct_cdi_equivalente(p_isento)
    assert abs(liq_isento - 93.5) < 0.01
    print(f"OK — isento líquido = {liq_isento}% CDI (igual ao bruto).")

    # Tributável curto prazo: desconta 22,5% de IR
    p_curto = {"isento": False, "tax_max": "120,00% CDI", "carencia": 90}
    liq_curto = idx._liquido_pct_cdi_equivalente(p_curto)
    esperado_curto = 120.0 * (1 - 0.225)
    assert abs(liq_curto - esperado_curto) < 0.01, f"esperado {esperado_curto}, veio {liq_curto}"
    print(f"OK — tributável curto prazo líquido = {liq_curto:.2f}% CDI (bruto 120% - IR 22,5%).")

    # Cenário que expõe o bug antigo: isento de 90% CDI vs tributável de 130% CDI
    # em prazo curto (22,5% IR). Bruto->bruto o tributável parece melhor (130 > 90);
    # a comparação antiga ("isento sempre primeiro") ignorava isso. Pelo líquido:
    # tributável = 130*(1-0.225) = 100,75% CDI > 90% CDI isento -> tributável DEVE ranquear na frente.
    produtos = [
        {"ativo": "LCA Isenta 90", "isento": True, "tax_max": "90,00% CDI", "risco": 5, "publico": "Investidor Geral"},
        {"ativo": "CDB Tributavel 130", "isento": False, "tax_max": "130,00% CDI", "carencia": 90, "risco": 5, "publico": "Investidor Geral"},
    ]

    def _sort_key(p):
        liq = idx._liquido_pct_cdi_equivalente(p)
        risco_n = float(p.get("risco")) if isinstance(p.get("risco"), (int, float)) else 99.0
        if liq is not None:
            return (0, -liq, risco_n)
        return (1, not p.get("isento"), risco_n)

    ordenado = sorted(produtos, key=_sort_key)
    print("ordem:", [p["ativo"] for p in ordenado])
    assert ordenado[0]["ativo"] == "CDB Tributavel 130", (
        "pelo líquido, o tributável de 130% CDI (líquido ~100,75%) deveria vir "
        "antes do isento de 90% CDI — a ordenação antiga (isento sempre primeiro) erraria aqui."
    )
    print("OK — ranking por líquido corrige o caso em que 'isento primeiro' erraria.")


if __name__ == "__main__":
    teste_1_soma_composicao()
    teste_2_fgc_conglomerado()
    teste_3_tributacao_liquida()
    print("\nTodos os testes passaram.")
