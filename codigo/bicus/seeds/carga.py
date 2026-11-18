from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select

from bicus.extensions import db
from bicus.models import Categoria, Prestador, Servico, Usuario
from bicus.seeds.dados_simulados import BAIRROS, CLIENTES, PRESTADORES


def carregar_dados(hoje: date) -> bool:
    if db.session.scalar(select(Usuario).limit(1)) is not None:
        return False

    # As categorias já existem: são criadas pela migração (dados de referência, NF20.4).
    categorias = {categoria.nome: categoria for categoria in db.session.scalars(select(Categoria))}
    db.session.add_all(_criar_usuario(dados) for dados in CLIENTES)
    db.session.add_all(_criar_prestador(dados, categorias, hoje) for dados in PRESTADORES)
    db.session.commit()
    return True


def _criar_usuario(dados: dict) -> Usuario:
    latitude, longitude = BAIRROS[dados["bairro"]]
    return Usuario(
        nome=dados["nome"],
        email=dados["email"],
        endereco=dados["endereco"],
        latitude=latitude,
        longitude=longitude,
    )


def _criar_prestador(dados: dict, categorias: dict[str, Categoria], hoje: date) -> Prestador:
    usuario = _criar_usuario(dados)
    inicio, fim = _periodo_indisponivel(dados.get("indisponivel_dias"), hoje)
    return Prestador(
        usuario=usuario,
        latitude_base=usuario.latitude,
        longitude_base=usuario.longitude,
        raio_deslocamento_km=dados["raio_km"],
        inicio_indisponibilidade=inicio,
        fim_indisponibilidade=fim,
        ativo=dados.get("ativo", True),
        nota_media=dados["nota"],
        total_avaliacoes=dados["avaliacoes"],
        servicos=[_criar_servico(servico, categorias) for servico in dados["servicos"]],
    )


def _criar_servico(dados: dict, categorias: dict[str, Categoria]) -> Servico:
    preco_minimo, preco_maximo = dados["preco"]
    return Servico(
        titulo=dados["titulo"],
        descricao=dados["descricao"],
        preco_minimo=Decimal(preco_minimo),
        preco_maximo=Decimal(preco_maximo),
        unidade_cobranca=dados["unidade"],
        ativo=dados.get("ativo", True),
        categoria=categorias[dados["categoria"]],
    )


def _periodo_indisponivel(
    dias: tuple[int, int] | None, hoje: date
) -> tuple[date | None, date | None]:
    if dias is None:
        return None, None
    inicio, fim = dias
    return hoje + timedelta(days=inicio), hoje + timedelta(days=fim)
