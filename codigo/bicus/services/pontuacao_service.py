"""H04 (F9): pontuação de recomendação de um prestador numa busca.

pontuação = 0,6 x (nota / 5) + 0,4 x (1 - distância / raio da busca), de 0 a 1.
A nota vale até 0,6 e a proximidade até 0,4: a nota pesa mais (NF9.1).
"""

PESO_NOTA = 0.6
PESO_PROXIMIDADE = 0.4
NOTA_MAXIMA = 5.0
NOTA_SEM_AVALIACAO = 3.0  # neutra: quem ainda não foi avaliado não fica sempre em último


def calcular_pontuacao(nota_media: float | None, distancia_km: float, raio_km: float) -> float:
    nota = NOTA_SEM_AVALIACAO if nota_media is None else nota_media
    proximidade = 1 - distancia_km / raio_km
    return PESO_NOTA * nota / NOTA_MAXIMA + PESO_PROXIMIDADE * proximidade
