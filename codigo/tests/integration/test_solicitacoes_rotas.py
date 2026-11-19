"""Rotas de solicitações, como o navegador usa: criar (H01), listar e cancelar (H02)."""

from datetime import date, timedelta

import pytest
from sqlalchemy import func, select

from bicus.domain import EstadoSolicitacao
from bicus.extensions import db as banco
from bicus.models import Solicitacao
from tests.fabricas import criar_prestador, criar_servico, criar_usuario, nova_solicitacao


@pytest.fixture
def servico(db):
    return criar_servico(criar_prestador("Lúcia"))


@pytest.fixture
def cliente_logado(client, db):
    cliente = criar_usuario("Ana")
    client.post(f"/entrar/{cliente.id}")
    return cliente


def formulario(servico, **alteracoes) -> dict:
    campos = {
        "servico_id": servico.id,
        "descricao": "Trocar três tomadas da sala.",
        "data_desejada": (date.today() + timedelta(days=1)).isoformat(),
        "turno": "MANHA",
        "endereco": "Rua Gomes Barbosa, 120 - Centro",
    }
    return campos | alteracoes


def total_de_solicitacoes() -> int:
    return banco.session.scalar(select(func.count()).select_from(Solicitacao))


# --- H01: criar solicitação -----------------------------------------------------------------------


def test_solicitacao_valida_volta_para_a_lista_com_mensagem_de_sucesso(
    client, cliente_logado, servico
):
    resposta = client.post("/solicitacoes", data=formulario(servico), follow_redirects=True)

    assert resposta.status_code == 200
    assert "Solicitação enviada." in resposta.text
    assert total_de_solicitacoes() == 1


def test_solicitacao_invalida_reabre_o_formulario_com_a_mensagem(client, cliente_logado, servico):
    ontem = (date.today() - timedelta(days=1)).isoformat()

    resposta = client.post("/solicitacoes", data=formulario(servico, data_desejada=ontem))

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith(f"/solicitacoes?servico={servico.id}")
    pagina = client.get(resposta.headers["Location"])
    assert "anterior a hoje" in pagina.text
    assert 'id="nova-solicitacao"' in pagina.text
    assert total_de_solicitacoes() == 0


def test_turno_invalido_mostra_mensagem_em_vez_de_erro(client, cliente_logado, servico):
    resposta = client.post(
        "/solicitacoes", data=formulario(servico, turno="XYZ"), follow_redirects=True
    )

    assert resposta.status_code == 200
    assert "Escolha o turno." in resposta.text
    assert total_de_solicitacoes() == 0


# --- H02: Minhas solicitações e cancelamento ------------------------------------------------------


def test_minhas_solicitacoes_exige_usuario_logado(client):
    resposta = client.get("/solicitacoes")

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/entrar")


def test_minhas_solicitacoes_mostra_so_as_do_cliente_logado(client, cliente_logado, servico):
    servico_do_bruno = criar_servico(criar_prestador("Júlia"), categoria="Pintura")
    nova_solicitacao(cliente_logado, servico)
    nova_solicitacao(criar_usuario("Bruno"), servico_do_bruno)

    pagina = client.get("/solicitacoes").text

    assert servico.titulo in pagina
    assert servico_do_bruno.titulo not in pagina


def test_botao_cancelar_aparece_so_nas_pendentes(client, cliente_logado, servico):
    pendente = nova_solicitacao(cliente_logado, servico)
    aceita = nova_solicitacao(cliente_logado, servico, estado=EstadoSolicitacao.ACEITA)

    pagina = client.get("/solicitacoes").text

    assert f"/solicitacoes/{pendente.id}/cancelar" in pagina
    assert f"/solicitacoes/{aceita.id}/cancelar" not in pagina


def test_cancelar_pela_tela_avisa_e_mantem_no_historico(client, cliente_logado, servico):
    solicitacao = nova_solicitacao(cliente_logado, servico)

    resposta = client.post(f"/solicitacoes/{solicitacao.id}/cancelar", follow_redirects=True)

    assert "Solicitação cancelada." in resposta.text
    assert "Cancelada" in resposta.text  # continua na lista, com o novo estado
    assert solicitacao.estado == EstadoSolicitacao.CANCELADA


def test_cancelar_solicitacao_de_outro_cliente_pela_url_e_recusado(client, cliente_logado, servico):
    de_outro = nova_solicitacao(criar_usuario("Bruno"), servico)

    resposta = client.post(f"/solicitacoes/{de_outro.id}/cancelar", follow_redirects=True)

    assert "Solicitação não encontrada." in resposta.text
    assert de_outro.estado == EstadoSolicitacao.PENDENTE
