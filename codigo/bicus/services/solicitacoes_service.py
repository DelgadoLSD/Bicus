from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bicus.domain import EstadoSolicitacao
from bicus.extensions import db
from bicus.models import Prestador, Servico, Solicitacao, Usuario


def listar_solicitacoes(cliente: Usuario) -> list[Solicitacao]:
    consulta = (
        select(Solicitacao)
        .where(Solicitacao.cliente_id == cliente.id)
        .order_by(Solicitacao.data_criacao.desc(), Solicitacao.id.desc())
        .options(
            selectinload(Solicitacao.servico)
            .selectinload(Servico.prestador)
            .selectinload(Prestador.usuario)
        )
    )
    return list(db.session.scalars(consulta))


class SolicitacaoInvalidaError(Exception):
    """Operação recusada por uma regra de negócio; a mensagem é mostrada ao usuário."""


def cancelar_solicitacao(cliente: Usuario, solicitacao_id: int) -> None:
    solicitacao = db.session.get(Solicitacao, solicitacao_id)
    if solicitacao is None or solicitacao.cliente_id != cliente.id:
        raise SolicitacaoInvalidaError("Solicitação não encontrada.")
    if not solicitacao.pode_cancelar():
        raise SolicitacaoInvalidaError("Só é possível cancelar solicitações pendentes.")
    solicitacao.estado = EstadoSolicitacao.CANCELADA
    db.session.commit()
