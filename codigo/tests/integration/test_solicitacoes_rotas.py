"""H01: a rota de criar solicitação mostra a mensagem do erro em vez de gravar ou quebrar."""

from datetime import date, timedelta

import pytest
from sqlalchemy import func, select

from bicus.extensions import db as banco
from bicus.models import Solicitacao
from tests.fabricas import criar_prestador, criar_servico, criar_usuario


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
