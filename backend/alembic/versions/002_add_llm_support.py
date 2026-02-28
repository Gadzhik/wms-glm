"""Add LLM support: description and embedding fields to events

Revision ID: 002
Revises: 001
Create Date: 2026-02-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Добавить поддержку LLM: поля description и embedding"""
    
    # Включаем расширение pgvector (только для PostgreSQL)
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Добавляем поле description для LLM-генерированных описаний
    op.add_column(
        'events',
        sa.Column('description', sa.Text(), nullable=True)
    )
    
    # Добавляем поле embedding для семантического поиска
    # Для SQLite это будет просто TEXT, для PostgreSQL - VECTOR
    op.add_column(
        'events',
        sa.Column('embedding', postgresql.ARRAY(sa.Float), nullable=True)
    )
    
    # Создаём индекс для поиска по embedding (только PostgreSQL)
    # op.execute('CREATE INDEX idx_events_embedding ON events USING ivfflat (embedding vector_cosine_ops)')


def downgrade():
    """Удалить поддержку LLM"""
    
    # Удаляем индекс если есть
    # op.drop_index('idx_events_embedding', table_name='events')
    
    # Удаляем колонки
    op.drop_column('events', 'embedding')
    op.drop_column('events', 'description')
    
    # Отключаем расширение pgvector (осторожно - может быть использовано другими таблицами)
    # op.execute('DROP EXTENSION IF EXISTS vector')
