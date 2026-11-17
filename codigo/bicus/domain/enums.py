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
