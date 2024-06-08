"""empty message

Revision ID: 44fa8442ceeb
Revises: 000000000000
Create Date: 2024-06-08 09:20:06.195979+00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '44fa8442ceeb'
down_revision = '000000000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=256), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_email', 'users', [sa.text('lower(email)')], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_table('auth_sessions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('user_ip', sa.String(length=128), nullable=False),
    sa.Column('user_agent', sa.String(length=256), nullable=True),
    sa.Column('fingerprint', sa.String(length=128), nullable=False),
    sa.Column('access_token', sa.Uuid(), nullable=True),
    sa.Column('refresh_token', sa.Uuid(), nullable=True),
    sa.Column('expires_in', sa.Integer(), nullable=False),
    sa.Column('last_online', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('access_token'),
    sa.UniqueConstraint('refresh_token')
    )
    op.create_table('folders',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('owner_user_id', sa.Integer(), nullable=False),
    sa.Column('parent_folder_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['parent_folder_id'], ['folders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('records',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('owner_user_id', sa.Integer(), nullable=False),
    sa.Column('folder_id', sa.Integer(), nullable=True),
    sa.Column('record_type', sa.Enum('note', 'login', 'card', name='recordtype'), nullable=False),
    sa.Column('title', sa.String(length=128), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('is_favorite', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['folder_id'], ['folders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('records')
    op.drop_table('folders')
    op.drop_table('auth_sessions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
