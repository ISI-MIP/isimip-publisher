import uuid

from sqlalchemy import Column, Text, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Dataset(Base):

    __tablename__ = 'datasets'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid.uuid4().hex)
    name = Column(Text, nullable=False)
    version = Column(String(8), nullable=False)
    attributes = Column(JSONB, nullable=False)

    files = relationship('File', back_populates='dataset')

    def __repr__(self):
        return str(self.id)


class File(Base):

    __tablename__ = 'files'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid.uuid4().hex)
    dataset_id = Column(UUID, ForeignKey('datasets.id'))
    name = Column(Text, nullable=False)
    version = Column(String(8), nullable=False)
    path = Column(Text, nullable=False)
    checksum = Column(Text, nullable=False)
    checksum_type = Column(Text, nullable=False)
    attributes = Column(JSONB, nullable=False)

    dataset = relationship('Dataset', back_populates='files')

    def __repr__(self):
        return str(self.id)
