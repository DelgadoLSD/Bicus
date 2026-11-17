from functools import wraps

from flask import (
    Blueprint,
    abort,
    current_app,
    redirect,
    render_template,
    session,
    url_for,
)
from sqlalchemy import select

from bicus.extensions import db
from bicus.models import Usuario

bp = Blueprint("sessao", __name__)


def usuario_logado() -> Usuario | None:
    usuario_id = session.get("usuario_id")
    if usuario_id is None:
        return None
    return db.session.get(Usuario, usuario_id)


def usuario_obrigatorio(view):
    @wraps(view)
    def view_protegida(*args, **kwargs):
        if usuario_logado() is None:
            return redirect(url_for("sessao.entrar"))
        return view(*args, **kwargs)

    return view_protegida


@bp.app_context_processor
def injetar_usuario_atual() -> dict:
    return {"usuario_atual": usuario_logado()}


@bp.before_request
def exigir_modo_demo() -> None:
    if not current_app.config["MODO_DEMO"]:
        abort(404)


@bp.get("/")
def inicio():
    if usuario_logado() is None:
        return redirect(url_for("sessao.entrar"))
    return redirect(url_for("busca.buscar"))


@bp.get("/entrar")
def entrar():
    usuarios = db.session.scalars(select(Usuario).order_by(Usuario.nome)).all()
    return render_template("sessao/entrar.html", usuarios=usuarios)


@bp.post("/entrar/<int:usuario_id>")
def entrar_como(usuario_id: int):
    usuario = db.get_or_404(Usuario, usuario_id)
    session["usuario_id"] = usuario.id
    return redirect(url_for("busca.buscar"))


@bp.post("/sair")
def sair():
    session.pop("usuario_id", None)
    return redirect(url_for("sessao.entrar"))
