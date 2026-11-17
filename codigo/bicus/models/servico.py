from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bicus.domain import UnidadeCobranca
from bicus.extensions import db

if TYPE_CHECKING:
    from bicus.models.categoria import Categoria
    from bicus.models.prestador import Prestador


class Servico(db.Model):
    __tablename__ = "servico"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(120))
    descricao: Mapped[str] = mapped_column(Text)
    preco_minimo: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    preco_maximo: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    unidade_cobranca: Mapped[UnidadeCobranca] = mapped_column(
        Enum(UnidadeCobranca, native_enum=False, length=20)
    )
    ativo: Mapped[bool] = mapped_column(default=True)
    prestador_id: Mapped[int] = mapped_column(ForeignKey("prestador.id"))
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categoria.id"))

    prestador: Mapped[Prestador] = relationship(back_populates="servicos")
    categoria: Mapped[Categoria] = relationship(back_populates="servicos")
