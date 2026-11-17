from flask import Blueprint, render_template

from bicus.controllers.sessao import usuario_obrigatorio

bp = Blueprint("solicitacoes", __name__, url_prefix="/solicitacoes")


@bp.route("/nova/<int:servico_id>", methods=["GET", "POST"])
@usuario_obrigatorio
def nova(servico_id: int):
    return render_template("solicitacoes/nova.html", servico_id=servico_id)


@bp.get("")
@usuario_obrigatorio
def listar():
    return render_template("solicitacoes/lista.html")
