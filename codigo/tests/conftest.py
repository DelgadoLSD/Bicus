import pytest

from bicus import create_app
from bicus.config import TestConfig
from bicus.extensions import db as banco


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        banco.create_all()
        yield app
        banco.session.remove()
        banco.drop_all()


@pytest.fixture
def db(app):
    return banco


@pytest.fixture
def client(app):
    return app.test_client()
