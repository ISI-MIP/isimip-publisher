import logging
import os
import uuid

from sqlalchemy import (Boolean, Column, ForeignKey, Index, String, Table,
                        Text, create_engine, func, inspect)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_specifiers(attributes):
    return [str(value) for value in attributes.values()]


def get_search_vector(attributes):
    values = [str(value) for value in attributes.values()]
    search_string = ' '.join(values)
    return func.setweight(func.to_tsvector(search_string), 'A')


# association table between resources and datasets
resources_datasets = Table('resources_datasets', Base.metadata,
                           Column('resource_id', UUID, ForeignKey('resources.id')),
                           Column('dataset_id', UUID, ForeignKey('datasets.id')))


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
    specifiers = Column(ARRAY(Text), nullable=False)
    search_vector = Column(TSVECTOR, nullable=False)
    public = Column(Boolean, nullable=False)

    files = relationship('File', back_populates='dataset')
    resources = relationship('Resource', secondary=resources_datasets, back_populates='datasets')

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
    specifiers = Column(ARRAY(Text), nullable=False)
    search_vector = Column(TSVECTOR, nullable=False)

    dataset = relationship('Dataset', back_populates='files')

    def __repr__(self):
        return str(self.id)


class Resource(Base):

    __tablename__ = 'resources'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid.uuid4().hex)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)

    doi = Column(Text, nullable=False, index=True)
    datacite = Column(JSONB, nullable=False)

    datasets = relationship('Dataset', secondary=resources_datasets, back_populates='resources')

    def __repr__(self):
        return str(self.id)


def init_database_session():
    engine = create_engine(os.getenv('DATABASE'))

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def insert_dataset(session, version, name, path, checksum, checksum_type, attributes):
    logger.info('insert_dataset %s', path)

    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == str(path),
        Dataset.version == version
    ).one_or_none()

    if dataset:
        if dataset.checksum == checksum:
            # if the dataset already exists, update its specifiers or attributes
            if dataset.attributes != attributes:
                dataset.attributes = attributes
                dataset.specifiers = get_specifiers(attributes)
                dataset.search_vector = get_search_vector(attributes)
                logger.debug('update dataset %s', path)
            else:
                logger.debug('skip dataset %s', path)

        else:
            # the file has been changed, but the version is the same, this is not ok
            raise RuntimeError('%s has been changed but the version is the same' % path)
    else:
        # insert a new row for this dataset
        logger.debug('insert dataset %s', path)
        dataset = Dataset(
            name=name,
            path=str(path),
            version=version,
            checksum=checksum,
            checksum_type=checksum_type,
            attributes=attributes,
            specifiers=get_specifiers(attributes),
            search_vector=get_search_vector(attributes),
            public=False
        )
        session.add(dataset)


def publish_dataset(session, version, path):
    # check that there is no public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == str(path),
        Dataset.public == True
    ).one_or_none()

    if public_dataset and public_dataset.version != version:
        raise RuntimeError('A public dataset with the path %s and the version %s was found' %
                           (path, public_dataset.version))

    # mark this dataset public
    dataset = session.query(Dataset).filter(
        Dataset.path == str(path),
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError('No dataset with the name %s and the version %s found' %
                           (path, public_dataset.version))

    dataset.public = True


def unpublish_dataset(session, path):
    # find the public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == str(path),
        Dataset.public == True
    ).one_or_none()

    if public_dataset:
        public_dataset.public = False
        return public_dataset.version


def retrieve_datasets(session, path, public=None):
    like_path = '{}%'.format(path)

    if public is None:
        datasets = session.query(Dataset).filter(
            Dataset.path.like(like_path),
        ).all()
    else:
        datasets = session.query(Dataset).filter(
            Dataset.path.like(like_path),
            Dataset.public == public
        ).all()

    # sort datasets and files (using python to have a consistant order) and return
    datasets = sorted(datasets, key=lambda d: d.path)
    for dataset in datasets:
        dataset.files = sorted(dataset.files, key=lambda f: f.path)

    return datasets


def insert_file(session, version, dataset_path, name, path, mime_type, checksum, checksum_type, attributes):
    logger.info('insert_file %s', path)

    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == str(dataset_path),
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError('No dataset with the name %s and the version %s found' % (dataset_path, version))

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == str(path),
        File.version == version
    ).one_or_none()

    if file:
        if file.checksum == checksum:
            # the file itself has not changed, update the specifiers or attributes
            if file.attributes != attributes:
                file.attributes = attributes
                file.specifiers = get_specifiers(attributes)
                file.search_vector = get_search_vector(attributes)
                logger.debug('update file %s', path)
            else:
                logger.debug('skip file %s', path)
        else:
            # the file has been changed, but the version is the same, this is not ok
            raise RuntimeError('%s has been changed but the version is the same' % path)
    else:
        # insert a new row for this file
        logger.debug('insert file %s', path)
        file = File(
            name=name,
            version=version,
            path=str(path),
            checksum=checksum,
            checksum_type=checksum_type,
            mime_type=mime_type,
            attributes=attributes,
            specifiers=get_specifiers(attributes),
            dataset=dataset,
            search_vector=get_search_vector(attributes)
        )
        session.add(file)


def insert_resource(session, path, version, datacite, datasets):
    # get the doi and the datacite version
    doi = next(item.get('identifier') for item in datacite.get('identifiers', []) if item.get('identifierType') == 'DOI')
    datacite_version = datacite.get('version')
    assert doi is not None
    assert datacite_version is not None

    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    if resource:
        raise RuntimeError('A resource with doi={} has already been registered.')

    # insert a new resource
    logger.debug('insert resource %s', path)
    resource = Resource(
        path=str(path),
        version=str(version),
        doi=doi,
        datacite=datacite
    )
    for dataset in datasets:
        resource.datasets.append(dataset)
    session.add(resource)


def update_resource(session, path, version, datacite):
    # get the doi and the datacite version
    doi = next(item.get('identifier') for item in datacite.get('identifiers', []) if item.get('identifierType') == 'DOI')
    datacite_version = datacite.get('version')
    assert doi is not None
    assert datacite_version is not None

    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    if resource:
        if resource.path != str(path):
            raise RuntimeError('A resource with doi={} has already been registered, but for a different path={}'.format(doi, path))

        if resource.datacite == datacite:
            logger.debug('skip resource %s', path)
        else:
            # check that the datacite version is not the same
            if resource.datacite.get('version') == datacite_version:
                raise RuntimeError('A resource with doi={} is in the database, and the datacite metadata '
                                   'has been updated, but the version={} is the same'.format(doi, datacite_version))

            # update the datecite metadata
            resource.datacite = datacite
    else:
        raise RuntimeError('A resource with doi={} can not be found in the database'.format(doi))


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
