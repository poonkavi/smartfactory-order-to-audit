
"""Add dispatch tracking

Revision ID: 19dd5378fd50
Revises: 3b0ce46e7c47
"""

from alembic import op
import sqlalchemy as sa


revision = '19dd5378fd50'
down_revision = '3b0ce46e7c47'
branch_labels = None
depends_on = None


def upgrade():

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    existing_tables = inspector.get_table_names()

    # Remove the partially created empty dispatch table
    # from the earlier failed migration attempt
    if 'dispatch' in existing_tables:
        op.drop_table('dispatch')

    # Create the dispatch table without a unique constraint
    # on dispatch_number (one dispatch can have multiple items)
    op.create_table(
        'dispatch',

        sa.Column('id', sa.Integer(), primary_key=True),

        sa.Column(
            'dispatch_number',
            sa.String(50),
            nullable=False
        ),

        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('order_item_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('dispatch_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.String(200), nullable=True),

        sa.ForeignKeyConstraint(
            ['order_id'],
            ['order.id']
        ),

        sa.ForeignKeyConstraint(
            ['order_item_id'],
            ['order_item.id']
        ),

        sa.ForeignKeyConstraint(
            ['product_id'],
            ['product.id']
        )
    )

    # Add dispatched_quantity only if it doesn't already exist
    inspector = sa.inspect(op.get_bind())

    order_item_columns = [
        column['name']
        for column in inspector.get_columns('order_item')
    ]

    if 'dispatched_quantity' not in order_item_columns:

        with op.batch_alter_table('order_item') as batch_op:

            batch_op.add_column(
                sa.Column(
                    'dispatched_quantity',
                    sa.Integer(),
                    nullable=False,
                    server_default='0'
                )
            )


def downgrade():

    inspector = sa.inspect(op.get_bind())

    order_item_columns = [
        column['name']
        for column in inspector.get_columns('order_item')
    ]

    if 'dispatched_quantity' in order_item_columns:

        with op.batch_alter_table('order_item') as batch_op:
            batch_op.drop_column('dispatched_quantity')

    if 'dispatch' in inspector.get_table_names():
        op.drop_table('dispatch')
