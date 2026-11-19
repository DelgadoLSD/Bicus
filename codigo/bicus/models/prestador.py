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

    id: Mapped[int] = mapped_column(ForeignKey("usuario.id"), primary_key=True)
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

    def indisponivel_em(self, data: date) -> bool:
        """NF6.2: a data cai no período marcado como indisponível (primeiro e último dia inclusos).
        Sem data de fim, a indisponibilidade continua até ser encerrada."""
        inicio, fim = self.inicio_indisponibilidade, self.fim_indisponibilidade
        if inicio is None:
            return False
        return inicio <= data and (fim is None or data <= fim)

    def alcanca(self, distancia_km: float) -> bool:
        """NF4.3: a distância cabe no raio de deslocamento; sem raio definido, vale qualquer uma."""
        return self.raio_deslocamento_km is None or distancia_km <= self.raio_deslocamento_km
