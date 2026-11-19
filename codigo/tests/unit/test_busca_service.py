"""Busca de prestadores: quem aparece e quem não aparece (H03, NF8.1 a NF8.3), a ordem de
recomendação (H04, F9 e NF9.2) e a ordem escolhida pelo cliente (H05, NF8.8)."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from bicus.domain import OrdemBusca
from bicus.models import Prestador, Servico
from bicus.services.busca_service import (
    ResultadoBusca,
    buscar_prestadores,
    ordenar_por_recomendacao,
)
from tests.fabricas import criar_prestador, criar_servico, criar_usuario, ponto_ao_norte

HOJE = date(2026, 11, 20)
RAIO_DA_BUSCA = 5.0


@pytest.fixture
def cliente(db):
    return criar_usuario("Ana")  # no Centro de Viçosa


def prestador_a(km: float, nome: str = "Lúcia", **campos):
    """Prestador a `km` quilômetros do cliente; `campos` troca raio, ativo, indisponibilidade..."""
    return criar_prestador(nome, ponto_ao_norte(km), **campos)


def encontrados(cliente, categoria_id: int, raio: float = RAIO_DA_BUSCA, **opcoes) -> list[str]:
    """Títulos dos serviços que a busca devolve, na ordem em que vêm."""
    resultados = buscar_prestadores(categoria_id, cliente, raio, HOJE, **opcoes)
    return [resultado.servico.titulo for resultado in resultados]


def criar_as_quatro_faxineiras() -> int:
    """O cenário dos dados de exemplo (busca da Ana em Faxina, 5 km), criado fora de ordem de
    propósito para nenhuma ordem sair certa por acaso. Devolve o id da categoria."""
    criar_servico(prestador_a(3.7, "Carla", nota_media=4.0), preco_minimo=Decimal(100))
    criar_servico(prestador_a(2.9, "Helena", nota_media=5.0), preco_minimo=Decimal(150))
    criar_servico(
        prestador_a(0.6, "Rosa", nota_media=None, total_avaliacoes=0), preco_minimo=Decimal(80)
    )
    lucia = criar_servico(prestador_a(0.7, "Lúcia", nota_media=4.5), preco_minimo=Decimal(120))
    return lucia.categoria_id


# --- H03: busca por categoria e raio (NF8.1, NF8.2) -----------------------------------------------


def test_nf8_2_encontra_o_servico_dentro_do_raio_com_a_distancia(cliente):
    servico = criar_servico(prestador_a(1.0))

    [resultado] = buscar_prestadores(servico.categoria_id, cliente, RAIO_DA_BUSCA, HOJE)

    assert resultado.servico == servico
    assert resultado.distancia_km == pytest.approx(1.0)


def test_nf8_1_prestador_fora_do_raio_da_busca_nao_aparece(cliente):
    servico = criar_servico(prestador_a(6.0))

    assert encontrados(cliente, servico.categoria_id, raio=5.0) == []
    assert encontrados(cliente, servico.categoria_id, raio=7.0) == [servico.titulo]


def test_servico_de_outra_categoria_nao_aparece(cliente):
    faxina = criar_servico(prestador_a(1.0, "Lúcia"), categoria="Faxina")
    criar_servico(prestador_a(1.0, "Júlia"), categoria="Pintura")

    assert encontrados(cliente, faxina.categoria_id) == [faxina.titulo]


# --- H03: quem não é exibido (NF8.3) --------------------------------------------------------------


def test_nf8_3_o_proprio_usuario_nao_aparece(db):
    lucia = prestador_a(0.0)
    servico = criar_servico(lucia)

    assert encontrados(lucia.usuario, servico.categoria_id) == []


def test_nf8_3_perfil_desativado_nao_aparece(cliente):
    servico = criar_servico(prestador_a(1.0, ativo=False))

    assert encontrados(cliente, servico.categoria_id) == []


def test_nf8_3_servico_inativo_nao_aparece(cliente):
    tiago = prestador_a(1.0, "Tiago")
    matematica = criar_servico(tiago, categoria="Aulas particulares", titulo="Matemática")
    criar_servico(tiago, categoria="Aulas particulares", titulo="Física", ativo=False)

    assert encontrados(cliente, matematica.categoria_id) == ["Matemática"]


# --- H03: indisponibilidade temporária (NF6.2) ----------------------------------------------------


def test_nf6_2_prestador_indisponivel_hoje_nao_aparece(cliente):
    rafael = prestador_a(
        1.0,
        "Rafael",
        inicio_indisponibilidade=HOJE - timedelta(days=2),
        fim_indisponibilidade=HOJE + timedelta(days=10),
    )
    servico = criar_servico(rafael)

    assert encontrados(cliente, servico.categoria_id) == []


@pytest.mark.parametrize(
    ("dias_inicio", "dias_fim"), [(-10, -1), (1, 5)], ids=["ja_acabou", "ainda_vai_comecar"]
)
def test_nf6_2_indisponibilidade_fora_de_hoje_nao_esconde(cliente, dias_inicio, dias_fim):
    rafael = prestador_a(
        1.0,
        "Rafael",
        inicio_indisponibilidade=HOJE + timedelta(days=dias_inicio),
        fim_indisponibilidade=HOJE + timedelta(days=dias_fim),
    )
    servico = criar_servico(rafael)

    assert encontrados(cliente, servico.categoria_id) == [servico.titulo]


# --- H03: raio de deslocamento do prestador (NF4.3) -----------------------------------------------


def test_nf4_3_prestador_que_nao_vai_ate_o_cliente_nao_aparece(cliente):
    pedro = prestador_a(2.9, "Pedro", raio_deslocamento_km=2.0)
    servico = criar_servico(pedro)

    assert encontrados(cliente, servico.categoria_id) == []


def test_nf4_3_prestador_sem_raio_definido_atende_qualquer_distancia(cliente):
    longe = prestador_a(30.0, "Marcos", raio_deslocamento_km=None)
    servico = criar_servico(longe)

    assert encontrados(cliente, servico.categoria_id, raio=50.0) == [servico.titulo]


# --- H04: ordem de recomendação (F9, NF9.1, NF9.2) ------------------------------------------------


def test_f9_cada_resultado_traz_a_pontuacao(cliente):
    servico = criar_servico(prestador_a(1.0, nota_media=4.5))

    [resultado] = buscar_prestadores(servico.categoria_id, cliente, RAIO_DA_BUSCA, HOJE)

    assert resultado.pontuacao == pytest.approx(0.6 * 4.5 / 5 + 0.4 * (1 - 1.0 / 5))


def test_f9_lista_vem_da_maior_para_a_menor_pontuacao(cliente):
    faxina = criar_as_quatro_faxineiras()

    assert encontrados(cliente, faxina) == [
        "Faxina com Lúcia",  # 0,88: boa nota e bem perto
        "Faxina com Helena",  # 0,77: nota máxima, mas 2 km mais longe
        "Faxina com Rosa",  # 0,71: sem avaliação conta como nota 3, mas é a mais perto
        "Faxina com Carla",  # 0,58: nota boa, mas longe
    ]


def resultado(pontuacao: float, avaliacoes: int, distancia: float, titulo: str) -> ResultadoBusca:
    """Resultado montado à mão (sem banco), para testar só a ordem."""
    return ResultadoBusca(
        Prestador(total_avaliacoes=avaliacoes), Servico(titulo=titulo), distancia, pontuacao
    )


def titulos(resultados: list[ResultadoBusca]) -> list[str]:
    return [r.servico.titulo for r in resultados]


def test_nf9_2_no_empate_vem_primeiro_quem_tem_mais_avaliacoes():
    poucas = resultado(0.8, avaliacoes=3, distancia=1.0, titulo="poucas")
    muitas = resultado(0.8, avaliacoes=30, distancia=1.0, titulo="muitas")

    assert titulos(ordenar_por_recomendacao([poucas, muitas])) == ["muitas", "poucas"]


def test_nf9_2_se_ainda_empatar_vem_primeiro_o_mais_proximo():
    longe = resultado(0.8, avaliacoes=10, distancia=3.0, titulo="longe")
    perto = resultado(0.8, avaliacoes=10, distancia=1.0, titulo="perto")

    assert titulos(ordenar_por_recomendacao([longe, perto])) == ["perto", "longe"]


def test_pontuacao_maior_vence_mesmo_com_menos_avaliacoes():
    popular = resultado(0.7, avaliacoes=100, distancia=1.0, titulo="popular")
    melhor = resultado(0.8, avaliacoes=1, distancia=1.0, titulo="melhor")

    assert titulos(ordenar_por_recomendacao([popular, melhor])) == ["melhor", "popular"]


# --- H05: ordem escolhida pelo cliente (NF8.8) ---------------------------------------------------


@pytest.mark.parametrize(
    ("ordem", "esperado"),
    [
        (OrdemBusca.RECOMENDACAO, ["Lúcia", "Helena", "Rosa", "Carla"]),
        (OrdemBusca.AVALIACAO, ["Helena", "Lúcia", "Carla", "Rosa"]),  # sem avaliação no fim
        (OrdemBusca.DISTANCIA, ["Rosa", "Lúcia", "Helena", "Carla"]),  # 0,6 0,7 2,9 3,7 km
        (OrdemBusca.PRECO, ["Rosa", "Carla", "Lúcia", "Helena"]),  # R$ 80 100 120 150
    ],
    ids=["recomendacao", "avaliacao", "distancia", "preco"],
)
def test_nf8_8_cliente_escolhe_a_ordem_da_lista(cliente, ordem, esperado):
    faxina = criar_as_quatro_faxineiras()

    titulos_encontrados = encontrados(cliente, faxina, ordem=ordem)

    assert titulos_encontrados == [f"Faxina com {nome}" for nome in esperado]


def test_nf8_8_no_empate_da_coluna_escolhida_decide_a_recomendacao(cliente):
    # Mesma nota; a mais perto tem pontuação maior e deve vir primeiro ao ordenar por avaliação.
    criar_servico(prestador_a(3.0, "Longe", nota_media=4.5))
    perto = criar_servico(prestador_a(1.0, "Perto", nota_media=4.5))

    lista = encontrados(cliente, perto.categoria_id, ordem=OrdemBusca.AVALIACAO)

    assert lista == ["Faxina com Perto", "Faxina com Longe"]
