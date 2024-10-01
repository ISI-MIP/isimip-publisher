import logging
import re
import warnings
from datetime import datetime
from math import isnan
from pathlib import Path
from uuid import uuid4

from deepdiff import DeepDiff
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Table,
    Text,
    create_engine,
    func,
    inspect,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.orm import backref, declarative_base, relationship, sessionmaker
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.sql import column

from .dois import get_doi, get_title

logger = logging.getLogger(__name__)

search_terms_split_pattern = re.compile(r'[\/\_\-\s]')

Base = declarative_base()

# association table between resources and datasets
resources_datasets = Table('resources_datasets', Base.metadata,
                           Column('resource_id', UUID, ForeignKey('resources.id')),
                           Column('dataset_id', UUID, ForeignKey('datasets.id')))


class Dataset(Base):

    __tablename__ = 'datasets'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)
    target_id = Column(UUID, ForeignKey('datasets.id'), nullable=True)

    name = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)
    size = Column(BigInteger, nullable=False)
    specifiers = Column(JSONB, nullable=False)
    identifiers = Column(ARRAY(Text), nullable=False)
    public = Column(Boolean, nullable=False)
    restricted = Column(Boolean, nullable=False)
    tree_path = Column(Text, nullable=True, index=True)
    rights = Column(Text)

    files = relationship('File', back_populates='dataset')
    links = relationship('Dataset', backref=backref('target', remote_side=id))
    resources = relationship('Resource', secondary=resources_datasets, back_populates='datasets')
    search = relationship('Search', back_populates='dataset', uselist=False)

    created = Column(DateTime)
    updated = Column(DateTime)
    published = Column(DateTime)
    archived = Column(DateTime)

    def __repr__(self):
        return str(self.id)


class File(Base):

    __tablename__ = 'files'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)
    dataset_id = Column(UUID, ForeignKey('datasets.id'))
    target_id = Column(UUID, ForeignKey('files.id'), nullable=True)

    name = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False, index=True)
    version = Column(String(8), nullable=False, index=True)
    size = Column(BigInteger, nullable=False)
    checksum = Column(Text, nullable=False)
    checksum_type = Column(Text, nullable=False)
    netcdf_header = Column(JSONB, nullable=True)
    specifiers = Column(JSONB, nullable=False)
    identifiers = Column(ARRAY(Text), nullable=False)

    created = Column(DateTime)
    updated = Column(DateTime)

    dataset = relationship('Dataset', back_populates='files')
    links = relationship('File', backref=backref('target', remote_side=id))

    def __repr__(self):
        return str(self.id)


class Resource(Base):

    __tablename__ = 'resources'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)

    doi = Column(Text, nullable=False, index=True)
    title = Column(Text, nullable=False)
    version = Column(Text)
    paths = Column(ARRAY(Text), nullable=False, index=True)
    datacite = Column(JSONB, nullable=False)

    created = Column(DateTime)
    updated = Column(DateTime)

    datasets = relationship('Dataset', secondary=resources_datasets, back_populates='resources')

    def __repr__(self):
        return str(self.id)


class Tree(Base):

    __tablename__ = 'trees'

    id = Column(UUID, nullable=False, primary_key=True, default=lambda: uuid4().hex)

    tree_dict = Column(JSONB, nullable=False)

    created = Column(DateTime)
    updated = Column(DateTime)

    def __repr__(self):
        return str(self.id)


class Search(Base):

    __tablename__ = 'search'
    __table_args__ = (
        Index('search_vector_idx', 'vector', postgresql_using='gin'),
    )

    dataset_id = Column(UUID, ForeignKey('datasets.id'), primary_key=True)
    vector = Column(TSVECTOR, nullable=False)

    created = Column(DateTime)
    updated = Column(DateTime)

    dataset = relationship('Dataset', back_populates='search')

    def __repr__(self):
        return str(self.dataset_id)


def init_database_session(database_settings):
    engine = create_engine(database_settings)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def get_search_terms(dataset):
    terms = list(dataset.specifiers.values())
    terms += search_terms_split_pattern.split(str(dataset.id))
    terms += search_terms_split_pattern.split(dataset.path)
    terms.append(dataset.version)
    terms.append(dataset.rights)

    # loop over resources to get title, doi, and creators
    for resource in dataset.resources:
        terms += [resource.title, *resource.doi.split('/')]
        if resource.datacite is not None:
            terms += [creator.get('name') for creator in resource.datacite.get('creators', [])]

    return terms


