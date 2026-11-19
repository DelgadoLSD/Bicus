"""Métodos dos modelos: regras que envolvem um objeto só."""

import pytest

from bicus.domain import EstadoSolicitacao
from bicus.models import Solicitacao


@pytest.mark.parametrize("estado", list(EstadoSolicitacao), ids=lambda estado: estado.name.lower())
def test_nf11_6_so_solicitacao_pendente_pode_ser_cancelada(estado):
    solicitacao = Solicitacao(estado=estado)

    assert solicitacao.pode_cancelar() == (estado == EstadoSolicitacao.PENDENTE)
