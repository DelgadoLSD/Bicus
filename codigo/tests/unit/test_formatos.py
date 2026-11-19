"""Números exibidos nas páginas no formato brasileiro (NF8.4: preço, nota e distância)."""

from decimal import Decimal

from bicus.formatos import dinheiro, numero


def test_numero_usa_virgula_nos_decimais():
    assert numero(3.7) == "3,7"


def test_numero_separa_os_milhares_com_ponto():
    assert numero(1234.5, casas=2) == "1.234,50"


def test_dinheiro_no_formato_brasileiro():
    assert dinheiro(Decimal("100")) == "R$ 100,00"
    assert dinheiro(Decimal("1500.5")) == "R$ 1.500,50"
