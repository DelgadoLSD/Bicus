"""H03 (F8 Buscar prestadores): quem aparece na busca e quem não aparece (NF8.1 a NF8.3)."""

from datetime import date, timedelta

import pytest

from bicus.services.busca_service import buscar_prestadores
from tests.fabricas import criar_prestador, criar_servico, criar_usuario, ponto_ao_norte

HOJE = date(2026, 11, 20)
RAIO_DA_BUSCA = 5.0


@pytest.fixture
def cliente(db):
    return criar_usuario("Ana")  # no Centro de Viçosa


def prestador_a(km: float, nome: str = "Lúcia", **campos):
    """Prestador a `km` quilômetros do cliente; `campos` troca raio, ativo, indisponibilidade..."""
    return criar_prestador(nome, ponto_ao_norte(km), **campos)


def encontrados(cliente, categoria_id: int, raio: float = RAIO_DA_BUSCA) -> list[str]:
    """Títulos dos serviços que a busca devolve."""
    resultados = buscar_prestadores(categoria_id, cliente, raio, HOJE)
    return [servico.titulo for _, servico, _ in resultados]


# --- busca por categoria e raio (NF8.1, NF8.2) ---------------------------------------------------


def test_nf8_2_encontra_o_servico_dentro_do_raio_com_a_distancia(cliente):
    servico = criar_servico(prestador_a(1.0))

    [(_, encontrado, distancia)] = buscar_prestadores(
        servico.categoria_id, cliente, RAIO_DA_BUSCA, HOJE
    )

    assert encontrado == servico
    assert distancia == pytest.approx(1.0)


def test_nf8_1_prestador_fora_do_raio_da_busca_nao_aparece(cliente):
    servico = criar_servico(prestador_a(6.0))

    assert encontrados(cliente, servico.categoria_id, raio=5.0) == []
    assert encontrados(cliente, servico.categoria_id, raio=7.0) == [servico.titulo]


def test_servico_de_outra_categoria_nao_aparece(cliente):
    faxina = criar_servico(prestador_a(1.0, "Lúcia"), categoria="Faxina")
    criar_servico(prestador_a(1.0, "Júlia"), categoria="Pintura")

    assert encontrados(cliente, faxina.categoria_id) == [faxina.titulo]


# --- quem não é exibido (NF8.3) ----------------------------------------------------------------


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


# --- indisponibilidade temporária (NF6.2) ------------------------------------------------------


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


# --- raio de deslocamento do prestador (NF4.3) -------------------------------------------------


def test_nf4_3_prestador_que_nao_vai_ate_o_cliente_nao_aparece(cliente):
    pedro = prestador_a(2.9, "Pedro", raio_deslocamento_km=2.0)
    servico = criar_servico(pedro)

    assert encontrados(cliente, servico.categoria_id) == []


def test_nf4_3_prestador_sem_raio_definido_atende_qualquer_distancia(cliente):
    longe = prestador_a(30.0, "Marcos", raio_deslocamento_km=None)
    servico = criar_servico(longe)

    assert encontrados(cliente, servico.categoria_id, raio=50.0) == [servico.titulo]
