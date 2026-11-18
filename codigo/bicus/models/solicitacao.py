from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bicus.domain import EstadoSolicitacao, Turno
from bicus.extensions import db

if TYPE_CHECKING:
    from bicus.models.servico import Servico
    from bicus.models.usuario import Usuario


class Solicitacao(db.Model):
    __tablename__ = "solicitacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    descricao: Mapped[str] = mapped_column(Text)
    data_desejada: Mapped[date]
    turno: Mapped[Turno] = mapped_column(Enum(Turno, native_enum=False, length=20))
    endereco: Mapped[str] = mapped_column(String(255))
    estado: Mapped[EstadoSolicitacao] = mapped_column(
        Enum(EstadoSolicitacao, native_enum=False, length=20),
        default=EstadoSolicitacao.PENDENTE,
    )
    data_criacao: Mapped[datetime] = mapped_column(server_default=func.now())
    cliente_id: Mapped[int] = mapped_column(ForeignKey("usuario.id"))
    servico_id: Mapped[int] = mapped_column(ForeignKey("servico.id"))

    cliente: Mapped[Usuario] = relationship(back_populates="solicitacoes")
    servico: Mapped[Servico] = relationship()

    def pode_cancelar(self) -> bool:
        return self.estado == EstadoSolicitacao.PENDENTE
