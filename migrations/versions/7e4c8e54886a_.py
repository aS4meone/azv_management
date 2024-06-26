"""empty message

Revision ID: 7e4c8e54886a
Revises: 9eec1863bde1
Create Date: 2024-03-26 23:32:46.068071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e4c8e54886a'
down_revision: Union[str, None] = '9eec1863bde1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('before_change', sa.Text(), nullable=True))
    op.add_column('history', sa.Column('after_change', sa.Text(), nullable=True))
    op.drop_column('history', 'items')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('history', sa.Column('items', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('history', 'after_change')
    op.drop_column('history', 'before_change')
    # ### end Alembic commands ###
