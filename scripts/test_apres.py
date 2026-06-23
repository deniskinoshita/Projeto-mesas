import sys, json
sys.path.insert(0,'api')
import index

payload = {
    "assessor": "Lucas Landroni Cozzi",
    "nome": "Lucia",
    "perfil": "arrojada",
    "objetivo": "renda",
    "conta": "327592",
    "patrimonio": 500000,
    "composicao": {"pos_fixado": 60, "inflacao": 20, "pre_fixado": 10, "acoes": 5, "fiis": 5},
    "ativos_detalhe": {},
    "rent": {"portfolio": {"mes": 0.5, "ano": 3.2, "12m": 8.1, "24m": 15.0}},
    "checklist": {},
    "cross_ativos": [],
    "recomendacoes": [],
    "desvios": []
}

with index.app.test_client() as c:
    r = c.post('/api/apresentacao',
               data=json.dumps(payload),
               content_type='application/json')
    print("Status:", r.status_code)
    if r.status_code != 200:
        print("Erro:", r.data.decode('utf-8', errors='replace')[:2000])
    else:
        print("PDF gerado! Bytes:", len(r.data))
