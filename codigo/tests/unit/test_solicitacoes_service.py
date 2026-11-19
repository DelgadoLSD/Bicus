"""Regras do service de solicitações: H01 (criar) e H02 (listar e cancelar)."""

from dataclasses import replace
from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import func, select

from bicus.domain import EstadoSolicitacao, Turno
from bicus.extensions import db as banco
from bicus.models import Solicitacao
from bicus.services.solicitacoes_service import (
    LIMITE_PENDENTES,
    DadosSolicitacao,
    SolicitacaoInvalidaError,
    cancelar_solicitacao,
    criar_solicitacao,
    listar_solicitacoes,
)
from tests.fabricas import criar_prestador, criar_servico, criar_usuario, nova_solicitacao

HOJE = date(2026, 11, 20)
AMANHA = HOJE + timedelta(days=1)
ONTEM = HOJE - timedelta(days=1)


@pytest.fixture
def cliente(db):
    return criar_usuario("Ana")


@pytest.fixture
def servico(db):
    return criar_servico(criar_prestador("Lúcia"))


def dados_validos(servico) -> DadosSolicitacao:
    return DadosSolicitacao(
        servico_id=servico.id,
        descricao="Trocar três tomadas da sala.",
        data_desejada=AMANHA,
        turno=Turno.MANHA,
        endereco="Rua Gomes Barbosa, 120 - Centro",
    )


def total_de_solicitacoes() -> int:
    return banco.session.scalar(select(func.count()).select_from(Solicitacao))


def enviar_ate_o_limite(cliente, servico) -> list[Solicitacao]:
    return [
        criar_solicitacao(cliente, dados_validos(servico), HOJE) for _ in range(LIMITE_PENDENTES)
    ]


# --- H01: caso válido (NF13.1) --------------------------------------------------------------------


def test_nf13_1_solicitacao_valida_nasce_pendente(cliente, servico):
    solicitacao = criar_solicitacao(cliente, dados_validos(servico), HOJE)

    assert solicitacao.id is not None
    assert solicitacao.estado == EstadoSolicitacao.PENDENTE
    assert solicitacao.cliente == cliente
    assert solicitacao.servico == servico
    assert solicitacao.data_criacao is not None


# --- H01: campos obrigatórios (NF11.1) ------------------------------------------------------------


@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("servico_id", None, "não está disponível"),
        ("descricao", "", "Descreva"),
        ("descricao", "   ", "Descreva"),
        ("data_desejada", None, "data desejada"),
        ("turno", None, "turno"),
    ],
    ids=["sem_servico", "descricao_vazia", "descricao_so_espacos", "sem_data", "sem_turno"],
)
def test_nf11_1_campo_obrigatorio_vazio_e_recusado(cliente, servico, campo, valor, mensagem):
    dados = replace(dados_validos(servico), **{campo: valor})

    with pytest.raises(SolicitacaoInvalidaError, match=mensagem):
        criar_solicitacao(cliente, dados, HOJE)
    assert total_de_solicitacoes() == 0


def test_nf11_1_endereco_vazio_usa_o_endereco_do_cliente(cliente, servico):
    dados = replace(dados_validos(servico), endereco="   ")

    solicitacao = criar_solicitacao(cliente, dados, HOJE)

    assert solicitacao.endereco == cliente.endereco


def test_servico_inexistente_e_recusado(cliente, servico):
    dados = replace(dados_validos(servico), servico_id=servico.id + 100)

    with pytest.raises(SolicitacaoInvalidaError, match="não está disponível"):
        criar_solicitacao(cliente, dados, HOJE)


def test_servico_inativo_e_recusado(cliente):
    inativo = criar_servico(criar_prestador("Tiago"), ativo=False)

    with pytest.raises(SolicitacaoInvalidaError, match="não está disponível"):
        criar_solicitacao(cliente, dados_validos(inativo), HOJE)


def test_servico_de_prestador_desativado_e_recusado(cliente):
    servico = criar_servico(criar_prestador("Sônia", ativo=False))

    with pytest.raises(SolicitacaoInvalidaError, match="não está disponível"):
        criar_solicitacao(cliente, dados_validos(servico), HOJE)


# --- H01: data válida (NF11.2) --------------------------------------------------------------------


def test_nf11_2_data_de_ontem_e_recusada(cliente, servico):
    dados = replace(dados_validos(servico), data_desejada=ONTEM)

    with pytest.raises(SolicitacaoInvalidaError, match="anterior a hoje"):
        criar_solicitacao(cliente, dados, HOJE)
    assert total_de_solicitacoes() == 0


