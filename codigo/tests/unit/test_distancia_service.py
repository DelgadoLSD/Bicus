"""F7 / NF8.2: distância em linha reta entre dois pontos (fórmula de Haversine)."""

import pytest

from bicus.domain import Coordenada
from bicus.services.distancia_service import distancia_km

CENTRO = Coordenada(-20.7546, -42.8826)
UFV = Coordenada(-20.7615, -42.8690)


def test_mesmo_ponto_tem_distancia_zero():
    assert distancia_km(CENTRO, CENTRO) == 0


def test_um_grau_de_latitude_mede_cerca_de_111_km():
    assert distancia_km(Coordenada(0, 0), Coordenada(1, 0)) == pytest.approx(111.19, abs=0.01)


def test_distancia_entre_o_centro_e_a_ufv():
    assert distancia_km(CENTRO, UFV) == pytest.approx(1.6, abs=0.05)


def test_distancia_nao_depende_do_sentido():
    assert distancia_km(CENTRO, UFV) == pytest.approx(distancia_km(UFV, CENTRO))
