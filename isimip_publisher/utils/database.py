import logging
import warnings
from pathlib import Path
from uuid import uuid4

from sqlalchemy import (BigInteger, Boolean, Column, ForeignKey, Index, String,
                        Table, Text, create_engine, func, inspect)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from .datacite import add_datasets_to_related_identifiers, get_doi

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
    tree_path = Column(Text, nullable=True, index=True)

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
    doi = Column(Text, nullable=False, index=True)
    paths = Column(ARRAY(Text), nullable=False, index=True)
    datacite = Column(JSONB, nullable=False)

    datasets = relationship('Dataset', secondary=resources_datasets, back_populates='resources')

    def __repr__(self):
        return str(self.id)


class Tree(Base):

    __tablename__ = 'trees'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)
    tree_dict = Column(JSONB, nullable=False)

    def __repr__(self):
        return str(self.id)


def init_database_session(database_settings):
    engine = create_engine(database_settings)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def insert_dataset(session, version, name, path, size, specifiers):
    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        logger.debug('skip dataset %s', path)
        assert dataset.name == name, \
            'Dataset {} is already stored, but with different name'.format(path)
        assert dataset.specifiers == specifiers, \
            'Dataset {} is already stored, but with different specifiers'.format(path)
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
    # check that there is no public dataset with the same path
    public_dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.public == True
    ).one_or_none()

    assert public_dataset is None or public_dataset.version == version, \
        'A public dataset with the path %s and the version %s was found' % (path, public_dataset.version)

    # get the dataset
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.version == version
    ).one_or_none()

    assert dataset is not None, \
        'No dataset with the name %s and the version %s found' % (path, public_dataset.version)

    # mark this dataset public
    logger.debug('publish dataset %s', path)
    dataset.public = True


def update_dataset(session, name, path, specifiers):
    # check if the dataset is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.public == True
    ).one_or_none()

    assert dataset is not None, \
        'No public dataset with the path {} found.'.format(path)

    # update the dataset
    logger.debug('update dataset %s', path)
    dataset.name = name
    dataset.specifiers = specifiers
    dataset.identifiers = list(specifiers.keys())
    dataset.search_vector = get_search_vector(specifiers)


def unpublish_dataset(session, path):
    # find the public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.public == True
    ).one_or_none()

    if public_dataset:
        # mark this dataset archived
        logger.debug('unpublish dataset %s', path)
        public_dataset.public = False
        return public_dataset.version


def retrieve_datasets(session, path, public=None):
    # check if path is a file
    if Path(path).suffix:
        path = Path(path).parent.as_posix()

    like_path = '{}/%'.format(path)

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
    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    assert dataset is not None, \
        'No dataset with the path {} found'.format(dataset_path)

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == path,
        File.version == version
    ).one_or_none()

    if file:
        logger.debug('skip file %s', path)
        assert uuid is None or file.id == uuid, \
            'File {} is already stored with the same version, but a different id'.format(path)
        assert file.checksum == checksum, \
            'File {} is already stored with the same version, but a different checksum'.format(path)
        assert file.name == name, \
            'File {} is already stored with the same version, but a different name'.format(path)
        assert file.specifiers == specifiers, \
            'File {} is already stored with the same version, but different specifiers'.format(path)
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


def update_file(session, dataset_path, name, path, specifiers):
    logger.info('update_file %s', path)

    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.public == True
    ).one_or_none()

    assert dataset is not None, \
        'No public dataset with the path {} found'.format(dataset_path)

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == path,
        File.dataset == dataset
    ).one_or_none()

    if file:
        logger.debug('update file %s', path)
        file.name = name
        file.specifiers = specifiers
    else:
        raise AssertionError('No file with the path {} found in dataset {}'.format(path, dataset_path))


def insert_resource(session, resource_metadata, isimip_data_url):
    # get the datacite metadata and the doi
    datacite = resource_metadata.get('datacite')
    if resource_metadata.get('datacite'):
        doi = get_doi(datacite)
        assert doi is not None, 'The DOI in the metadata does not match the provided DOI.'
    else:
        doi = resource_metadata.get('external_doi')
        assert doi is not None, 'No DataCite metadata or external DOI was provided.'

    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    assert resource is None, \
        'A resource with doi={} is already in the database.'.format(doi)

    # get the path
    paths = resource_metadata.get('paths', [])
    assert paths, 'No paths were provided for {}.'.format(doi)

    # gather datasets
    datasets = []
    for path in paths:
        datasets += retrieve_datasets(session, path, public=True)
    assert datasets, 'No datasets found for {}.'.format(doi)

    if datacite:
        datacite = add_datasets_to_related_identifiers(datasets, datacite, isimip_data_url)

    # insert a new resource
    logger.debug('insert resource %s', doi)
    resource = Resource(
        doi=doi,
        paths=paths,
        datacite=datacite
    )
    for dataset in datasets:
        resource.datasets.append(dataset)
    session.add(resource)


