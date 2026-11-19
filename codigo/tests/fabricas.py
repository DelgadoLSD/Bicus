"""Cria no banco de teste só o que cada teste precisa (os dados simulados não são usados)."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from bicus.domain import Coordenada, Turno, UnidadeCobranca
from bicus.extensions import db
from bicus.models import Categoria, Prestador, Servico, Solicitacao, Usuario

CENTRO = Coordenada(-20.7546, -42.8826)


def criar_usuario(nome: str, local: Coordenada = CENTRO) -> Usuario:
    usuario = Usuario(
        nome=nome,
        email=f"{nome.lower()}@teste.dev",
        endereco=f"Rua de {nome}, 1",
        latitude=local.latitude,
        longitude=local.longitude,
    )
    db.session.add(usuario)
    db.session.commit()
    return usuario


def criar_prestador(nome: str, local: Coordenada = CENTRO, **campos) -> Prestador:
    """Usuário com perfil de prestador; `campos` troca os valores padrão (raio, nota, ativo...)."""
    valores = {"raio_deslocamento_km": 10.0, "nota_media": 4.5, "total_avaliacoes": 10, **campos}
    prestador = Prestador(
        usuario=criar_usuario(nome, local),
        latitude_base=local.latitude,
        longitude_base=local.longitude,
        **valores,
    )
    db.session.add(prestador)
    db.session.commit()
    return prestador


def criar_servico(prestador: Prestador, categoria: str = "Faxina", **campos) -> Servico:
    """Serviço do prestador na categoria; `campos` troca os valores padrão (ativo, preço...)."""
    valores = {
        "titulo": f"{categoria} com {prestador.usuario.nome}",
        "descricao": "Serviço de teste.",
        "preco_minimo": Decimal(100),
        "preco_maximo": Decimal(150),
        "unidade_cobranca": UnidadeCobranca.DIARIA,
        **campos,
    }
    servico = Servico(prestador=prestador, categoria=_categoria(categoria), **valores)
    db.session.add(servico)
    db.session.commit()
    return servico


def nova_solicitacao(cliente: Usuario, servico: Servico, **campos) -> Solicitacao:
    """Grava a solicitação direto no banco, sem passar pelas regras da H01, em qualquer estado;
    `campos` troca os valores padrão (estado, data_criacao, data_desejada...)."""
    valores = {
        "descricao": "Pedido de teste.",
        "data_desejada": date(2026, 11, 30),
        "turno": Turno.MANHA,
        "endereco": cliente.endereco,
        **campos,
    }
    solicitacao = Solicitacao(cliente=cliente, servico=servico, **valores)
    db.session.add(solicitacao)
    db.session.commit()
    return solicitacao


def _categoria(nome: str) -> Categoria:
    existente = db.session.scalar(select(Categoria).where(Categoria.nome == nome))
    return existente or Categoria(nome=nome)
