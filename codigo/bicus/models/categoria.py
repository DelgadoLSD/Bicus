from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bicus.extensions import db

if TYPE_CHECKING:
    from bicus.models.servico import Servico


class Categoria(db.Model):
    __tablename__ = "categoria"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(60), unique=True)
    ativa: Mapped[bool] = mapped_column(default=True)

    servicos: Mapped[list[Servico]] = relationship(back_populates="categoria")
