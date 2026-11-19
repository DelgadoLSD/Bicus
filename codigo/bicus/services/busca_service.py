from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bicus.extensions import db
from bicus.models import Prestador, Servico, Usuario
from bicus.services.distancia_service import distancia_km


def buscar_prestadores(
    categoria_id: int, cliente: Usuario, raio_km: float, hoje: date
) -> list[tuple[Prestador, Servico, float]]:
    """H03 (F8): serviços ativos da categoria cujo prestador atende o cliente (NF8.3)."""
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
            resultados.append((prestador, servico, distancia))
    return resultados


def _atende(prestador: Prestador, distancia: float, raio_km: float, hoje: date) -> bool:
    """Dentro do raio da busca (NF8.1), dentro do raio de deslocamento do prestador (NF4.3) e sem
    indisponibilidade hoje (NF6.2)."""
    return (
        distancia <= raio_km
        and prestador.alcanca(distancia)
        and not prestador.indisponivel_em(hoje)
    )
