from flask import Flask

from bicus.controllers.busca import bp as busca_bp
from bicus.controllers.saude import bp as saude_bp
from bicus.controllers.sessao import bp as sessao_bp
from bicus.controllers.solicitacoes import bp as solicitacoes_bp


def registrar_blueprints(app: Flask) -> None:
    app.register_blueprint(saude_bp)
    app.register_blueprint(sessao_bp)
    app.register_blueprint(busca_bp)
    app.register_blueprint(solicitacoes_bp)
