"""Teste de exemplo — serve de referência de estilo para o RAG imitar
ao gerar novos testes a partir dos PRs."""


def somar(a: int, b: int) -> int:
    return a + b


def test_somar_numeros_positivos():
    assert somar(2, 3) == 5


def test_somar_com_zero():
    assert somar(0, 7) == 7


def test_somar_numeros_negativos():
    assert somar(-2, -3) == -5