def get_search_vector(dataset):
    terms = get_search_terms(dataset)

    # if the dataset has a target (is a link), get the terms of the target
    if dataset.target is not None:
        terms += get_search_terms(dataset.target)

        # loop over the links of the target, but not this dataset
        for link in dataset.target.links:
            if link.id != dataset.id:
                terms += get_search_terms(link)

    # loop over links, if any
    for link in dataset.links:
        terms += get_search_terms(link)

    search_string = ' '.join({str(value) for value in set(terms)})
    return func.setweight(func.to_tsvector(search_string), 'A')


def insert_dataset(session, version, rights, restricted, name, path, size, specifiers):
    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        logger.debug('skip dataset %s', path)
        if dataset.target is not None:
            raise RuntimeError(f'Dataset {path} is already stored, but with a target')
        if dataset.rights != rights:
            raise RuntimeError(f'Dataset {path} is already stored, but with different rights')
        if dataset.name != name:
            raise RuntimeError(f'Dataset {path} is already stored, but with different name')
        if dataset.specifiers != specifiers:
            raise RuntimeError(f'Dataset {path} is already stored, but with different specifiers')
    else:
        # insert a new row for this dataset
        logger.debug('insert dataset %s', path)
        dataset = Dataset(
            name=name,
            path=path,
            version=version,
            size=size,
            rights=rights,
            specifiers=specifiers,
            identifiers=list(specifiers.keys()),
            public=False,
            restricted=restricted,
            created=datetime.utcnow()
        )
        session.add(dataset)


def publish_dataset(session, version, path):
    # check that there is no public dataset with the same path
    public_dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.public == True  # noqa: E712
    ).one_or_none()

    if public_dataset is not None and public_dataset.version != version:
        raise RuntimeError(f'A public dataset with the path {path} and the version {public_dataset.version} was found')

    # get the dataset
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError(f'No dataset with the name {path} and the version {public_dataset.version} found')

    # mark this dataset public
    logger.debug('publish dataset %s', path)
    dataset.public = True
    dataset.published = datetime.utcnow()


def update_dataset(session, rights, restricted, path, specifiers):
    # check if the dataset is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.public == True  # noqa: E712
    ).one_or_none()

    if dataset is None:
        raise RuntimeError(f'No public dataset with the path {path} found.')

    if dataset.target:
        if dataset.target.rights != rights:
            raise RuntimeError(f'Target dataset {dataset.target.path} was found, but with different rights')

    # update the dataset
    logger.debug('update dataset %s', path)

    # update rights and restricted on all links
    if dataset.rights != rights:
        dataset.rights = rights
        for link in dataset.links:
            link.rights = rights

    if dataset.restricted != restricted:
        dataset.restricted = restricted
        for link in dataset.links:
            link.restricted = restricted

    dataset.specifiers = specifiers
    dataset.identifiers = list(specifiers.keys())
    dataset.updated = datetime.utcnow()


def insert_dataset_link(session, version, rights, restricted, target_dataset_path, name, path, size, specifiers):
    # get the target_dataset
    target_dataset = session.query(Dataset).filter(
        Dataset.path == target_dataset_path,
        Dataset.version == version
    ).one_or_none()

    if target_dataset is None:
        raise RuntimeError(f'No target dataset for the path {target_dataset_path} with version {version} found')
    if target_dataset.rights != rights:
        raise RuntimeError(f'Target dataset {target_dataset_path}#{version} was found, but with different rights')
    if target_dataset.name != name:
        raise RuntimeError(f'Target dataset {target_dataset_path}#{version} was found, but with a different name')
    if target_dataset.size != size:
        raise RuntimeError(f'Target dataset {target_dataset_path}#{version} was found, but with a different size')

    # check if the dataset with this version is already in the database
    dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.version == version
    ).one_or_none()

    if dataset:
        logger.debug('skip dataset link %s', path)
        if dataset.target != target_dataset:
            raise RuntimeError(f'Dataset link {path} is already stored, but with a different target')
        if dataset.rights != rights:
            raise RuntimeError(f'Dataset link {path} is already stored, but with different rights')
        if dataset.name != name:
            raise RuntimeError(f'Dataset link {path} is already stored, but with a different name')
        if dataset.specifiers != specifiers:
            raise RuntimeError(f'Dataset link {path} is already stored, but with different specifiers')
    else:
        # insert a new row for this dataset
        logger.debug('insert dataset %s', path)
        dataset = Dataset(
            name=name,
            path=path,
            version=version,
            size=size,
            rights=rights,
            specifiers=specifiers,
            identifiers=list(specifiers.keys()),
            public=True,
            restricted=restricted,
            target=target_dataset,
            created=datetime.utcnow()
        )
        session.add(dataset)


