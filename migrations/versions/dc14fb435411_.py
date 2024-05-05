"""empty message

Revision ID: dc14fb435411
Revises: 8e4979afaec7
Create Date: 2024-05-06 00:00:22.870911

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dc14fb435411'
down_revision = '8e4979afaec7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ledger_account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('label', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ledger_account', schema=None) as batch_op:
        batch_op.drop_column('label')

    # ### end Alembic commands ###
