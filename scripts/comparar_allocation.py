"""
comparar_allocation.py
Compara a composição real do cliente com o modelo do perfil (Levante Asset)
e gera diagnóstico de fragilidades e oportunidades.

Uso:
    python comparar_allocation.py <composicao.json> <perfil> [--modelo <modelos_allocation.json>]
"""

import sys
import json
import argparse
from pathlib import Path

RAIZ = Path(__file__).parent.parent
MODELOS_DEFAULT = RAIZ / "modelos_allocation.json"

LABELS = {
    "pos_fixado": "Pós Fixado",
    "inflacao": "Inflação",
    "pre_fixado": "Pré Fixado",
    "acoes": "Ações",
    "fiis": "FIIs",
    "multimercado": "Multimercado",
    "internacional": "Internacional",
    "alternativos": "Alternativos",
    "criptomoedas": "Criptomoedas",
}

THRESHOLD_RELEVANTE = 1.5  # desvio em pp considerado relevante


def carregar_json(caminho):
    with open(caminho, encoding="utf-8") as f:
        return json.load(f)


def calcular_desvios(composicao_real: dict, modelo: dict) -> list[dict]:
    desvios = []
    for cat, label in LABELS.items():
        real = composicao_real.get(cat, 0.0)
        alvo = modelo.get(cat, 0.0)
        desvio = real - alvo
        desvios.append({
            "categoria": cat,
            "label": label,
            "real_pct": round(real, 2),
            "alvo_pct": round(alvo, 2),
            "desvio_pp": round(desvio, 2),
        })
    # Ordena por desvio absoluto decrescente
    desvios.sort(key=lambda x: abs(x["desvio_pp"]), reverse=True)
    return desvios


def diagnosticar(desvios: list[dict]) -> dict:
    fragilidades = []
    oportunidades = []

    for d in desvios:
        if abs(d["desvio_pp"]) < THRESHOLD_RELEVANTE:
            continue
        if d["desvio_pp"] < 0:
            fragilidades.append({
                **d,
                "mensagem": (
                    f"Subexposição em {d['label']}: "
                    f"{d['real_pct']:.1f}% vs. alvo {d['alvo_pct']:.1f}% "
                    f"(falta {abs(d['desvio_pp']):.1f} pp)"
                )
            })
        else:
            oportunidades.append({
                **d,
                "mensagem": (
                    f"Sobrealocação em {d['label']}: "
                    f"{d['real_pct']:.1f}% vs. alvo {d['alvo_pct']:.1f}% "
                    f"(excesso de {d['desvio_pp']:.1f} pp — candidato a realocação)"
                )
            })

    return {
        "fragilidades": fragilidades,
        "oportunidades_realocacao": oportunidades,
    }


def gerar_sugestoes(diagnostico: dict) -> list[str]:
    sugestoes = []
    origens = diagnostico["oportunidades_realocacao"]
    destinos = diagnostico["fragilidades"]

    if not origens or not destinos:
        return sugestoes

    for dest in destinos:
        para = dest["label"]
        falta = abs(dest["desvio_pp"])
        de_list = [o["label"] for o in origens]
        sugestoes.append(
            f"Realocar ~{falta:.1f} pp de {' e/ou '.join(de_list)} para {para}."
        )

    return sugestoes


def main():
    parser = argparse.ArgumentParser(description="Compara carteira do cliente com modelo de alocação")
    parser.add_argument("composicao", help="JSON de composição extraída (saída do extrair_composicao.py)")
    parser.add_argument("perfil", choices=["conservadora", "moderada", "arrojada", "agressiva"])
    parser.add_argument("--modelo", default=str(MODELOS_DEFAULT), help="Caminho para modelos_allocation.json")
    args = parser.parse_args()

    dados = carregar_json(args.composicao)
    composicao_real = dados.get("composicao", dados)

    modelos = carregar_json(args.modelo)
    modelo_perfil = modelos[args.perfil]

    desvios = calcular_desvios(composicao_real, modelo_perfil)
    diagnostico = diagnosticar(desvios)
    sugestoes = gerar_sugestoes(diagnostico)

    resultado = {
        "perfil": args.perfil,
        "desvios": desvios,
        "diagnostico": diagnostico,
        "sugestoes_movimentacao": sugestoes,
    }

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return resultado


if __name__ == "__main__":
    main()
