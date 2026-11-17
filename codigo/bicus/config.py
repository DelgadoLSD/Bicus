import os


def normalizar_url_banco(url: str) -> str:
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + url.removeprefix(prefixo)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-inseguro")
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(
        os.environ.get("DATABASE_URL", "sqlite:///bicus.db")
    )
    MODO_DEMO = os.environ.get("MODO_DEMO", "1") == "1"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = normalizar_url_banco(
        os.environ.get("TEST_DATABASE_URL", "sqlite:///:memory:")
    )
