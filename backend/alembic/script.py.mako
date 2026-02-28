"""Mako template for Alembic migration scripts"""
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma-separated}
Create Date: ${create_date}
Upgrade from ${down_revision | comma-separated

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}


def upgrade():
    ${upgrades if upgrades else "pass"}


def downgrade():
    ${downgrades if downgrades else "pass"}
