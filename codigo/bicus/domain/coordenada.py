from dataclasses import dataclass


@dataclass(frozen=True)
class Coordenada:
    latitude: float
    longitude: float