def archive_dataset(session, path):
    # find the public version of this dataset
    public_dataset = session.query(Dataset).filter(
        Dataset.path == path,
        Dataset.public == True  # noqa: E712
    ).one_or_none()

    if public_dataset:
        # mark this dataset archived
        logger.debug('unpublish dataset %s', path)
        public_dataset.public = False
        public_dataset.archived = datetime.utcnow()
        return public_dataset.version


def retrieve_datasets(session, path, public=None, follow=False, like=True):
    path = Path(path)
    db_datasets = session.query(Dataset)

    if like:
        like_path = path.as_posix() + '/%'
        db_datasets = db_datasets.filter(Dataset.path.like(like_path))
    else:
        db_datasets = db_datasets.join(Dataset.files).filter(File.path == path.as_posix())

    if public:
        db_datasets = db_datasets.filter(Dataset.public == public)

    datasets = []
    for dataset in db_datasets.all():
        if follow and dataset.target:
            datasets.append(dataset.target)
        else:
            datasets.append(dataset)

    # sort datasets and files (using python to have a consistant order) and return
    datasets = sorted(datasets, key=lambda d: d.path)
    for dataset in datasets:
        dataset.files = sorted(dataset.files, key=lambda f: f.path)

    return datasets


def check_file_id(session, path, uuid):
    file = session.query(File).filter(File.id == uuid).one_or_none()
    if file:
        raise RuntimeError(f'File {path} has an id which already exists in the database ({uuid})')


def insert_file(session, version, dataset_path, uuid, name, path, size,
                checksum, checksum_type, netcdf_header, specifiers):
    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError(f'No dataset with the path {dataset_path} found')

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == path,
        File.version == version
    ).one_or_none()

    if file:
        logger.debug('skip file %s', path)
        if uuid is not None and str(file.id) != uuid:
            raise RuntimeError(f'File {path} is already stored with the same version, but a different id')
        if file.name != name:
            raise RuntimeError(f'File {path} is already stored with the same version, but a different name')
        if file.size != size:
            raise RuntimeError(f'File {path} is already stored with the same version, but a different size')
        if file.checksum != checksum:
            raise RuntimeError(f'File {path} is already stored with the same version, but a different checksum')
        if file.checksum_type != checksum_type:
            raise RuntimeError(f'File {path} is already stored with the same version, but a different checksum_type')
        if DeepDiff(file.netcdf_header, netcdf_header, ignore_numeric_type_changes=False):
            raise RuntimeError(f'File {path} is already stored with the same version, but a different netcdf_header')
        if file.specifiers != specifiers:
            raise RuntimeError(f'File {path} is already stored with the same version, but different specifiers')
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
            netcdf_header=clean_json(netcdf_header),
            specifiers=specifiers,
            identifiers=list(specifiers.keys()),
            dataset=dataset,
            created=datetime.utcnow()
        )
        session.add(file)


def update_file(session, dataset_path, path, specifiers):
    logger.info('update_file %s', path)

    # get the dataset from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.public == True  # noqa: E712
    ).one_or_none()

    if dataset is None:
        raise RuntimeError(f'No public dataset with the path {dataset_path} found')

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == path,
        File.dataset == dataset
    ).one_or_none()

    if file:
        logger.debug('update file %s', path)
        file.specifiers = specifiers
        file.identifiers = list(specifiers.keys())
        file.updated = datetime.utcnow()
    else:
        raise RuntimeError(f'No file with the path {path} found in dataset {dataset_path}')


