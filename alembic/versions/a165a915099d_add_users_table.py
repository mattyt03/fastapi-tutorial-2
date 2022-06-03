"""add users table

Revision ID: a165a915099d
Revises: 7cc2068e24e3
Create Date: 2022-06-02 22:16:34.041645

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a165a915099d'
down_revision = '7cc2068e24e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('email', sa.String(), nullable=False, unique=True),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), 
                              server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    op.drop_table('users')
