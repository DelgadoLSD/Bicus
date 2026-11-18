from flask import Blueprint

bp = Blueprint("saude", __name__)


@bp.get("/saude")
def saude():
    return {"status": "ok"}
