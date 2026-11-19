from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from bicus.domain import EstadoSolicitacao, Turno
from bicus.extensions import db
from bicus.models import Prestador, Servico, Solicitacao, Usuario

LIMITE_PENDENTES = 10  # NF11.5


class SolicitacaoInvalidaError(Exception):
    """Operação recusada por uma regra de negócio; a mensagem é mostrada ao usuário."""


@dataclass(frozen=True)
class DadosSolicitacao:
    """Dados do formulário de nova solicitação; o que veio vazio ou inválido chega como None."""

    servico_id: int | None
    descricao: str
    data_desejada: date | None
    turno: Turno | None
    endereco: str


def criar_solicitacao(cliente: Usuario, dados: DadosSolicitacao, hoje: date) -> Solicitacao:
    """H01 (F11): cria a solicitação no estado Pendente ou recusa com SolicitacaoInvalidaError."""
    _validar_campos_obrigatorios(dados)
    servico = _servico_disponivel(dados.servico_id)
    _validar_data_desejada(dados.data_desejada, hoje)
    _validar_cliente(cliente, servico)

    solicitacao = Solicitacao(
        cliente=cliente,
        servico=servico,
        descricao=dados.descricao.strip(),
        data_desejada=dados.data_desejada,
        turno=dados.turno,
        endereco=dados.endereco.strip() or cliente.endereco,
    )
    db.session.add(solicitacao)
    db.session.commit()
    return solicitacao


def _validar_campos_obrigatorios(dados: DadosSolicitacao) -> None:
    """NF11.1: descrição, data desejada e turno (o serviço é conferido à parte)."""
    if not dados.descricao.strip():
        raise SolicitacaoInvalidaError("Descreva o que você precisa.")
    if dados.data_desejada is None:
        raise SolicitacaoInvalidaError("Informe a data desejada.")
    if dados.turno is None:
        raise SolicitacaoInvalidaError("Escolha o turno.")


def _servico_disponivel(servico_id: int | None) -> Servico:
    servico = db.session.get(Servico, servico_id) if servico_id is not None else None
    if servico is None or not servico.disponivel():
        raise SolicitacaoInvalidaError("Este serviço não está disponível.")
    return servico


def _validar_data_desejada(data_desejada: date, hoje: date) -> None:
    """NF11.2: a data desejada é hoje ou depois."""
    if data_desejada < hoje:
        raise SolicitacaoInvalidaError("A data desejada não pode ser anterior a hoje.")


def _validar_cliente(cliente: Usuario, servico: Servico) -> None:
    """NF11.3 (autossolicitação) e NF11.5 (limite de pendentes)."""
    if servico.oferecido_por(cliente):
        raise SolicitacaoInvalidaError("Você não pode solicitar o próprio serviço.")
    if _total_de_pendentes(cliente) >= LIMITE_PENDENTES:
        raise SolicitacaoInvalidaError(
            f"Você já tem {LIMITE_PENDENTES} solicitações pendentes. "
            "Aguarde a resposta ou cancele alguma antes de enviar outra."
        )


def _total_de_pendentes(cliente: Usuario) -> int:
    consulta = (
        select(func.count())
        .select_from(Solicitacao)
        .where(
            Solicitacao.cliente_id == cliente.id,
            Solicitacao.estado == EstadoSolicitacao.PENDENTE,
        )
    )
    return db.session.scalar(consulta)


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


def cancelar_solicitacao(cliente: Usuario, solicitacao_id: int) -> None:
    solicitacao = db.session.get(Solicitacao, solicitacao_id)
    if solicitacao is None or solicitacao.cliente_id != cliente.id:
        raise SolicitacaoInvalidaError("Solicitação não encontrada.")
    if not solicitacao.pode_cancelar():
        raise SolicitacaoInvalidaError("Só é possível cancelar solicitações pendentes.")
    solicitacao.estado = EstadoSolicitacao.CANCELADA
    db.session.commit()
