from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.datastructures import MultiDict

from bicus.controllers.sessao_controller import usuario_logado, usuario_obrigatorio
from bicus.domain import Turno
from bicus.extensions import db
from bicus.models import Servico
from bicus.services.solicitacoes_service import (
    DadosSolicitacao,
    SolicitacaoInvalidaError,
    cancelar_solicitacao,
    criar_solicitacao,
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
    dados = _dados_do_formulario(request.form)
    try:
        criar_solicitacao(usuario_logado(), dados, date.today())
    except SolicitacaoInvalidaError as erro:
        flash(str(erro), "erro")
        return redirect(url_for("solicitacoes.listar", servico=dados.servico_id))
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


def _dados_do_formulario(formulario: MultiDict) -> DadosSolicitacao:
    """Converte o formulário; o que vier vazio ou inválido vira None e a regra recusa."""
    return DadosSolicitacao(
        servico_id=formulario.get("servico_id", type=int),
        descricao=formulario.get("descricao", ""),
        data_desejada=formulario.get("data_desejada", type=date.fromisoformat),
        turno=Turno.__members__.get(formulario.get("turno", "")),
        endereco=formulario.get("endereco", ""),
    )
