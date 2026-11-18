from flask import Blueprint, render_template, request
from sqlalchemy import select

from bicus.controllers.sessao_controller import usuario_logado, usuario_obrigatorio
from bicus.extensions import db
from bicus.models import Categoria
from bicus.services.busca_service import buscar_prestadores

bp = Blueprint("busca", __name__, url_prefix="/busca")


@bp.get("")
@usuario_obrigatorio
def buscar():
    categorias = db.session.scalars(
        select(Categoria).where(Categoria.ativa).order_by(Categoria.nome)
    ).all()
    categoria_id = request.args.get("categoria", type=int)
    raio = request.args.get("raio", type=float)

    resultados = []
    if categoria_id and raio:
        resultados = buscar_prestadores(categoria_id, usuario_logado(), raio)

    return render_template(
        "busca/index.html",
        categorias=categorias,
        categoria_id=categoria_id,
        raio=raio,
        resultados=resultados,
    )
