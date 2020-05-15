import logging
import mimetypes
import os
import uuid

from sqlalchemy import (Boolean, Column, ForeignKey, Index, String, Text,
                        create_engine, func, inspect)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from .checksum import (get_checksum_type, get_dataset_checksum,
                       get_file_checksum)

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_search_vector(config, path):
    search_string = path.replace('_', ' ').replace('-', ' ').replace('/', ' ')
    return func.setweight(func.to_tsvector(search_string), 'A')


class Dataset(Base):

    __tablename__ = 'datasets'
    __table_args__ = (
        Index('datasets_search_vector_idx', 'search_vector', postgresql_using='gin'),
    )

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid.uuid4().hex)
    name = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)
    checksum = Column(Text, nullable=False)
    checksum_type = Column(Text, nullable=False)
    attributes = Column(JSONB, nullable=False)
    search_vector = Column(TSVECTOR, nullable=False)
    public = Column(Boolean, nullable=False)

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
    mime_type = Column(Text, nullable=False)
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
    return session


def insert_dataset(session, version, config, dataset, attributes):
    dataset_name = str(dataset['name'])
    dataset_path = str(dataset['path'])
    checksum = get_dataset_checksum(dataset)
    checksum_type = get_checksum_type()
    search_vector = get_search_vector(config, dataset_path)

    logger.info('insert_dataset %s', dataset_path)

    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        if dataset.checksum == checksum:
            # if the dataset already exists, update its attributes
            if dataset.attributes != attributes:
                dataset.attributes = attributes
                dataset.search_vector = search_vector
                logger.debug('update dataset %s', dataset_path)
            else:
                logger.debug('skip dataset %s', dataset_path)

        else:
            # the file has been changed, but the version is the same, this is not ok
            raise RuntimeError('%s has been changed but the version is the same' % dataset_path)
    else:
        # insert a new row for this dataset
        logger.debug('insert dataset %s', dataset_path)
        dataset = Dataset(
            name=dataset_name,
            path=dataset_path,
            version=version,
            checksum=checksum,
            checksum_type=checksum_type,
            attributes=attributes,
            search_vector=search_vector,
            public=False
        )
        session.add(dataset)


def publish_dataset(session, version, dataset):
    dataset_path = str(dataset['path'])

    # check that there is no public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.public == True
    ).one_or_none()

    if public_dataset and public_dataset.version != version:
        raise RuntimeError('A public dataset with the path %s and the version %s was found' %
                           (dataset_path, public_dataset.version))

    # mark this dataset public
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError('No dataset with the name %s and the version %s found' %
                           (dataset_path, public_dataset.version))

    dataset.public = True


def unpublish_dataset(session, dataset):
    dataset_path = str(dataset['path'])

    # find the public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.public == True
    ).one_or_none()

    if public_dataset:
        public_dataset.public = False
        return public_dataset.version


def insert_file(session, version, config, file, attributes):
    file_name = str(file['name'])
    file_path = str(file['path'])
    dataset_path = str(file['dataset_path'])
    checksum = get_file_checksum(file)
    checksum_type = get_checksum_type()
    mime_type, _ = mimetypes.guess_type(file['abspath'])
    search_vector = get_search_vector(config, file_path)

    logger.info('insert_file %s', file_path)

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
            mime_type=mime_type,
            attributes=attributes,
            dataset=dataset,
            search_vector=search_vector
        )
        session.add(file)


def update_words_view(session):
    engine = session.get_bind()
    if 'words' in inspect(engine).get_view_names():
        session.connection().execute('''
            REFRESH MATERIALIZED VIEW words
        ''')
        logger.debug('update words view')
    else:
        session.connection().execute('''
            CREATE MATERIALIZED VIEW words AS SELECT word FROM ts_stat('SELECT search_vector FROM public.datasets')
        ''')
        session.connection().execute('''
            CREATE INDEX ON words USING gin(word gin_trgm_ops)
        ''')
        logger.debug('create words view')


def update_attributes_view(session):
    engine = session.get_bind()
    if 'attributes' in inspect(engine).get_view_names():
        session.connection().execute('''
            REFRESH MATERIALIZED VIEW attributes
        ''')
        logger.debug('update attributes view')
    else:
        session.connection().execute('''
            CREATE MATERIALIZED VIEW attributes AS SELECT DISTINCT jsonb_object_keys(attributes) AS key FROM public.datasets
        ''')
        session.connection().execute('''
            CREATE INDEX ON attributes(key)
        ''')
        logger.debug('create attributes view')
