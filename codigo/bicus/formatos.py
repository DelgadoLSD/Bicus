"""Formatos de exibição usados nas páginas: números no padrão brasileiro.

Registrados como filtros do Jinja, por exemplo: {{ distancia|numero }} km, {{ preco|dinheiro }}.
"""

from decimal import Decimal

from flask import Flask


def numero(valor: float | Decimal, casas: int = 1) -> str:
    """3.7 -> '3,7'; 1234.5 com 2 casas -> '1.234,50'."""
    americano = f"{valor:,.{casas}f}"
    return americano.translate(str.maketrans(",.", ".,"))


def dinheiro(valor: float | Decimal) -> str:
    """Decimal('100') -> 'R$ 100,00'."""
    return f"R$ {numero(valor, casas=2)}"


def registrar_formatos(app: Flask) -> None:
    app.add_template_filter(numero)
    app.add_template_filter(dinheiro)