def update_resource(session, resource_metadata, isimip_data_url):
    # get the datacite metadata and the doi
    datacite = resource_metadata.get('datacite')
    if resource_metadata.get('datacite'):
        doi = get_doi(datacite)
        version = datacite.get('version')
        assert doi is not None, 'The DOI in the metadata does not match the provided DOI.'
    else:
        doi = resource_metadata.get('external_doi')
        version = None
        assert doi is not None, 'No DataCite metadata or external DOI was provided.'

    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    assert resource is not None, \
        'A resource with doi={} was not found.'.format(doi)

    # gather datasets
    if datacite:
        datacite = add_datasets_to_related_identifiers(resource.datasets, datacite, isimip_data_url)

    if resource.datacite == datacite:
        logger.debug('skip resource %s', doi)
    else:
        # check that the datacite version is not the same
        if version and resource.datacite and resource.datacite.get('version') == version:
            message = 'A resource with doi={} was found in the database, and the DataCite metadata has been updated, but the version={} is the same.'.format(doi, version)
            warnings.warn(RuntimeWarning(message))

        # update the datecite metadata
        resource.datacite = datacite


def update_tree(session, path, tree):
    # check if path is a file
    if Path(path).suffix:
        path = Path(path).parent.as_posix()

    # step 1: get the public datasets for this path
    like_path = '{}%'.format(path)
    datasets = session.query(Dataset).filter(
        Dataset.path.like(like_path),
        Dataset.public == True
    ).all()

    # step 2: get the tree
    database_tree = session.query(Tree).one_or_none()
    if database_tree is not None:
        logger.debug('update tree')
    else:
        logger.debug('insert tree')
        database_tree = Tree(tree_dict={})
        session.add(database_tree)

    # step 3: recursively update tree_dict and set the tree_path for the dataset
    for dataset in datasets:
        tree_path = build_tree_dict(database_tree.tree_dict, Path(), tree['identifiers'], dataset.specifiers)
        dataset.tree_path = tree_path.as_posix()

    # for some reason we need to flag the field as modified
    flag_modified(database_tree, 'tree_dict')


def build_tree_dict(tree_dict, tree_path, identifiers, specifiers):
    identifier = identifiers[0]
    specifier = None

    if '&' in identifier:
        sub_identifiers, sub_specifiers = [], []
        for sub_identifier in identifiers[0].split('&'):
            if sub_identifier in specifiers:
                sub_identifiers.append(sub_identifier)
                sub_specifiers.append(specifiers.get(sub_identifier))
        identifier = '-'.join(sub_identifiers)
        specifier = '-'.join(sub_specifiers)

    elif '|' in identifier:
        for sub_identifier in identifiers[0].split('|'):
            if sub_identifier in specifiers:
                identifier = sub_identifier
                specifier = specifiers.get(sub_identifier)
                break

    else:
        specifier = specifiers.get(identifier)

    if specifier is None:
        return tree_path
    else:
        if specifier not in tree_dict:
            # add a new node to the tree_dict
            tree_dict[specifier] = {
                'identifier': identifier,
                'specifier': specifier,
                'items': {}
            }

        # update tree_path
        tree_path /= specifier

        if len(identifiers) == 1:
            # this is the last node
            return tree_path
        else:
            return build_tree_dict(tree_dict[specifier]['items'], tree_path, identifiers[1:], specifiers)


def clean_tree(session):
    # step 1: get the tree
    database_tree = session.query(Tree).one_or_none()

    # step 2: get all dataset tree_pathes as as set
    tree_pathes = set([row[0] for row in session.query(Dataset).filter(
        Dataset.public == True
    ).values('tree_path')])

    clean_tree_dict = {}
    for tree_path in tree_pathes:
        if tree_path:
            specifiers = Path(tree_path).parts
            clean_tree_dict = build_clean_tree_dict(database_tree.tree_dict, clean_tree_dict, specifiers)

    # replace database_tree.tree_dict
    database_tree.tree_dict = clean_tree_dict

    # for some reason we need to flag the field as modified
    flag_modified(database_tree, 'tree_dict')


def build_clean_tree_dict(tree_dict, clean_tree_dict, specifiers):
    specifier = specifiers[0]

    if specifier not in clean_tree_dict:
        clean_tree_dict[specifier] = {
            'identifier': tree_dict[specifier]['identifier'],
            'specifier': tree_dict[specifier]['specifier'],
            'items': {}
        }

    if len(specifiers) > 1:
        clean_tree_dict[specifier]['items'] = build_clean_tree_dict(tree_dict[specifier]['items'],
                                                                    clean_tree_dict[specifier]['items'],
                                                                    specifiers[1:])

    return clean_tree_dict


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
