from flask import Flask

from bicus.config import Config
from bicus.extensions import db, migrate


def create_app(config: type[Config] = Config) -> Flask:
    app = Flask(__name__, template_folder="views")
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from bicus import models  # noqa: F401  (registra os modelos para as migrações)
    from bicus.controllers import registrar_blueprints
    from bicus.seeds import registrar_comandos

    registrar_blueprints(app)
    registrar_comandos(app)
    return app
