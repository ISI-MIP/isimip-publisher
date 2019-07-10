import uuid

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class File(Base):

    __tablename__ = 'files'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid.uuid4().hex)
    name = Column(Text, nullable=False)
    path = Column(Text, nullable=False)
    checksum = Column(Text, nullable=False)
    attributes = Column(JSONB, nullable=False)

    def __repr__(self):
        return str(self.id)