def insert_file_link(session, version, target_file_path, dataset_path,
                     name, path, size, checksum, checksum_type, netcdf_header, specifiers):
    # get the target file
    target_file = session.query(File).filter(
        File.path == target_file_path,
        File.version == version
    ).one_or_none()

    if target_file is None:
        raise RuntimeError(f'No target file for the path {target_file_path} with version {version} found')
    if target_file.name != name:
        raise RuntimeError(f'Target file {target_file_path}#{version} was found, but with a different name')
    if target_file.size != size:
        raise RuntimeError(f'Target file {target_file_path}#{version} was found, but with a different size')
    if target_file.checksum != checksum:
        raise RuntimeError(f'Target file {target_file_path}#{version} was found, but with a different checksum')
    if target_file.checksum_type != checksum_type:
        raise RuntimeError(f'Target file {target_file_path}#{version} was found, but with a different checksum_type')

    # get the linked dataset for this file from the database
    dataset = session.query(Dataset).filter(
        Dataset.path == dataset_path,
        Dataset.version == version
    ).one_or_none()

    if dataset is None:
        raise RuntimeError(f'No dataset with the path {dataset_path} found')
    if dataset.target != target_file.dataset:
        raise RuntimeError(f'Dataset for file link does not match dataset for {path}')

    # check if the file is already in the database
    file = session.query(File).filter(
        File.path == path,
        File.version == version
    ).one_or_none()

    if file:
        logger.debug('skip file %s', path)
        if file.name != name:
            raise RuntimeError(f'File link {path} is already stored with the same version, but a different name')
        if file.size != size:
            raise RuntimeError(f'File link {path} is already stored with the same version, but a different size')
        if file.checksum != checksum:
            raise RuntimeError(f'File link {path} is already stored with the same version, but a different checksum')
        if file.checksum_type != checksum_type:
            raise RuntimeError(f'File link {path} is already stored with the same version,'
                                ' but a different checksum_type')
        if DeepDiff(file.netcdf_header, netcdf_header, ignore_numeric_type_changes=False):
            raise RuntimeError(f'File link {path} is already stored with the same version,'
                                ' but a different netcdf_header')
        if file.specifiers != specifiers:
            raise RuntimeError(f'File link {path} is already stored with the same version, but different specifiers')
    else:
        # insert a new row for this file
        logger.debug('insert file %s', path)
        file = File(
            name=name,
            path=path,
            version=version,
            size=size,
            checksum=checksum,
            checksum_type=checksum_type,
            netcdf_header=clean_json(netcdf_header),
            specifiers=specifiers,
            identifiers=list(specifiers.keys()),
            dataset=dataset,
            target=target_file,
            created=datetime.utcnow()
        )
        session.add(file)


def insert_resource(session, datacite, paths, datacite_prefix):
    doi = get_doi(datacite)
    title = get_title(datacite)
    version = datacite.get('version')

    if doi is None:
        raise RuntimeError('No DOI was provided.')
    if title is None:
        raise RuntimeError('No title was provided.')

    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    if resource is not None:
        raise RuntimeError(f'A resource with doi={doi} is already in the database.')

    # get the path
    if not paths:
        raise RuntimeError(f'No paths were provided for {doi}.')

    # gather datasets, use a set to remove duplicate datasets (for links)
    datasets = set()
    for path in paths:
        datasets.update(retrieve_datasets(session, path, public=True, follow=True))

    if not datasets:
        message = f'No datasets found for {doi}.'
        warnings.warn(RuntimeWarning(message), stacklevel=2)

    # insert a new resource
    logger.debug('insert resource %s', doi)
    resource = Resource(
        doi=doi,
        title=title,
        version=version,
        paths=paths,
        created=datetime.utcnow()
    )

    # only add the metadata if this is a "native" DOI, not an external one
    if doi.startswith(datacite_prefix):
        resource.datacite = datacite
    else:
        resource.datacite = {}

    # add the datasets as many to many relation
    for dataset in datasets:
        resource.datasets.append(dataset)

    session.add(resource)

    return resource


