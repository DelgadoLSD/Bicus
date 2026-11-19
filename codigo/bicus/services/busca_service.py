from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bicus.extensions import db
from bicus.models import Prestador, Servico, Usuario
from bicus.services.distancia_service import distancia_km
from bicus.services.pontuacao_service import calcular_pontuacao


@dataclass(frozen=True)
class ResultadoBusca:
    """Um item da lista da busca: o serviço, quem presta, a que distância e com que pontuação."""

    prestador: Prestador
    servico: Servico
    distancia_km: float
    pontuacao: float


def buscar_prestadores(
    categoria_id: int, cliente: Usuario, raio_km: float, hoje: date
) -> list[ResultadoBusca]:
    """H03 (F8): serviços ativos da categoria cujo prestador atende o cliente (NF8.3),
    H04 (F9): ordenados do mais para o menos recomendado."""
    consulta = (
        select(Prestador, Servico)
        .join(Prestador.servicos)
        .where(
            Servico.categoria_id == categoria_id,
            Servico.ativo,
            Prestador.ativo,
            Prestador.id != cliente.id,
        )
        .options(selectinload(Prestador.usuario))
    )

    resultados = []
    for prestador, servico in db.session.execute(consulta):
        distancia = distancia_km(cliente.localizacao, prestador.localizacao_base)
        if _atende(prestador, distancia, raio_km, hoje):
            pontuacao = calcular_pontuacao(prestador.nota_media, distancia, raio_km)
            resultados.append(ResultadoBusca(prestador, servico, distancia, pontuacao))
    return ordenar_por_recomendacao(resultados)


def ordenar_por_recomendacao(resultados: list[ResultadoBusca]) -> list[ResultadoBusca]:
    """Maior pontuação primeiro. No empate (NF9.2), quem tem mais avaliações (cada avaliação vem de
    um serviço concluído) e, depois, o mais próximo."""
    return sorted(
        resultados,
        key=lambda r: (-r.pontuacao, -r.prestador.total_avaliacoes, r.distancia_km),
    )


def _atende(prestador: Prestador, distancia: float, raio_km: float, hoje: date) -> bool:
    """Dentro do raio da busca (NF8.1), dentro do raio de deslocamento do prestador (NF4.3) e sem
    indisponibilidade hoje (NF6.2)."""
    return (
        distancia <= raio_km
        and prestador.alcanca(distancia)
        and not prestador.indisponivel_em(hoje)
    )
