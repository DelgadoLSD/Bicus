from math import asin, cos, radians, sin, sqrt

from bicus.domain import Coordenada

RAIO_TERRA_KM = 6371.0


def distancia_km(origem: Coordenada, destino: Coordenada) -> float:
    """Distância em linha reta entre dois pontos, pela fórmula de Haversine (NF8.2)."""
    lat1, lon1 = radians(origem.latitude), radians(origem.longitude)
    lat2, lon2 = radians(destino.latitude), radians(destino.longitude)

    a = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * RAIO_TERRA_KM * asin(sqrt(a))
