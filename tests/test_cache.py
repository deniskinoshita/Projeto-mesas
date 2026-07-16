"""
_kv_client() — singleton por processo/instância quente.

O cliente Redis (Upstash) é caro para recriar a cada chamada e as env vars não
mudam em runtime, então _kv_client() memoiza o resultado em duas globals do
módulo (_KV_CLIENT_CACHE/_KV_CLIENT_TRIED). Este teste confirma o singleton
SEM abrir conexão real: injeta um módulo `upstash_redis` falso em sys.modules
(mock mínimo necessário — só a classe Redis, que apenas registra quantas vezes
foi instanciada) e garante que uma segunda chamada reaproveita a mesma
instância em vez de reconectar.
"""
import sys
import types

import api.index as idx


def test_kv_client_retorna_mesma_instancia_em_chamadas_repetidas(monkeypatch):
    instanciacoes = []

    class FakeRedis:
        def __init__(self, url, token):
            instanciacoes.append((url, token))

    fake_mod = types.ModuleType("upstash_redis")
    fake_mod.Redis = FakeRedis
    monkeypatch.setitem(sys.modules, "upstash_redis", fake_mod)
    monkeypatch.setenv("KV_REST_API_URL", "https://fake-kv.example.com")
    monkeypatch.setenv("KV_REST_API_TOKEN", "fake-token")

    cliente_1 = idx._kv_client()
    cliente_2 = idx._kv_client()

    assert cliente_1 is not None
    assert cliente_1 is cliente_2  # singleton: mesma instância, não recriada
    assert len(instanciacoes) == 1  # Redis(...) só foi chamado uma vez


def test_kv_client_sem_credenciais_retorna_none_e_nao_tenta_importar(monkeypatch):
    # upstash_redis NÃO fica disponível neste teste (nem instalado no ambiente
    # de dev, propositalmente) — sem as env vars, _kv_client() nem tenta o
    # import, então nunca deveria estourar ImportError.
    cliente_1 = idx._kv_client()
    cliente_2 = idx._kv_client()
    assert cliente_1 is None
    assert cliente_2 is None
