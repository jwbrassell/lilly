"""Add Certificate model with metadata fields

Revision ID: fc7f717e9465
Revises: 03939640c2de
Create Date: 2024-12-30 10:20:34.586534

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc7f717e9465'
down_revision = '03939640c2de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('certificates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('domain', sa.String(length=255), nullable=False),
    sa.Column('private_key', sa.Text(), nullable=False),
    sa.Column('certificate', sa.Text(), nullable=False),
    sa.Column('chain', sa.Text(), nullable=True),
    sa.Column('issuer', sa.String(length=255), nullable=True),
    sa.Column('expiry_date', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_certificates_domain'), ['domain'], unique=False)
        batch_op.create_index(batch_op.f('ix_certificates_expiry_date'), ['expiry_date'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_certificates_expiry_date'))
        batch_op.drop_index(batch_op.f('ix_certificates_domain'))

    op.drop_table('certificates')
    # ### end Alembic commands ###