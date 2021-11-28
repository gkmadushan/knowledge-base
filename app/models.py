from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, text, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Frequency(Base):
    __tablename__ = 'frequency'

    id = Column(UUID, primary_key=True)
    name = Column(String(250), nullable=False)
    code = Column(String(250), nullable=False)


class Schedule(Base):
    __tablename__ = 'schedule'

    id = Column(UUID, primary_key=True)
    start = Column(Time, nullable=False)
    terminate = Column(Time, nullable=False)
    active = Column(Boolean, nullable=False, server_default=text("false"))
    frequency = Column(ForeignKey('frequency.id'), nullable=False)
    reference = Column(UUID, nullable=True)
    last_check = Column(DateTime, nullable=True)

    frequency1 = relationship('Frequency')