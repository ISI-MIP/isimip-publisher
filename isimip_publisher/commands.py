import logging
from pathlib import Path

from tqdm import tqdm

from .config import settings, store
from .utils.database import (archive_dataset, clean_tree, fetch_resource,
                             init_database_session, insert_dataset,
                             insert_dataset_link, insert_file,
                             insert_file_link, insert_resource,
                             publish_dataset, retrieve_datasets,
                             update_dataset, update_file, update_resource,
                             update_search, update_tree, update_views)
from .utils.dois import upload_doi
from .utils.files import (copy_files, delete_file, link_file, list_files,
                          list_links, move_file)
from .utils.json import write_json_file
from .utils.patterns import filter_datasets, match_datasets
from .utils.validation import check_datasets, validate_datasets

logger = logging.getLogger(__name__)


def list_remote():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    for file_path in remote_files:
        print(file_path)


def list_remote_links():
    remote_links = list_links(settings.REMOTE_PATH, settings.PATH,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    for link_path in remote_links:
        print(link_path)


def list_local():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH)
    for file_path in local_files:
        print(file_path)


def list_public():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    for file_path in public_files:
        print(file_path)


def list_public_links():
    public_files = list_links(settings.PUBLIC_PATH, settings.PATH)
    for file_path in public_files:
        print(file_path)


