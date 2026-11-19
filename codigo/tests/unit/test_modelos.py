"""Métodos dos modelos: regras que envolvem um objeto só."""

from datetime import date

import pytest

from bicus.domain import EstadoSolicitacao
from bicus.models import Prestador, Solicitacao

HOJE = date(2026, 11, 20)


# --- Solicitacao (H02) --------------------------------------------------------------------------


@pytest.mark.parametrize("estado", list(EstadoSolicitacao), ids=lambda estado: estado.name.lower())
def test_nf11_6_so_solicitacao_pendente_pode_ser_cancelada(estado):
    solicitacao = Solicitacao(estado=estado)

    assert solicitacao.pode_cancelar() == (estado == EstadoSolicitacao.PENDENTE)


# --- Prestador (H03) ----------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("inicio", "fim", "indisponivel"),
    [
        (None, None, False),
        (date(2026, 11, 21), date(2026, 11, 25), False),
        (date(2026, 11, 20), date(2026, 11, 25), True),
        (date(2026, 11, 15), date(2026, 11, 25), True),
        (date(2026, 11, 15), date(2026, 11, 20), True),
        (date(2026, 11, 10), date(2026, 11, 19), False),
        (date(2026, 11, 15), None, True),
    ],
    ids=[
        "sem_periodo",
        "ainda_vai_comecar",
        "primeiro_dia",
        "no_meio",
        "ultimo_dia",
        "ja_acabou",
        "sem_data_para_acabar",
    ],
)
def test_nf6_2_prestador_indisponivel_em(inicio, fim, indisponivel):
    prestador = Prestador(inicio_indisponibilidade=inicio, fim_indisponibilidade=fim)

    assert prestador.indisponivel_em(HOJE) is indisponivel


@pytest.mark.parametrize(
    ("raio", "distancia", "alcanca"),
    [(2.0, 1.5, True), (2.0, 2.0, True), (2.0, 2.5, False), (None, 100.0, True)],
    ids=["dentro_do_raio", "no_limite", "fora_do_raio", "sem_raio_definido"],
)
def test_nf4_3_prestador_alcanca_a_distancia(raio, distancia, alcanca):
    prestador = Prestador(raio_deslocamento_km=raio)

    assert prestador.alcanca(distancia) is alcanca
