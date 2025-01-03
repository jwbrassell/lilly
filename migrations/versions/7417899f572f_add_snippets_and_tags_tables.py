"""Add snippets and tags tables

Revision ID: 7417899f572f
Revises: fc7f717e9465
Create Date: 2024-12-30 10:35:21.139694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7417899f572f'
down_revision = 'fc7f717e9465'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('snippet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('command', sa.Text(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('usage_notes', sa.Text(), nullable=True),
    sa.Column('example', sa.Text(), nullable=True),
    sa.Column('expected_output', sa.Text(), nullable=True),
    sa.Column('failure_scenarios', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('snippet_tags',
    sa.Column('snippet_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['snippet_id'], ['snippet.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('snippet_id', 'tag_id')
    )
    op.drop_table('host')
    op.drop_table('note')
    op.drop_table('git_repo')
    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.drop_index('ix_certificates_domain')
        batch_op.drop_index('ix_certificates_expiry_date')

    op.drop_table('certificates')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('certificates',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('domain', sa.VARCHAR(length=255), nullable=False),
    sa.Column('private_key', sa.TEXT(), nullable=False),
    sa.Column('certificate', sa.TEXT(), nullable=False),
    sa.Column('chain', sa.TEXT(), nullable=True),
    sa.Column('issuer', sa.VARCHAR(length=255), nullable=True),
    sa.Column('expiry_date', sa.DATETIME(), nullable=True),
    sa.Column('status', sa.VARCHAR(length=20), nullable=True),
    sa.Column('notes', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('updated_at', sa.DATETIME(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('certificates', schema=None) as batch_op:
        batch_op.create_index('ix_certificates_expiry_date', ['expiry_date'], unique=False)
        batch_op.create_index('ix_certificates_domain', ['domain'], unique=False)

    op.create_table('git_repo',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=200), nullable=False),
    sa.Column('url', sa.VARCHAR(length=500), nullable=False),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('note',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=200), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.Column('updated_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('host',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('hostname', sa.VARCHAR(length=200), nullable=False),
    sa.Column('ip_address', sa.VARCHAR(length=45), nullable=False),
    sa.Column('username', sa.VARCHAR(length=100), nullable=True),
    sa.Column('description', sa.TEXT(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('snippet_tags')
    op.drop_table('tag')
    op.drop_table('snippet')
    # ### end Alembic commands ###
