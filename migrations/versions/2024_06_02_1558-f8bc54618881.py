"""empty message

Revision ID: f8bc54618881
Revises: 000000000000
Create Date: 2024-06-02 15:58:29.242458+00:00
"""

import sqlalchemy as sa
from alembic import op


revision = "f8bc54618881"
down_revision = "000000000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=256), nullable=False),
        sa.Column("password_hash", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_users_email", "users", [sa.text("lower(email)")], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("user_ip", sa.String(length=128), nullable=True),
        sa.Column("user_agent", sa.String(length=256), nullable=True),
        sa.Column("fingerprint", sa.String(length=128), nullable=False),
        sa.Column("access_token", sa.Uuid(), nullable=True),
        sa.Column("refresh_token", sa.Uuid(), nullable=True),
        sa.Column("expires_in", sa.Integer(), nullable=False),
        sa.Column("last_online", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("access_token"),
        sa.UniqueConstraint("refresh_token"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("auth_sessions")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index("idx_users_email", table_name="users")
    op.drop_table("users")
