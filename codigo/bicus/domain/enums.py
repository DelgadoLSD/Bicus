from enum import Enum


class Turno(Enum):
    MANHA = "manhã"
    TARDE = "tarde"
    NOITE = "noite"


class EstadoSolicitacao(Enum):
    PENDENTE = "pendente"
    ACEITA = "aceita"
    RECUSADA = "recusada"
    EXPIRADA = "expirada"
    CANCELADA = "cancelada"
    CONCLUIDA = "concluída"


class UnidadeCobranca(Enum):
    HORA = "hora"
    DIARIA = "diária"
    SERVICO = "serviço"


class OrdemBusca(Enum):
    """Ordem da lista da busca escolhida pelo cliente (NF8.8); o valor vai no endereço (?ordem=)."""

    RECOMENDACAO = "recomendacao"
    AVALIACAO = "avaliacao"
    DISTANCIA = "distancia"
    PRECO = "preco"
