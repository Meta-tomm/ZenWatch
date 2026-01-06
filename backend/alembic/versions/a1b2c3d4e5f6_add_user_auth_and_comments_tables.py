"""add user auth and comments tables

Revision ID: a1b2c3d4e5f6
Revises: 957bd231a672
Create Date: 2026-01-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ARRAY


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '957bd231a672'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('bio', sa.String(500), nullable=True),
        sa.Column('github_url', sa.Text(), nullable=True),
        sa.Column('portfolio_url', sa.Text(), nullable=True),
        sa.Column('role', sa.String(20), server_default='user', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.CheckConstraint("role IN ('user', 'admin')", name='ck_users_role')
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])

    op.create_table(
        'oauth_accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(20), nullable=False),
        sa.Column('provider_user_id', sa.String(255), nullable=False),
        sa.Column('provider_email', sa.String(255), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.CheckConstraint("provider IN ('github', 'google', 'discord')", name='ck_oauth_provider'),
        sa.UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_user')
    )
    op.create_index('idx_oauth_user_id', 'oauth_accounts', ['user_id'])

    op.create_table(
        'user_article_states',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_favorite', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint('user_id', 'article_id', name='uq_user_article')
    )
    op.create_index('idx_user_article_states_user', 'user_article_states', ['user_id'])
    op.create_index('idx_user_article_states_article', 'user_article_states', ['article_id'])

    op.create_table(
        'user_video_states',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('video_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_read', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('is_favorite', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.UniqueConstraint('user_id', 'video_id', name='uq_user_video')
    )
    op.create_index('idx_user_video_states_user', 'user_video_states', ['user_id'])
    op.create_index('idx_user_video_states_video', 'user_video_states', ['video_id'])

    op.create_table(
        'user_keywords',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('keyword', sa.String(100), nullable=False),
        sa.Column('weight', sa.Float(), server_default='1.0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'keyword', name='uq_user_keyword')
    )
    op.create_index('idx_user_keywords_user', 'user_keywords', ['user_id'])

    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=True),
        sa.Column('video_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), nullable=True),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('comments.id', ondelete='CASCADE'), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.CheckConstraint('article_id IS NOT NULL OR video_id IS NOT NULL', name='ck_comments_target')
    )
    op.create_index('idx_comments_article', 'comments', ['article_id'], postgresql_where=sa.text('article_id IS NOT NULL'))
    op.create_index('idx_comments_video', 'comments', ['video_id'], postgresql_where=sa.text('video_id IS NOT NULL'))
    op.create_index('idx_comments_parent', 'comments', ['parent_id'], postgresql_where=sa.text('parent_id IS NOT NULL'))
    op.create_index('idx_comments_user', 'comments', ['user_id'])

    op.create_table(
        'user_consents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('consent_type', sa.String(50), nullable=False),
        sa.Column('consented', sa.Boolean(), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('consented_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('withdrawn_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("consent_type IN ('terms', 'privacy', 'marketing', 'analytics')", name='ck_consent_type')
    )
    op.create_index('idx_user_consents_user', 'user_consents', ['user_id'])

    op.create_table(
        'data_export_requests',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('file_url', sa.Text(), nullable=True),
        sa.Column('requested_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending', 'processing', 'completed', 'expired')", name='ck_export_status')
    )
    op.create_index('idx_data_export_user', 'data_export_requests', ['user_id'])

    op.add_column('user_config', sa.Column('user_id', UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_user_config_user', 'user_config', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_unique_constraint('uq_user_config_user_id', 'user_config', ['user_id'])
    op.create_index('idx_user_config_user', 'user_config', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_user_config_user', 'user_config')
    op.drop_constraint('uq_user_config_user_id', 'user_config', type_='unique')
    op.drop_constraint('fk_user_config_user', 'user_config', type_='foreignkey')
    op.drop_column('user_config', 'user_id')

    op.drop_index('idx_data_export_user', 'data_export_requests')
    op.drop_table('data_export_requests')

    op.drop_index('idx_user_consents_user', 'user_consents')
    op.drop_table('user_consents')

    op.drop_index('idx_comments_user', 'comments')
    op.drop_index('idx_comments_parent', 'comments')
    op.drop_index('idx_comments_video', 'comments')
    op.drop_index('idx_comments_article', 'comments')
    op.drop_table('comments')

    op.drop_index('idx_user_keywords_user', 'user_keywords')
    op.drop_table('user_keywords')

    op.drop_index('idx_user_video_states_video', 'user_video_states')
    op.drop_index('idx_user_video_states_user', 'user_video_states')
    op.drop_table('user_video_states')

    op.drop_index('idx_user_article_states_article', 'user_article_states')
    op.drop_index('idx_user_article_states_user', 'user_article_states')
    op.drop_table('user_article_states')

    op.drop_index('idx_oauth_user_id', 'oauth_accounts')
    op.drop_table('oauth_accounts')

    op.drop_index('idx_users_username', 'users')
    op.drop_index('idx_users_email', 'users')
    op.drop_table('users')
