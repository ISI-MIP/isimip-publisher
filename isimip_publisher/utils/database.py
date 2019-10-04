import logging
import os
import uuid

from sqlalchemy import Column, ForeignKey, String, Text, Index, create_engine, func
from sqlalchemy.dialects.postgresql import JSONB, UUID, TSVECTOR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import ProgrammingError

from . import order_dict
from .checksum import get_checksum, get_checksum_type

logger = logging.getLogger(__name__)

Base = declarative_base()


class Dataset(Base):

    __tablename__ = 'datasets'
    __table_args__ = (
        Index('datasets_search_vector_idx', 'search_vector', postgresql_using='gin'),
    )

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid.uuid4().hex)
    name = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)
    attributes = Column(JSONB, nullable=False)
    search_vector = Column(TSVECTOR, nullable=False)

    files = relationship('File', back_populates='dataset')

    def __repr__(self):
        return str(self.id)


class File(Base):

    __tablename__ = 'files'
    __table_args__ = (
        Index('files_search_vector_idx', 'search_vector', postgresql_using='gin'),
    )

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid.uuid4().hex)
    dataset_id = Column(UUID, ForeignKey('datasets.id'))
    name = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)
    checksum = Column(Text, nullable=False)
    checksum_type = Column(Text, nullable=False)
    attributes = Column(JSONB, nullable=False)
    search_vector = Column(TSVECTOR, nullable=False)

    dataset = relationship('Dataset', back_populates='files')

    def __repr__(self):
        return str(self.id)


def create_search_vector(config, name, attributes):
    vector = func.setweight(func.to_tsvector(name), 'B')

    for key in config['database_metadata_search']:
        vector = vector.concat(func.setweight(func.to_tsvector(attributes[key]), 'A'))

    return vector


def init_database_session():
    engine = create_engine(os.getenv('DATABASE'))

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    return Session()


def insert_dataset(session, version, config, dataset_path, dataset_name, metadata):
    attributes = order_dict(metadata)
    search_vector = create_search_vector(config, dataset_name, attributes)

    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        if dataset.attributes != attributes:
            dataset.attributes = attributes
            dataset.search_vector = search_vector
            logger.debug('update dataset %s', dataset_path)
        else:
            logger.debug('skip dataset %s', dataset_path)
    else:
        # insert a new row for this dataset
        logger.debug('insert dataset %s', dataset_path)
        dataset = Dataset(
            name=dataset_name,
            path=dataset_path,
            version=version,
            attributes=attributes,
            search_vector=search_vector
        )
        session.add(dataset)


def insert_file(session, version, config, file_path, file_abspath, file_name, dataset_path, metadata):
    checksum = get_checksum(file_abspath)
    checksum_type = get_checksum_type()
    attributes = order_dict(metadata)
    search_vector = create_search_vector(config, file_name, attributes)

    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError('No dataset with the name %s and the version %s found' % (dataset_path, version))

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == file_path,
        File.version == version
    ).one_or_none()

    if file:
        if file.checksum == checksum:
            # the file has not changed
            if file.attributes != attributes:
                file.attributes = attributes
                file.search_vector = search_vector
                logger.debug('update file %s', file_path)
            else:
                logger.debug('skip file %s', file_path)

        else:
            # the file has been changed, but the version is the same, this is not ok
            raise RuntimeError('%s has been changed but the version is the same' % file_path)
    else:
        # insert a new row for this file
        logger.debug('insert file %s', file_path)
        file = File(
            name=file_name,
            version=version,
            path=file_path,
            checksum=checksum,
            checksum_type=checksum_type,
            attributes=attributes,
            dataset=dataset,
            search_vector=search_vector
        )
        session.add(file)


def update_words_view(session):
    try:
        session.connection().execute('''
            CREATE MATERIALIZED VIEW words AS SELECT word FROM ts_stat('SELECT search_vector FROM datasets')
        ''')
        session.connection().execute('''
            CREATE INDEX ON words USING gin(word gin_trgm_ops)
        ''')
    except ProgrammingError:
        session.rollback()
        session.connection().execute('''
            REFRESH MATERIALIZED VIEW words
        ''')
