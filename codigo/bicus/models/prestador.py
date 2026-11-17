from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bicus.domain import Coordenada
from bicus.extensions import db

if TYPE_CHECKING:
    from bicus.models.servico import Servico
    from bicus.models.usuario import Usuario


class Prestador(db.Model):
    __tablename__ = "prestador"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), unique=True)
    latitude_base: Mapped[float]
    longitude_base: Mapped[float]
    raio_deslocamento_km: Mapped[float | None]
    inicio_indisponibilidade: Mapped[date | None]
    fim_indisponibilidade: Mapped[date | None]
    ativo: Mapped[bool] = mapped_column(default=True)
    nota_media: Mapped[float | None]
    total_avaliacoes: Mapped[int] = mapped_column(default=0)

    usuario: Mapped[Usuario] = relationship(back_populates="prestador")
    servicos: Mapped[list[Servico]] = relationship(back_populates="prestador")

    @property
    def localizacao_base(self) -> Coordenada:
        return Coordenada(self.latitude_base, self.longitude_base)
