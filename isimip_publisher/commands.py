import logging
from pathlib import Path

from tqdm import tqdm

from .config import settings, store
from .utils.database import (archive_dataset, clean_tree,
                             init_database_session, insert_dataset,
                             insert_file, insert_resource, publish_dataset,
                             retrieve_datasets, update_attributes_view,
                             update_dataset, update_file, update_resource,
                             update_tree, update_words_view)
from .utils.datacite import fetch_datacite_xml, upload_doi, upload_doi_metadata
from .utils.files import copy_files, delete_file, list_files, move_file
from .utils.json import write_json_file
from .utils.patterns import filter_datasets, match_datasets
from .utils.validation import check_datasets, validate_datasets

logger = logging.getLogger(__name__)


def list_local():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH)
    for file_path in local_files:
        print(file_path)


def list_public():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    for file_path in public_files:
        print(file_path)


def list_remote():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH, remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    for file_path in remote_files:
        print(file_path)


def match_remote():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH, remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def match_local():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def match_public():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, datasets)
    for dataset in datasets:
        for file in dataset.files:
            print(file.path)


def fetch_files():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH, remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, datasets)

    c = sum([len(dataset.files) for dataset in datasets])
    t = tqdm(total=c, desc='fetch_files'.ljust(18))
    for n in copy_files(settings.REMOTE_DEST, settings.REMOTE_PATH, settings.LOCAL_PATH, settings.PATH, datasets):
        t.update(n)


def write_jsons():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        validate_datasets(settings.SCHEMA, datasets)
        store.datasets = datasets

    for dataset in tqdm(store.datasets, desc='write_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def update_jsons():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, datasets)

    for dataset in tqdm(datasets, desc='update_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def insert_datasets():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        validate_datasets(settings.SCHEMA, datasets)
        store.datasets = datasets

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(store.datasets, desc='insert_datasets'.ljust(18)):
        insert_dataset(session, settings.VERSION, settings.RIGHTS,
                       dataset.name, dataset.path, dataset.size, dataset.specifiers)

        for file in dataset.files:
            insert_file(session, settings.VERSION, settings.RIGHTS,
                        file.dataset.path, file.uuid, file.name, file.path,
                        file.size, file.checksum, file.checksum_type, file.specifiers)

        session.commit()

    update_words_view(session)
    update_attributes_view(session)

    session.commit()


def publish_datasets():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        validate_datasets(settings.SCHEMA, datasets)
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
    validate_datasets(settings.SCHEMA, datasets)

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(datasets, desc='update_datasets'.ljust(18)):
        update_dataset(session, settings.RIGHTS, dataset.name, dataset.path, dataset.specifiers)

        for file in dataset.files:
            update_file(session, settings.RIGHTS, file.dataset.path, file.name, file.path, file.specifiers)

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
    db_path = path.parent.as_posix() if path.suffix else path
    db_datasets = retrieve_datasets(session, db_path, public=True)

    # apply include and exclude lists on the datasets from the database
    datasets = filter_datasets(db_datasets, include=settings.INCLUDE, exclude=settings.EXCLUDE)

    for dataset in tqdm(datasets, desc='archive_datasets'.ljust(18)):
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
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    validate_datasets(settings.SCHEMA, datasets)

    session = init_database_session(settings.DATABASE)

    # retrieve all datasets for this path and remove datasets which have no files in public_files
    path = Path(settings.PATH)
    db_path = path.parent.as_posix() if path.suffix else path
    db_datasets = retrieve_datasets(session, db_path, public=True)

    check_datasets(datasets, db_datasets)


def update_index():
    session = init_database_session(settings.DATABASE)

    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()

    update_words_view(session)
    update_attributes_view(session)
    session.commit()


def clean():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH)
    for file_path in local_files:
        delete_file(settings.LOCAL_PATH / file_path)


def insert_doi():
    session = init_database_session(settings.DATABASE)

    for resource in settings.RESOURCES:
        insert_resource(session, resource, settings.ISIMIP_DATA_URL)

    session.commit()


def update_doi():
    session = init_database_session(settings.DATABASE)

    for resource in settings.RESOURCES:
        update_resource(session, resource, settings.ISIMIP_DATA_URL)

    session.commit()


def register_doi():
    print('Registering a DOI with DataCite is permanent. Please type the DOI again to confirm.')
    string = input()

    if string == settings.DOI:
        xml = fetch_datacite_xml(settings.ISIMIP_DATA_URL, settings.DOI)
        upload_doi_metadata(settings.DOI, xml,
                            settings.DATACITE_METADATA_URL, settings.DATACITE_USERNAME, settings.DATACITE_PASSWORD)
        upload_doi(settings.ISIMIP_DATA_URL, settings.DOI,
                   settings.DATACITE_DOI_URL, settings.DATACITE_USERNAME, settings.DATACITE_PASSWORD)
    else:
        print('DOI do not match. Exiting.')


def init():
    init_database_session(settings.DATABASE)
