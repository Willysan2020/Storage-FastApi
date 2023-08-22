"""update StoredFiles table add serversize

Revision ID: 63edef7d6463
Revises: f89d98403252
Create Date: 2023-06-02 00:17:28.030653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63edef7d6463'
down_revision = 'f89d98403252'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('storedfiles', sa.Column('serversize', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('storedfiles', 'serversize')
    # ### end Alembic commands ###
