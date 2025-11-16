"""Add user profile fields

Revision ID: 1e1ea79a3f5c
Revises: 7d21f02eb495
Create Date: 2025-11-16 11:50:13.666169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e1ea79a3f5c'
down_revision = '7d21f02eb495'
branch_labels = None
depends_on = None


def upgrade():
    # Додаємо нові поля до таблиці users
    op.add_column('users', sa.Column('birth_date', sa.Date(), nullable=True), schema='brama')
    op.add_column('users', sa.Column('specialty', sa.String(length=128), nullable=True), schema='brama')
    op.add_column('users', sa.Column('join_goal', sa.Text(), nullable=True), schema='brama')
    op.add_column('users', sa.Column('can_help', sa.Text(), nullable=True), schema='brama')
    op.add_column('users', sa.Column('want_to_do', sa.Text(), nullable=True), schema='brama')
    op.add_column('users', sa.Column('consent_given', sa.Boolean(), server_default='false', nullable=False), schema='brama')
    op.add_column('users', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True), schema='brama')
    op.add_column('users', sa.Column('profile_photo_url', sa.String(length=255), nullable=True), schema='brama')


def downgrade():
    # Видаляємо додані поля
    op.drop_column('users', 'profile_photo_url', schema='brama')
    op.drop_column('users', 'created_at', schema='brama')
    op.drop_column('users', 'consent_given', schema='brama')
    op.drop_column('users', 'want_to_do', schema='brama')
    op.drop_column('users', 'can_help', schema='brama')
    op.drop_column('users', 'join_goal', schema='brama')
    op.drop_column('users', 'specialty', schema='brama')
    op.drop_column('users', 'birth_date', schema='brama')
