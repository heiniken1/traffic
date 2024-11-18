from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b33a24f7369d'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('violation', schema=None) as batch_op:
        batch_op.add_column(sa.Column('added_by', sa.String(length=150), nullable=False, server_default='admin'))
        batch_op.add_column(sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()))

def downgrade():
    with op.batch_alter_table('violation', schema=None) as batch_op:
        batch_op.drop_column('added_by')
        batch_op.drop_column('is_deleted')