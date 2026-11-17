from flask import Blueprint, render_template

from bicus.controllers.sessao import usuario_obrigatorio

bp = Blueprint("busca", __name__, url_prefix="/busca")


@bp.get("")
@usuario_obrigatorio
def buscar():
    return render_template("busca/index.html")