def test_nf11_2_data_de_hoje_e_aceita(cliente, servico):
    dados = replace(dados_validos(servico), data_desejada=HOJE)

    assert criar_solicitacao(cliente, dados, HOJE).data_desejada == HOJE


# --- H01: autossolicitação (NF11.3) ---------------------------------------------------------------


def test_nf11_3_prestador_nao_solicita_o_proprio_servico(servico):
    dono = servico.prestador.usuario

    with pytest.raises(SolicitacaoInvalidaError, match="próprio serviço"):
        criar_solicitacao(dono, dados_validos(servico), HOJE)
    assert total_de_solicitacoes() == 0


# --- H01: limite de pendentes (NF11.5) ------------------------------------------------------------


def test_nf11_5_pendente_alem_do_limite_e_recusada(cliente, servico):
    enviar_ate_o_limite(cliente, servico)

    with pytest.raises(SolicitacaoInvalidaError, match="pendentes"):
        criar_solicitacao(cliente, dados_validos(servico), HOJE)
    assert total_de_solicitacoes() == LIMITE_PENDENTES


def test_nf11_5_cancelar_uma_pendente_libera_vaga(cliente, servico):
    primeira, *_ = enviar_ate_o_limite(cliente, servico)
    cancelar_solicitacao(cliente, primeira.id)

    nova = criar_solicitacao(cliente, dados_validos(servico), HOJE)

    assert nova.estado == EstadoSolicitacao.PENDENTE


def test_nf11_5_pendentes_de_outro_cliente_nao_contam(cliente, servico):
    enviar_ate_o_limite(criar_usuario("Bruno"), servico)

    assert criar_solicitacao(cliente, dados_validos(servico), HOJE).id is not None


# --- H02: Minhas solicitações (F17) ---------------------------------------------------------------


def test_f17_lista_so_as_solicitacoes_do_cliente(cliente, servico):
    minhas = [nova_solicitacao(cliente, servico), nova_solicitacao(cliente, servico)]
    nova_solicitacao(criar_usuario("Bruno"), servico)

    listadas = listar_solicitacoes(cliente)

    assert {s.id for s in listadas} == {s.id for s in minhas}


def test_f17_lista_a_mais_recente_primeiro(cliente, servico):
    # Criadas fora de ordem, para a ordem da lista não coincidir com a ordem de inserção.
    antiga = nova_solicitacao(cliente, servico, data_criacao=datetime(2026, 11, 18, 9, 0))
    recente = nova_solicitacao(cliente, servico, data_criacao=datetime(2026, 11, 20, 9, 0))
    do_meio = nova_solicitacao(cliente, servico, data_criacao=datetime(2026, 11, 19, 9, 0))

    assert listar_solicitacoes(cliente) == [recente, do_meio, antiga]


def test_f17_cliente_sem_solicitacoes_recebe_lista_vazia(cliente):
    assert listar_solicitacoes(cliente) == []


# --- H02: cancelamento pelo cliente (NF11.6) ------------------------------------------------------


def test_nf11_6_cancelar_pendente_vira_cancelada(cliente, servico):
    solicitacao = nova_solicitacao(cliente, servico)

    cancelar_solicitacao(cliente, solicitacao.id)

    assert solicitacao.estado == EstadoSolicitacao.CANCELADA


def test_nf11_6_nao_cancela_solicitacao_de_outro_cliente(cliente, servico):
    de_outro = nova_solicitacao(criar_usuario("Bruno"), servico)

    with pytest.raises(SolicitacaoInvalidaError, match="não encontrada"):
        cancelar_solicitacao(cliente, de_outro.id)
    assert de_outro.estado == EstadoSolicitacao.PENDENTE


def test_cancelar_solicitacao_inexistente_e_recusado(cliente):
    with pytest.raises(SolicitacaoInvalidaError, match="não encontrada"):
        cancelar_solicitacao(cliente, 999)


@pytest.mark.parametrize(
    "estado",
    [estado for estado in EstadoSolicitacao if estado != EstadoSolicitacao.PENDENTE],
    ids=lambda estado: estado.name.lower(),
)
def test_nf11_6_so_cancela_solicitacao_pendente(cliente, servico, estado):
    solicitacao = nova_solicitacao(cliente, servico, estado=estado)

    with pytest.raises(SolicitacaoInvalidaError, match="pendentes"):
        cancelar_solicitacao(cliente, solicitacao.id)
    assert solicitacao.estado == estado
