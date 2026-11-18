from flask import Flask

from bicus.controllers.busca_controller import bp as busca_bp
from bicus.controllers.saude_controller import bp as saude_bp
from bicus.controllers.sessao_controller import bp as sessao_bp
from bicus.controllers.solicitacoes_controller import bp as solicitacoes_bp


def registrar_blueprints(app: Flask) -> None:
    app.register_blueprint(saude_bp)
    app.register_blueprint(sessao_bp)
    app.register_blueprint(busca_bp)
    app.register_blueprint(solicitacoes_bp)
