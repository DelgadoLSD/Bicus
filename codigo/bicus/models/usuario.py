from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bicus.domain import Coordenada
from bicus.extensions import db

if TYPE_CHECKING:
    from bicus.models.prestador import Prestador
    from bicus.models.solicitacao import Solicitacao


class Usuario(db.Model):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    endereco: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float]
    longitude: Mapped[float]

    prestador: Mapped[Prestador | None] = relationship(back_populates="usuario")
    solicitacoes: Mapped[list[Solicitacao]] = relationship(back_populates="cliente")

    @property
    def localizacao(self) -> Coordenada:
        return Coordenada(self.latitude, self.longitude)
