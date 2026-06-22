"""
extrair_composicao.py
Extrai a composição por indexador do PDF de Relatório de Investimentos XP
e salva um JSON mapeado para as categorias do modelo Levante Asset.

Uso:
    python extrair_composicao.py <caminho_pdf> [--output <caminho_json>]
"""

import sys
import re
import json
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("Instale pdfplumber: pip install pdfplumber")
    sys.exit(1)


# Mapeamento de categorias XP → categorias do modelo
MAPEAMENTO = {
    # Pós-fixado
    "pós fixado": "pos_fixado",
    "pos fixado": "pos_fixado",
    "pós-fixado": "pos_fixado",
    "pos-fixado": "pos_fixado",
    "renda fixa pós": "pos_fixado",
    # Inflação
    "inflação": "inflacao",
    "inflacao": "inflacao",
    "renda fixa inflação": "inflacao",
    "ipca": "inflacao",
    # Pré-fixado
    "pré fixado": "pre_fixado",
    "pre fixado": "pre_fixado",
    "pré-fixado": "pre_fixado",
    "pre-fixado": "pre_fixado",
    "renda fixa pré": "pre_fixado",
    # Ações
    "ações": "acoes",
    "acoes": "acoes",
    "renda variável": "acoes",
    "renda variavel": "acoes",
    "rv brasil": "acoes",
    "renda variável brasil": "acoes",
    # FIIs
    "fiis": "fiis",
    "fii": "fiis",
    "fundos imobiliários": "fiis",
    "fundos imobiliarios": "fiis",
    # Multimercado
    "multimercado": "multimercado",
    "multi mercado": "multimercado",
    # Internacional
    "internacional": "internacional",
    "dólar": "internacional",
    "dolar": "internacional",
    "exterior": "internacional",
    "renda fixa global": "internacional",
    "rv exterior": "internacional",
    "renda variável exterior": "internacional",
    # Criptomoedas
    "criptomoedas": "criptomoedas",
    "cripto": "criptomoedas",
    "crypto": "criptomoedas",
    # Alternativos
    "alternativos": "alternativos",
    "alternativo": "alternativos",
    "outros": "alternativos",
    # Caixa (ignorado do modelo — registrado separado)
    "caixa": "caixa",
    "conta corrente": "caixa",
}

CATEGORIAS_MODELO = [
    "pos_fixado", "inflacao", "pre_fixado", "acoes",
    "fiis", "multimercado", "internacional", "alternativos", "criptomoedas"
]


def normalizar(texto: str) -> str:
    return texto.lower().strip()


def mapear_categoria(texto: str) -> str | None:
    t = normalizar(texto)
    for chave, valor in MAPEAMENTO.items():
        if chave in t:
            return valor
    return None


def extrair_percentuais_do_texto(texto: str) -> dict:
    """
    Tenta encontrar linhas no formato:
        Pós Fixado    R$ 150.000    75,00%
    ou
        Pós Fixado    75,00%
    e retorna {categoria_modelo: percentual_float}
    """
    composicao = {cat: 0.0 for cat in CATEGORIAS_MODELO}
    composicao["caixa"] = 0.0

    # Padrão: texto da categoria seguido (em algum ponto da linha) de XX,XX% ou XX.XX%
    padrao = re.compile(
        r"([A-Za-zÀ-ÿ\s\-\/]+?)\s+"   # nome da categoria
        r"(?:R\$[\s\d\.,]+\s+)?"        # valor financeiro opcional
        r"(\d{1,3}(?:[.,]\d{1,3})*(?:[.,]\d{1,2})?)\s*%",
        re.IGNORECASE
    )

    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        m = padrao.search(linha)
        if m:
            nome_raw = m.group(1).strip()
            perc_raw = m.group(2).replace(".", "").replace(",", ".")
            try:
                perc = float(perc_raw)
            except ValueError:
                continue
            categoria = mapear_categoria(nome_raw)
            if categoria and perc > 0:
                composicao[categoria] = composicao.get(categoria, 0.0) + perc

    return composicao


def normalizar_percentuais(composicao: dict) -> dict:
    """
    Remove o caixa do total e recalcula os % sobre o patrimônio investido.
    Caixa fica registrado mas não entra no modelo de comparação.
    """
    caixa = composicao.pop("caixa", 0.0)
    total = sum(composicao.values())

    if total == 0:
        return composicao, caixa

    if abs(total - 100.0) > 1.0:
        # Normaliza para 100% excluindo caixa
        fator = 100.0 / total
        composicao = {k: round(v * fator, 2) for k, v in composicao.items()}
    else:
        composicao = {k: round(v, 2) for k, v in composicao.items()}

    return composicao, caixa


def extrair_de_pdf(caminho_pdf: str) -> dict:
    texto_completo = ""
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto_completo += (pagina.extract_text() or "") + "\n"

    composicao_bruta = extrair_percentuais_do_texto(texto_completo)
    composicao, caixa = normalizar_percentuais(composicao_bruta)

    return {
        "composicao": composicao,
        "caixa_pct": round(caixa, 2),
        "fonte": Path(caminho_pdf).name,
        "aviso": (
            "Caixa excluído do cálculo de desvio. "
            "Percentuais normalizados sobre patrimônio alocado."
        )
    }


def main():
    parser = argparse.ArgumentParser(description="Extrai composição por indexador de PDF XP")
    parser.add_argument("pdf", help="Caminho para o PDF do relatório XP")
    parser.add_argument("--output", "-o", help="Caminho para salvar o JSON de saída")
    args = parser.parse_args()

    resultado = extrair_de_pdf(args.pdf)

    json_str = json.dumps(resultado, ensure_ascii=False, indent=2)
    print(json_str)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"\nSalvo em: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
