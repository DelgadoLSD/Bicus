from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from bicus.controllers.sessao_controller import usuario_logado, usuario_obrigatorio
from bicus.domain import Turno
from bicus.extensions import db
from bicus.models import Servico
from bicus.models.solicitacao import Solicitacao
from bicus.services.solicitacoes_service import (
    SolicitacaoInvalidaError,
    cancelar_solicitacao,
    listar_solicitacoes,
)

bp = Blueprint("solicitacoes", __name__, url_prefix="/solicitacoes")

@bp.get("")
@usuario_obrigatorio
def listar():
    servico_id = request.args.get("servico", type=int)
    return render_template(
        "solicitacoes/lista.html",
        solicitacoes=listar_solicitacoes(usuario_logado()),
        servico=db.session.get(Servico, servico_id) if servico_id else None,
        turnos=list(Turno),
        hoje=date.today(),
    )

@bp.post("")
@usuario_obrigatorio
def criar():
    solicitacao = Solicitacao(
        cliente = usuario_logado(),
        servico_id = request.form.get("servico_id", type=int),
        descricao = request.form.get("descricao"),
        data_desejada = request.form.get("data_desejada", type=date.fromisoformat),
        turno = Turno[request.form["turno"]],
        endereco = request.form.get("endereco"),
    )
    db.session.add(solicitacao)
    db.session.commit()
    flash("Solicitação enviada.", "sucesso")
    return redirect(url_for("solicitacoes.listar"))


@bp.post("/<int:solicitacao_id>/cancelar")
@usuario_obrigatorio
def cancelar(solicitacao_id: int):
    try:
        cancelar_solicitacao(usuario_logado(), solicitacao_id)
    except SolicitacaoInvalidaError as erro:
        flash(str(erro), "erro")
    else:
        flash("Solicitação cancelada.", "sucesso")
    return redirect(url_for("solicitacoes.listar"))
