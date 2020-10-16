import logging
import warnings
from uuid import uuid4

from sqlalchemy import (BigInteger, Boolean, Column, ForeignKey, Index, String,
                        Table, Text, create_engine, func, inspect)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from .datacite import gather_datasets

logger = logging.getLogger(__name__)

Base = declarative_base()


def get_search_vector(specifiers):
    values = [str(value) for value in specifiers.values()]
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

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)
    name = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)
    size = Column(BigInteger, nullable=False)
    specifiers = Column(JSONB, nullable=False)
    identifiers = Column(ARRAY(Text), nullable=False)
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

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)
    dataset_id = Column(UUID, ForeignKey('datasets.id'))
    name = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)
    size = Column(BigInteger, nullable=False)
    checksum = Column(Text, nullable=False)
    checksum_type = Column(Text, nullable=False)
    specifiers = Column(JSONB, nullable=False)
    identifiers = Column(ARRAY(Text), nullable=False)
    search_vector = Column(TSVECTOR, nullable=False)

    dataset = relationship('Dataset', back_populates='files')

    def __repr__(self):
        return str(self.id)


class Resource(Base):

    __tablename__ = 'resources'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)

    doi = Column(Text, nullable=False, index=True)
    datacite = Column(JSONB, nullable=False)

    datasets = relationship('Dataset', secondary=resources_datasets, back_populates='resources')

    def __repr__(self):
        return str(self.id)


class Tree(Base):

    __tablename__ = 'trees'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)
    tree_dict = Column(JSONB, nullable=False)
    tree_list = Column(JSONB, nullable=False)

    def __repr__(self):
        return str(self.id)


def init_database_session(database_settings):
    engine = create_engine(database_settings)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def insert_dataset(session, version, name, path, size, specifiers):
    logger.info('insert_dataset %s', path)

    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        # if the dataset already exists, update its specifiers
        if dataset.specifiers != specifiers:
            dataset.specifiers = specifiers
            dataset.identifiers = list(specifiers.keys())
            dataset.search_vector = get_search_vector(specifiers)
            logger.debug('update dataset %s', path)
        else:
            logger.debug('skip dataset %s', path)

    else:
        # insert a new row for this dataset
        logger.debug('insert dataset %s', path)
        dataset = Dataset(
            name=name,
            path=path,
            version=version,
            size=size,
            specifiers=specifiers,
            identifiers=list(specifiers.keys()),
            search_vector=get_search_vector(specifiers),
            public=False
        )
        session.add(dataset)


def publish_dataset(session, version, path):
    # check that there is no public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.public == True
    ).one_or_none()

    if public_dataset and public_dataset.version != version:
        raise RuntimeError('A public dataset with the path %s and the version %s was found' %
                           (path, public_dataset.version))

    # mark this dataset public
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError('No dataset with the name %s and the version %s found' %
                           (path, public_dataset.version))

    dataset.public = True


def unpublish_dataset(session, path):
    # find the public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == path,
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


def insert_file(session, version, dataset_path, uuid, name, path, size, checksum, checksum_type, specifiers):
    logger.info('insert_file %s', path)

    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError('No dataset with the name %s and the version %s found' % (dataset_path, version))

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == path,
        File.version == version
    ).one_or_none()

    if file:
        if uuid is not None and file.id != uuid:
            # the file is already stored with a different id
            raise RuntimeError('%s is already stored with the same version but a different id' % path)

        if file.checksum == checksum:
            # the file itself has not changed, update the specifiers
            if file.specifiers != specifiers:
                file.specifiers = specifiers
                file.identifiers = list(specifiers.keys())
                file.search_vector = get_search_vector(specifiers)
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
            id=uuid,
            name=name,
            path=path,
            version=version,
            size=size,
            checksum=checksum,
            checksum_type=checksum_type,
            specifiers=specifiers,
            identifiers=list(specifiers.keys()),
            search_vector=get_search_vector(specifiers),
            dataset=dataset
        )
        session.add(file)


def insert_resource(session, path, version, datacite, isimip_data_url, datasets, update=False):
    # get the doi and the datacite version
    doi = next(item.get('identifier') for item in datacite.get('identifiers', []) if item.get('identifierType') == 'DOI')
    datacite_version = datacite.get('version')
    assert doi is not None
    assert datacite_version is not None

    # add datasets to relatedIdentifiers
    datacite['relatedIdentifiers'] += gather_datasets(isimip_data_url, datasets)

    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    if resource:
        if resource.path != path:
            message = 'A resource with doi={} was found in the database, but for a different path={}.'.format(doi, path)
            raise RuntimeError(message)

        # check that the datasets match
        if sorted(resource.datasets, key=lambda d: d.id) != sorted(datasets, key=lambda d: d.id):
            message = 'A resource with doi={} was found in the database, but the list of related public datasets changed. Please consider a new DOI.'.format(doi)
            raise RuntimeError(message)

        if resource.datacite == datacite:
            logger.debug('skip resource %s', path)
        else:
            # check that the datacite version is not the same
            if resource.datacite.get('version') == datacite_version:
                message = 'A resource with doi={} was found in the database, and the DataCite metadata has been updated, but the version={} is the same.'.format(doi, datacite_version)
                warnings.warn(RuntimeWarning(message))

            # update the datecite metadata
            resource.datacite = datacite

    else:
        # insert a new resource
        logger.debug('insert resource %s', path)
        resource = Resource(
            path=path,
            version=str(version),
            doi=doi,
            datacite=datacite
        )
        for dataset in datasets:
            resource.datasets.append(dataset)
        session.add(resource)


def update_tree(session):
    datasets = session.query(Dataset).filter(
        Dataset.public == True
    ).order_by(Dataset.path)

    # step 1: recursively build tree_dict
    tree_dict = {}
    for dataset in datasets:
        specifiers = [(identifier, dataset.specifiers[identifier]) for identifier in dataset.identifiers]
        build_tree_dict(tree_dict, specifiers)

    # step 2: recursively build tree_list
    tree_list = build_tree_list(tree_dict)

    tree = session.query(Tree).one_or_none()
    if tree:
        # insert a new tree
        logger.debug('update tree')
        tree.tree_dict = tree_dict
        tree.tree_list = tree_list

    else:
        # insert a new tree
        logger.debug('insert tree')
        tree = Tree(
            tree_dict=tree_dict,
            tree_list=tree_list
        )
        session.add(tree)


def build_tree_dict(tree_dict, specifiers):
    identifier, specifier = specifiers[0]

    if specifier not in tree_dict:
        tree_dict[specifier] = {
            'identifier': identifier,
            'specifier': specifier,
            'items': {}
        }

    if len(specifiers) > 1:
        build_tree_dict(tree_dict[specifier]['items'], specifiers[1:])


def build_tree_list(tree_dict):
    tree_list = []
    for specifier, item in tree_dict.items():
        tree_list.append({
            'identifier': item.get('identifier'),
            'specifier': item.get('specifier'),
            'items': build_tree_list(item.get('items'))
        })

    return tree_list


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
            CREATE MATERIALIZED VIEW attributes AS SELECT DISTINCT jsonb_object_keys(specifiers) AS key FROM public.datasets
        ''')
        session.connection().execute('''
            CREATE INDEX ON attributes(key)
        ''')
        logger.debug('create attributes view')