def match_remote():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def match_remote_links():
    remote_links = list_links(settings.REMOTE_PATH, settings.PATH,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_links,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def match_local():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def match_public():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def match_public_links():
    public_links = list_links(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_links,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def fetch_files():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_files,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    c = sum([len(dataset.files) for dataset in datasets])
    t = tqdm(total=c, desc='fetch_files'.ljust(18))
    for n in copy_files(settings.REMOTE_DEST, settings.REMOTE_PATH, settings.LOCAL_PATH, settings.PATH, datasets):
        t.update(n)


def write_local_jsons():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        validate_datasets(settings.SCHEMA, settings.PATH, datasets)
        store.datasets = datasets

    for dataset in tqdm(store.datasets, desc='write_local_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def write_public_jsons():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    for dataset in tqdm(datasets, desc='write_public_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def write_link_jsons():
    public_links = list_links(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_links,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    for dataset in tqdm(datasets, desc='write_link_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def insert_datasets():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files,
                                  include=settings.INCLUDE, exclude=settings.EXCLUDE)
        validate_datasets(settings.SCHEMA, settings.PATH, datasets)
        store.datasets = datasets

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(store.datasets, desc='insert_datasets'.ljust(18)):
        insert_dataset(session, settings.VERSION, settings.RIGHTS, settings.RESTRICTED,
                       dataset.name, dataset.path, dataset.size, dataset.specifiers)

        for file in dataset.files:
            insert_file(session, settings.VERSION, file.dataset.path, file.uuid, file.name, file.path, file.size,
                        file.checksum, file.checksum_type, file.netcdf_header, file.specifiers)

        session.commit()

    update_search(session, settings.PATH)
    update_views(session)

    session.commit()


def link_links():
    remote_links = list_links(settings.REMOTE_PATH, settings.PATH,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_links,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    for dataset in tqdm(datasets, desc='link_links'.ljust(18)):
        for file in dataset.files:
            link_file(settings.PUBLIC_PATH, settings.TARGET_PATH, settings.PATH, file.path)


def link_files():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_files,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    for dataset in tqdm(datasets, desc='link_files'.ljust(18)):
        for file in dataset.files:
            link_file(settings.PUBLIC_PATH, settings.TARGET_PATH, settings.PATH, file.path)


def link_datasets():
    # collect and validate the links
    public_links = list_links(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_links,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(datasets, desc='link_datasets'.ljust(18)):
        target_dataset_path = str(settings.TARGET_PATH / Path(dataset.path).relative_to(settings.PATH))
        insert_dataset_link(session, settings.VERSION, settings.RIGHTS, target_dataset_path,
                            dataset.name, dataset.path, dataset.size, dataset.specifiers)

        for file in dataset.files:
            target_file_path = str(settings.TARGET_PATH / Path(file.path).relative_to(settings.PATH))
            insert_file_link(session, settings.VERSION, target_file_path, file.dataset.path, file.name, file.path,
                             file.size, file.checksum, file.checksum_type, file.netcdf_header, file.specifiers)

    session.commit()
    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()

    update_search(session, settings.PUBLIC_PATH)
    update_search(session, settings.TARGET_PATH)
    update_views(session)
    session.commit()


def publish_datasets():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        validate_datasets(settings.SCHEMA, settings.PATH, datasets)
        store.datasets = datasets

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(store.datasets, desc='publish_datasets'.ljust(18)):
        publish_dataset(session, settings.VERSION, dataset.path)

        for file in dataset.files:
            source_path = Path(file.abspath)
            target_path = Path(settings.PUBLIC_PATH) / Path(source_path).relative_to(settings.LOCAL_PATH)

            move_file(source_path, target_path)
            move_file(source_path.with_suffix('.json'), target_path.with_suffix('.json'))

        session.commit()

    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def update_datasets():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(datasets, desc='update_datasets'.ljust(18)):
        update_dataset(session, settings.RIGHTS, settings.RESTRICTED, dataset.path, dataset.specifiers)

        for file in dataset.files:
            update_file(session, file.dataset.path, file.path, file.specifiers)

        session.commit()

    update_search(session, settings.PATH)
    session.commit()
    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def archive_datasets():
    session = init_database_session(settings.DATABASE)

    # # since we have only files, not datasets (patterns could have changed since publication),
    # # we retrieve all datasets for this path and remove datasets which have no files in public_files
    path = Path(settings.PATH)
    like = not bool(path.suffix)
    db_datasets = retrieve_datasets(session, path, public=True, like=like)

    # apply include and exclude lists on the datasets from the database
    datasets = filter_datasets(db_datasets, include=settings.INCLUDE, exclude=settings.EXCLUDE)

    for dataset in tqdm(datasets, desc='archive_datasets'.ljust(18)):
        for link in dataset.links:
            link_version = archive_dataset(session, link.path)
            if link_version:
                archive_path = settings.ARCHIVE_PATH / link_version
                for file in link.files:
                    source_path = settings.PUBLIC_PATH / file.path
                    target_path = archive_path / Path(source_path).relative_to(settings.PUBLIC_PATH)

                    if source_path.is_file():
                        move_file(source_path, target_path)

                    if source_path.with_suffix('.json').is_file():
                        move_file(source_path.with_suffix('.json'), target_path.with_suffix('.json'))

        dataset_version = archive_dataset(session, dataset.path)
        if dataset_version:
            archive_path = settings.ARCHIVE_PATH / dataset_version
            for file in dataset.files:
                source_path = settings.PUBLIC_PATH / file.path
                target_path = archive_path / Path(source_path).relative_to(settings.PUBLIC_PATH)

                if source_path.is_file():
                    move_file(source_path, target_path)

                if source_path.with_suffix('.json').is_file():
                    move_file(source_path.with_suffix('.json'), target_path.with_suffix('.json'))

        session.commit()

    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def check():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)

    public_links = list_links(settings.PUBLIC_PATH, settings.PATH)
    datasets += match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_links,
                               include=settings.INCLUDE, exclude=settings.EXCLUDE)

    validate_datasets(settings.SCHEMA, settings.PATH, datasets)

    session = init_database_session(settings.DATABASE)

    # retrieve all datasets for this path and remove datasets which have no files in public_files
    path = Path(settings.PATH)
    db_datasets = retrieve_datasets(session, (path.parent if path.suffix else path), public=True)

    check_datasets(datasets, db_datasets)


def update_index():
    session = init_database_session(settings.DATABASE)

    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()

    update_search(session, settings.PATH)
    update_views(session)
    session.commit()


def clean():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH)
    for file_path in local_files:
        delete_file(settings.LOCAL_PATH / file_path)


def insert_doi():
    session = init_database_session(settings.DATABASE)

    resource = insert_resource(session, settings.RESOURCE, settings.PATHS, settings.DATACITE_PREFIX)

    session.commit()

    for path in resource.paths:
        update_search(session, path)

    session.commit()


def update_doi():
    session = init_database_session(settings.DATABASE)

    resource = update_resource(session, settings.RESOURCE)

    for path in resource.paths:
        update_search(session, path)

    session.commit()


def register_doi():
    print('Registering a DOI with DataCite is permanent. Please type "yes" to confirm.')
    string = input()

    if string.lower() == 'yes':
        session = init_database_session(settings.DATABASE)
        resource = fetch_resource(session, settings.DOI)
        upload_doi(resource, settings.ISIMIP_DATA_URL,
                   settings.DATACITE_USERNAME, settings.DATACITE_PASSWORD,
                   settings.DATACITE_PREFIX, settings.DATACITE_TEST_MODE)


def init():
    session = init_database_session(settings.DATABASE)
    update_views(session)
    session.commit()
