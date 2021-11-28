from sqlalchemy import Column, DateTime, MetaData, String, Table
from sqlalchemy.dialects.postgresql import UUID

metadata = MetaData()


t_lesson_learnt_report = Table(
    'lesson_learnt_report', metadata,
    Column('id', UUID, nullable=False),
    Column('title', String(500), nullable=False),
    Column('description', String(6000), nullable=False),
    Column('submitted_at', DateTime, nullable=False),
    Column('issue_id', UUID, nullable=False),
    Column('ref', String(6000), nullable=False)
)