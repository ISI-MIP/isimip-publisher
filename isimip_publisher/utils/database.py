import logging
import os
import uuid

from sqlalchemy import (Column, ForeignKey, Index, String, Text, create_engine,
                        func)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from .checksum import get_checksum, get_checksum_type

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_search_vector(config, attributes):
    search_vector = None

    for value in attributes.values():
        vector = func.setweight(func.to_tsvector(str(value)), 'A')

        if search_vector is None:
            search_vector = vector
        else:
            search_vector = search_vector.concat(vector)

    return search_vector


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


def init_database_session():
    engine = create_engine(os.getenv('DATABASE'))

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    session = Session()

    try:
        session.connection().execute('CREATE EXTENSION pg_trgm;')
    except ProgrammingError:
        session.rollback()

    return session


def insert_dataset(session, version, config, dataset_path, dataset_name, attributes):
    search_vector = get_search_vector(config, attributes)

    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        # if the dataset already exists, update its attributes
        if dataset.attributes != attributes:
            dataset.attributes = attributes
            dataset.search_vector = search_vector
            logger.info('update dataset %s', dataset_path)
        else:
            logger.info('skip dataset %s', dataset_path)
    else:
        # insert a new row for this dataset
        logger.info('insert dataset %s', dataset_path)
        dataset = Dataset(
            name=dataset_name,
            path=dataset_path,
            version=version,
            attributes=attributes,
            search_vector=search_vector
        )
        session.add(dataset)


def insert_file(session, version, config, file_path, file_abspath, file_name, dataset_path, attributes):
    checksum = get_checksum(file_abspath)
    checksum_type = get_checksum_type()
    search_vector = get_search_vector(config, attributes)

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
            # the file itself has not changed, update the attributes
            if file.attributes != attributes:
                file.attributes = attributes
                file.search_vector = search_vector
                logger.info('update file %s', file_path)
            else:
                logger.info('skip file %s', file_path)

        else:
            # the file has been changed, but the version is the same, this is not ok
            raise RuntimeError('%s has been changed but the version is the same' % file_path)
    else:
        # insert a new row for this file
        logger.info('insert file %s', file_path)
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


def update_latest_view(session):
    try:
        session.connection().execute('''
            CREATE MATERIALIZED VIEW latest AS
                SELECT d.id AS dataset_id, d.version FROM datasets AS d
                JOIN (
                    SELECT "path", MAX("version") AS version FROM datasets GROUP BY "path"
                ) AS l ON l.path = d.path AND l.version = d.version;
        ''')
        session.connection().execute('''
            CREATE INDEX ON latest(dataset_id)
        ''')
        logger.info('create latest view')
    except ProgrammingError:
        session.rollback()
        session.connection().execute('''
            REFRESH MATERIALIZED VIEW latest
        ''')
        logger.info('update latest view')


def update_words_view(session):
    try:
        session.connection().execute('''
            CREATE MATERIALIZED VIEW words AS SELECT word FROM ts_stat('SELECT search_vector FROM datasets')
        ''')
        session.connection().execute('''
            CREATE INDEX ON words USING gin(word gin_trgm_ops)
        ''')
        logger.info('create words view')
    except ProgrammingError:
        session.rollback()
        session.connection().execute('''
            REFRESH MATERIALIZED VIEW words
        ''')
        logger.info('update words view')


def update_attributes_view(session):
    try:
        session.connection().execute('''
            CREATE MATERIALIZED VIEW attributes AS SELECT DISTINCT jsonb_object_keys(attributes) AS key FROM datasets
        ''')
        session.connection().execute('''
            CREATE INDEX ON attributes(key)
        ''')
        logger.info('create attributes view')
    except ProgrammingError:
        session.rollback()
        session.connection().execute('''
            REFRESH MATERIALIZED VIEW attributes
        ''')
        logger.info('update attributes view')
