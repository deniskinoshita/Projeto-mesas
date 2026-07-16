"""
Configuração compartilhada da suíte pytest do Projeto-mesas.

Responsabilidades:
  1) Garantir que `import api.index` funcione a partir de tests/ (adiciona a
     raiz do projeto no sys.path).
  2) Isolar TODO teste de serviços externos reais (Redis/Upstash, Anthropic).
     api/index.py só conecta nesses serviços se as env vars correspondentes
     estiverem definidas — aqui garantimos que elas NUNCA vazam do shell do
     desenvolvedor (ex.: depois de um `vercel env pull`) para dentro da suíte,
     e resetamos o cache-singleton do cliente KV entre testes.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest

# Import único do módulo gigante (api/index.py, ~20k linhas). Nada aqui abre
# conexão de verdade: Flask app é só instanciado, Redis/Anthropic são lazy
# (só conectam dentro de _kv_client()/blocos que checam a env var na hora do uso).
import api.index as idx  # noqa: E402


@pytest.fixture(autouse=True)
def _isolar_servicos_externos(monkeypatch):
    """Roda em TODO teste: remove credenciais reais do ambiente e zera o
    singleton do cliente KV, para nenhum teste bater em Redis/Anthropic de
    verdade nem vazar estado (cache) de um teste para o outro."""
    for var in ("KV_REST_API_URL", "KV_REST_API_TOKEN", "ANTHROPIC_API_KEY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(idx, "_KV_CLIENT_CACHE", None, raising=False)
    monkeypatch.setattr(idx, "_KV_CLIENT_TRIED", False, raising=False)
    yield


@pytest.fixture
def app():
    idx.app.testing = True
    return idx.app


@pytest.fixture
def client(app):
    return app.test_client()
