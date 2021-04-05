"""create answers table

Revision ID: 55b76cb82606
Revises: 4ef2b8c361e8
Create Date: 2021-04-05 21:06:58.909196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55b76cb82606'
down_revision = '4ef2b8c361e8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_question', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(length=256), nullable=False),
    sa.Column('is_true', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['id_question'], ['question.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('question', 'is_true')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('is_true', sa.BOOLEAN(), nullable=True))
    op.drop_table('answer')
    # ### end Alembic commands ###
