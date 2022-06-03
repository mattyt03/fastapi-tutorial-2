"""add foreign key to posts table

Revision ID: 8f8bfcda1d3e
Revises: a165a915099d
Create Date: 2022-06-02 22:36:47.812181

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f8bfcda1d3e'
down_revision = 'a165a915099d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('owner_id', sa.Integer(), 
                  sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False))


def downgrade() -> None:
    op.drop_column('posts', 'owner_id')
