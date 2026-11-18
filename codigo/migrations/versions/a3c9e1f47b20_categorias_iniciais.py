"""categorias iniciais (NF20.4)

Revision ID: a3c9e1f47b20
Revises: 5f79808c2d75
Create Date: 2026-11-17 22:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a3c9e1f47b20'
down_revision = '5f79808c2d75'
branch_labels = None
depends_on = None

# Dados de referência: o sistema precisa deles em qualquer ambiente (local, CI e produção),
# independente dos dados simulados do seed. A lista fica congelada aqui, como o resto da
# migração; categorias novas entram por uma migração nova ou pela administração (F20).
CATEGORIAS = [
    "Jardinagem",
    "Aulas particulares",
    "Pequenos reparos domésticos",
    "Faxina",
    "Pintura",
    "Montagem de móveis",
    "Cuidado de animais",
]

categoria = sa.table(
    "categoria",
    sa.column("id", sa.Integer),
    sa.column("nome", sa.String),
    sa.column("ativa", sa.Boolean),
)
servico = sa.table("servico", sa.column("categoria_id", sa.Integer))


def upgrade():
    # Só insere as que faltam: bancos criados antes desta migração já têm as categorias do seed.
    existentes = set(op.get_bind().scalars(sa.select(categoria.c.nome)))
    novas = [{"nome": nome, "ativa": True} for nome in CATEGORIAS if nome not in existentes]
    if novas:
        op.bulk_insert(categoria, novas)


def downgrade():
    # Remove só as categorias que nenhum serviço usa, para não quebrar as chaves estrangeiras.
    em_uso = sa.select(servico.c.categoria_id)
    op.execute(
        categoria.delete().where(
            categoria.c.nome.in_(CATEGORIAS), categoria.c.id.not_in(em_uso)
        )
    )
