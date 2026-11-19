"""H04 (F9): pontuação de recomendação = 0,6 x nota/5 + 0,4 x (1 - distância/raio) (NF9.1)."""

import pytest

from bicus.services.pontuacao_service import calcular_pontuacao

RAIO = 5.0


def test_nota_maxima_colado_no_cliente_vale_1():
    assert calcular_pontuacao(5.0, 0.0, RAIO) == pytest.approx(1.0)


def test_exemplo_com_valores_conhecidos():
    # 0,6 x 4,5/5 + 0,4 x (1 - 1/5) = 0,54 + 0,32
    assert calcular_pontuacao(4.5, 1.0, RAIO) == pytest.approx(0.86)


def test_no_limite_do_raio_a_proximidade_nao_soma_nada():
    assert calcular_pontuacao(4.0, RAIO, RAIO) == pytest.approx(0.48)


def test_prestador_sem_avaliacao_conta_como_nota_3():
    assert calcular_pontuacao(None, 2.0, RAIO) == pytest.approx(calcular_pontuacao(3.0, 2.0, RAIO))


def test_com_a_mesma_distancia_a_nota_maior_vence():
    assert calcular_pontuacao(4.8, 2.0, RAIO) > calcular_pontuacao(4.2, 2.0, RAIO)


def test_com_a_mesma_nota_o_mais_perto_vence():
    assert calcular_pontuacao(4.5, 1.0, RAIO) > calcular_pontuacao(4.5, 3.0, RAIO)


def test_nf9_1_a_nota_pesa_mais_que_a_proximidade():
    cinco_estrelas_no_limite = calcular_pontuacao(5.0, RAIO, RAIO)
    uma_estrela_colado = calcular_pontuacao(1.0, 0.0, RAIO)

    assert cinco_estrelas_no_limite > uma_estrela_colado
