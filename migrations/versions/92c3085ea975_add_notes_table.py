"""Add notes table

Revision ID: 92c3085ea975
Revises: 3cfeebe9acc3
Create Date: 2024-12-30 13:55:38.898364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92c3085ea975'
down_revision = '3cfeebe9acc3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('note')
    # ### end Alembic commands ###