def update_resource(session, datacite):
    doi = get_doi(datacite)
    title = get_title(datacite)
    version = datacite.get('version')

    if doi is None:
        raise RuntimeError('No DOI was provided.')
    if title is None:
        raise RuntimeError('No title was provided.')

    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    if resource is None:
        raise RuntimeError(f'A resource with doi={doi} was not found.')

    # update the datecite metadata
    resource.title = title
    resource.version = version
    resource.datacite = datacite
    resource.updated = datetime.utcnow()

    return resource


def fetch_resource(session, doi):
    # look for the resource in the database
    resource = session.query(Resource).filter(
        Resource.doi == doi
    ).one_or_none()

    if resource is None:
        raise RuntimeError(f'A resource with doi={doi} was not found.')

    return resource


def update_tree(session, path, tree):
    # check if path is a file
    if Path(path).suffix:
        path = Path(path).parent.as_posix()

    # step 1: get the public datasets for this path
    like_path = f'{path}%'
    datasets = session.query(Dataset).filter(
        Dataset.path.like(like_path),
        Dataset.public == True  # noqa: E712
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
                sub_specifiers.append(str(specifiers.get(sub_identifier)))
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
    tree_pathes = {row[0] for row in session.query(Dataset).filter(
        Dataset.public == True  # noqa: E712
    ).values(column('tree_path'))}

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


def update_search(session, path):
    # check if path is a file
    if Path(path).suffix:
        path = Path(path).parent.as_posix()

    # step 1: get the all datasets for this path
    like_path = f'{path}%'
    datasets = session.query(Dataset).filter(
        Dataset.path.like(like_path)
    ).all()

    for dataset in datasets:
        create_or_update_search(session, dataset)

        if dataset.target:
            create_or_update_search(session, dataset.target)

        for link in dataset.links:
            create_or_update_search(session, link)


def create_or_update_search(session, dataset):
    if dataset.search is None:
        dataset.search = Search(
            dataset=dataset,
            vector=get_search_vector(dataset),
            created=datetime.utcnow()
        )
        session.add(dataset.search)
    else:
        dataset.search.vector = get_search_vector(dataset)
        dataset.search.updated = datetime.utcnow()


def update_views(session):
    update_identifiers_view(session)
    update_specifiers_view(session)


def update_identifiers_view(session):
    if 'identifiers' in get_materialized_view_names(session):
        session.connection().execute(text('''
            REFRESH MATERIALIZED VIEW identifiers
        '''))
        logger.debug('update identifiers view')
    else:
        session.connection().execute(text('''
            CREATE MATERIALIZED VIEW identifiers AS
            SELECT specifiers.key AS identifier,
                   JSON_AGG(DISTINCT specifiers.value) AS specifiers
            FROM public.datasets,
                 jsonb_each_text(public.datasets.specifiers) AS specifiers
            GROUP BY identifier
            ORDER BY identifier
        '''))
        session.connection().execute(text('''
            CREATE INDEX ON identifiers(identifier)
        '''))
        logger.debug('create identifiers view')


def update_specifiers_view(session):
    if 'specifiers' in get_materialized_view_names(session):
        session.connection().execute(text('''
            REFRESH MATERIALIZED VIEW specifiers
        '''))
        logger.debug('update specifiers view')
    else:
        session.connection().execute(text('''
            CREATE MATERIALIZED VIEW specifiers AS
            SELECT DISTINCT specifiers.value::text as specifier
            FROM public.datasets,
                 jsonb_each_text(public.datasets.specifiers) AS specifiers
            ORDER BY specifier;
        '''))
        session.connection().execute(text('''
            CREATE INDEX ON specifiers USING gin(specifier gin_trgm_ops)
        '''))
        logger.debug('create specifiers view')


def get_materialized_view_names(session):
    engine = session.get_bind()
    try:
        return inspect(engine).get_materialized_view_names()
    except AttributeError:
        # for SQLAlchemy < 2
        return inspect(engine).get_view_names()


def clean_json(data):
    if isinstance(data, list):
        return [clean_json(item) for item in data]
    elif isinstance(data, dict):
        return {key: clean_json(value) for key, value in data.items()}
    elif isinstance(data, float) and isnan(data):
        return 'NaN'
    else:
        return data
