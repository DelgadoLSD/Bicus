from datetime import date

import click
from flask import Flask

from bicus.seeds.carga import carregar_dados


def registrar_comandos(app: Flask) -> None:
    @app.cli.command("carregar-dados")
    def carregar_dados_comando() -> None:
        """Preenche o banco com os dados simulados (só se ele estiver vazio)."""
        if carregar_dados(date.today()):
            click.echo("Dados simulados carregados.")
        else:
            click.echo("O banco já tem dados; nada foi inserido.")
