from sqlalchemy import select
from sqlalchemy.orm import selectinload

from bicus.extensions import db
from bicus.models import Prestador, Servico, Usuario
from bicus.services.distancia_service import distancia_km


def buscar_prestadores(
    categoria_id: int, cliente: Usuario, raio_km: float) -> list[tuple[Prestador, Servico, float]]:
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
        if distancia <= raio_km:
            resultados.append((prestador, servico, distancia))
    return resultados
