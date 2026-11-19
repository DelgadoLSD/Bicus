"""A página de busca, como o navegador usa: filtros (H03), ordem de recomendação (H04) e
ordem escolhida pelo cliente (H05)."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from tests.fabricas import criar_prestador, criar_servico, criar_usuario, ponto_ao_norte


@pytest.fixture
def cliente_logado(client, db):
    cliente = criar_usuario("Ana")
    client.post(f"/entrar/{cliente.id}")
    return cliente


def buscar(client, servico, raio: float = 5) -> str:
    return client.get(f"/busca?categoria={servico.categoria_id}&raio={raio}").text


def test_busca_exige_usuario_logado(client):
    resposta = client.get("/busca")

    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith("/entrar")


def test_busca_mostra_os_dados_do_prestador_e_o_botao_solicitar(client, cliente_logado):
    lucia = criar_prestador("Lúcia", ponto_ao_norte(1.0), nota_media=4.5, total_avaliacoes=12)
    servico = criar_servico(lucia)

    pagina = buscar(client, servico)

    assert "Lúcia" in pagina
    assert servico.titulo in pagina
    assert "R$ 100,00" in pagina  # NF8.4: faixa de preço, no formato brasileiro
    assert "4,5" in pagina
    assert "12 avaliações" in pagina
    assert "1,0 km" in pagina
    assert f"/solicitacoes?servico={servico.id}" in pagina  # botão Solicitar (H01)


def test_prestador_sem_avaliacao_aparece_como_sem_avaliacoes(client, cliente_logado):
    julia = criar_prestador("Júlia", ponto_ao_norte(1.0), nota_media=None, total_avaliacoes=0)
    servico = criar_servico(julia)

    assert "Sem avaliações" in buscar(client, servico)


def test_nf8_5_busca_sem_resultado_sugere_ampliar_o_raio(client, cliente_logado):
    servico = criar_servico(criar_prestador("Carla", ponto_ao_norte(8.0)))

    assert "ampliar o raio" in buscar(client, servico, raio=5)


def test_busca_usa_a_data_de_hoje_para_a_indisponibilidade(client, cliente_logado):
    hoje = date.today()
    rafael = criar_prestador(
        "Rafael",
        ponto_ao_norte(1.0),
        inicio_indisponibilidade=hoje,
        fim_indisponibilidade=hoje + timedelta(days=3),
    )
    servico = criar_servico(rafael)

    assert servico.titulo not in buscar(client, servico)


def test_f9_pagina_mostra_o_mais_recomendado_primeiro(client, cliente_logado):
    carla = criar_servico(criar_prestador("Carla", ponto_ao_norte(3.7), nota_media=4.0))
    criar_servico(criar_prestador("Lúcia", ponto_ao_norte(0.7), nota_media=4.5))

    pagina = buscar(client, carla)

    assert pagina.index("Faxina com Lúcia") < pagina.index("Faxina com Carla")


# --- H05: ordem escolhida pelo cliente (NF8.8) ---------------------------------------------------


@pytest.fixture
def helena(db):
    """Helena (nota 5,0, a 3 km) e Rosa (nota 3,5, a 0,5 km): a recomendação põe Rosa primeiro
    (0,78 contra 0,76), mas por avaliação vem Helena. Devolve o serviço da Helena."""
    servico = criar_servico(
        criar_prestador("Helena", ponto_ao_norte(3.0), nota_media=5.0), preco_minimo=Decimal(150)
    )
    criar_servico(
        criar_prestador("Rosa", ponto_ao_norte(0.5), nota_media=3.5), preco_minimo=Decimal(80)
    )
    return servico


@pytest.mark.parametrize(
    ("ordem", "primeira"),
    [("", "Rosa"), ("avaliacao", "Helena"), ("distancia", "Rosa"), ("xyz", "Rosa")],
    ids=["padrao_recomendados", "avaliacao", "distancia", "valor_invalido_vira_padrao"],
)
def test_nf8_8_ordem_escolhida_pelo_endereco(client, cliente_logado, helena, ordem, primeira):
    endereco = f"/busca?categoria={helena.categoria_id}&raio=5&ordem={ordem}"

    pagina = client.get(endereco).text

    posicao_helena = pagina.index("Faxina com Helena")
    posicao_rosa = pagina.index("Faxina com Rosa")
    assert (posicao_helena < posicao_rosa) == (primeira == "Helena")


def test_nf8_8_colunas_levam_a_cada_ordem_e_a_escolhida_fica_marcada(
    client, cliente_logado, helena
):
    pagina = client.get(f"/busca?categoria={helena.categoria_id}&raio=5&ordem=avaliacao").text

    assert "ordem=distancia" in pagina  # títulos das outras colunas são links
    assert "ordem=preco" in pagina
    assert "avaliação, da maior para a menor" in pagina  # a ordem atual, escrita acima da tabela
    assert "ordem=recomendacao" in pagina  # link "voltar para recomendados"
    assert 'name="ordem" value="avaliacao"' in pagina  # uma nova busca mantém a ordem
