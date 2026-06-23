"""
Simula log de atividade para o painel admin (admin/dashboard).
"""
import sys, os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
from index import _load, _save, _ADMIN_ACTIVITY_FILE

ASSESSORES = [
    "Alex Alves dos Santos", "Andre Guilherme Leite Figueiredo", "Bruno Seiji Ito",
    "Carlos Fernando Victor Bolivar Moreira Neto", "Carolina Custodio Siqueira",
    "Denis Albertino dos Santos Kinoshita", "Felipe Fraga", "Felipe Santos Nishio",
    "Giuseppe Hilario Neto", "Lucas Landroni Cozzi", "Marcelo Ramos Dias",
    "Matheus Escoza Milani", "Michael Ademilson Santos da Silva",
    "Paulo Roberto Negreiros Sobrinho", "Tatiane Cristina da Silva Cecchetti",
    "Thiago Brunelli Borba",
]

hoje = datetime.now()
log = _load(_ADMIN_ACTIVITY_FILE, [])

# Remove simulados anteriores
log = [e for e in log if not e.get("simulado")]

acoes = [
    ("analisou-carteira", "Analisou carteira de cliente"),
    ("acesso", "Abriu pagina do assessor"),
    ("pptx_gerado", "Gerou apresentacao PPTX"),
    ("acesso", "Abriu pagina do assessor"),
    ("analisou-carteira", "Analisou carteira de cliente"),
]

nomes_clientes = [
    "Roberto Almeida da Silva", "Maria Fernanda Costa", "Joao Paulo Machado",
    "Ana Carolina Ferreira", "Carlos Eduardo Santos", "Luciana Oliveira Mendes",
    "Pedro Henrique Lima", "Gabriela Rodrigues", "Fernando Souza Neto",
    "Patricia Vieira Gomes", "Andre Luis Martins", "Camila Pereira",
    "Ricardo Teixeira Borges", "Juliana Nascimento", "Marcio Cavalcanti",
    "Beatriz Alves Moreira",
]

for i, nome_ass in enumerate(ASSESSORES):
    for j, (acao, detalhe) in enumerate(acoes):
        ts = (hoje - timedelta(hours=i*3+j)).strftime("%d/%m/%Y %H:%M")
        entry = {
            "role": "assessor",
            "nome": nome_ass,
            "acao": acao,
            "detalhe": detalhe if "cliente" not in detalhe else f"Analisou carteira de {nomes_clientes[i]}",
            "ts": ts,
            "simulado": True,
        }
        log.insert(0, entry)

# Lideres
for nome_lid in ["Denis Kinoshita", "Felipe Nishio"]:
    for j in range(3):
        ts = (hoje - timedelta(hours=j*8)).strftime("%d/%m/%Y %H:%M")
        log.insert(0, {
            "role": "lider",
            "nome": nome_lid,
            "acao": "acesso",
            "detalhe": "Abriu a pagina do Lider",
            "ts": ts,
            "simulado": True,
        })

_save(_ADMIN_ACTIVITY_FILE, log[:500])
print(f"OK: {len([e for e in log if e.get('simulado')])} entradas de atividade simuladas salvas!")
