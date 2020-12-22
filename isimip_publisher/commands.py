import logging
from pathlib import Path

from tqdm import tqdm

from .config import settings, store
from .utils.checksum import get_checksum_suffix, write_checksum_file
from .utils.database import (clean_tree, init_database_session, insert_dataset,
                             insert_file, insert_resource, publish_dataset,
                             retrieve_datasets, unpublish_dataset,
                             update_attributes_view, update_dataset,
                             update_file, update_resource, update_tree,
                             update_words_view)
from .utils.datacite import gather_related_identifiers
from .utils.files import copy_files, delete_file, list_files, move_file
from .utils.json import write_json_file
from .utils.patterns import match_datasets
from .utils.region import get_region
from .utils.thumbnails import write_thumbnail_file
from .utils.validation import check_datasets, validate_datasets

logger = logging.getLogger(__name__)


def list_local():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    for file_path in local_files:
        print(file_path)


def list_public():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    for file_path in public_files:
        print(file_path)


def list_remote():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    for file_path in remote_files:
        print(file_path)


def match_remote():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])
    datasets = match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_files)
    validate_datasets(settings.SCHEMA, datasets)


def match_local():
    local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)
    validate_datasets(settings.SCHEMA, datasets)


def match_public():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files)
    validate_datasets(settings.SCHEMA, datasets)


def fetch_files():
    remote_files = list_files(settings.REMOTE_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE,
                              remote_dest=settings.REMOTE_DEST, suffix=settings.PATTERN['suffix'])

    t = tqdm(total=len(remote_files), desc='fetch_files'.ljust(18))
    for n in copy_files(settings.REMOTE_DEST, settings.REMOTE_PATH, settings.LOCAL_PATH, settings.PATH, remote_files):
        t.update(n)


def write_thumbnails():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)
        validate_datasets(settings.SCHEMA, datasets)
        store.datasets = datasets

    for dataset in tqdm(store.datasets, desc='write_thumbnails'.ljust(18)):
        region = get_region(settings.DEFINITIONS, dataset.specifiers)

        for file in dataset.files:
            write_thumbnail_file(file.abspath, region)


def update_thumbnails():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files)
    validate_datasets(settings.SCHEMA, datasets)

    for dataset in tqdm(datasets, desc='write_thumbnails'.ljust(18)):
        region = get_region(settings.DEFINITIONS, dataset.specifiers)

        for file in dataset.files:
            write_thumbnail_file(file.abspath, region)


def write_jsons():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)
        validate_datasets(settings.SCHEMA, datasets)
        store.datasets = datasets

    for dataset in tqdm(store.datasets, desc='write_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def update_jsons():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files)
    validate_datasets(settings.SCHEMA, datasets)

    for dataset in tqdm(datasets, desc='update_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def write_checksums():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)
        validate_datasets(settings.SCHEMA, datasets)
        store.datasets = datasets

    for dataset in tqdm(store.datasets, desc='write_checksums'.ljust(18)):
        for file in dataset.files:
            write_checksum_file(file.abspath, file.checksum, file.path)


def insert_datasets():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)
        validate_datasets(settings.SCHEMA, datasets)
        store.datasets = datasets

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(store.datasets, desc='insert_datasets'.ljust(18)):
        insert_dataset(session, settings.VERSION, dataset.name, dataset.path, dataset.size, dataset.specifiers)

        for file in dataset.files:
            insert_file(session, settings.VERSION, file.dataset.path, file.uuid, file.name, file.path,
                        file.size, file.checksum, file.checksum_type, file.specifiers)

        session.commit()

    update_words_view(session)
    update_attributes_view(session)

    session.commit()


def publish_datasets():
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
        datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)
        validate_datasets(settings.SCHEMA, datasets)
        store.datasets = datasets

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(store.datasets, desc='publish_datasets'.ljust(18)):
        publish_dataset(session, settings.VERSION, dataset.path)

        for file in dataset.files:
            source_path = Path(file.abspath)
            target_path = Path(settings.PUBLIC_PATH) / Path(source_path).relative_to(settings.LOCAL_PATH)

            move_file(source_path, target_path)
            for suffix in [get_checksum_suffix(), '.png', '.json']:
                move_file(source_path.with_suffix(suffix), target_path.with_suffix(suffix))

        session.commit()

    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def update_datasets():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files)
    validate_datasets(settings.SCHEMA, datasets)

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(datasets, desc='update_datasets'.ljust(18)):
        update_dataset(session, dataset.name, dataset.path, dataset.specifiers)

        for file in dataset.files:
            update_file(session, file.dataset.path, file.name, file.path, file.specifiers)

        session.commit()

    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def archive_datasets():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)

    session = init_database_session(settings.DATABASE)

    # since we have only files, not datasets (patterns could have changed since publication),
    # we retrieve all datasets for this path and remove datasets which have no files in public_files
    db_datasets = []
    for db_dataset in retrieve_datasets(session, settings.PATH, public=True):
        if any([file.path in public_files for file in db_dataset.files]):
            db_datasets.append(db_dataset)

    for dataset in tqdm(db_datasets, desc='archive_datasets'.ljust(18)):
        dataset_version = unpublish_dataset(session, dataset.path)

        if dataset_version:
            archive_path = settings.ARCHIVE_PATH / dataset_version

            for file in dataset.files:
                source_path = settings.PUBLIC_PATH / file.path
                target_path = archive_path / Path(source_path).relative_to(settings.PUBLIC_PATH)

                if source_path.is_file():
                    move_file(source_path, target_path)

                for suffix in [get_checksum_suffix(), '.png', '.json']:
                    if source_path.with_suffix(suffix).is_file():
                        move_file(source_path.with_suffix(suffix), target_path.with_suffix(suffix))

        session.commit()

    update_tree(session, settings.PATH, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def check():
    public_files = list_files(settings.PUBLIC_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files)
    validate_datasets(settings.SCHEMA, datasets)

    session = init_database_session(settings.DATABASE)

    # retrieve all datasets for this path and remove datasets which have no files in public_files
    db_datasets = []
    for db_dataset in retrieve_datasets(session, settings.PATH, public=True):
        if any([file.path in public_files for file in db_dataset.files]):
            db_datasets.append(db_dataset)

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
    local_files = list_files(settings.LOCAL_PATH, settings.PATH, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    for file_path in local_files:
        delete_file(settings.LOCAL_PATH / file_path)


def insert_doi():
    session = init_database_session(settings.DATABASE)

    datasets = []
    for path in settings.RESOURCE.get('path', []):
        datasets += retrieve_datasets(session, path, public=True)

    gather_related_identifiers(settings.RESOURCE, settings.ISIMIP_DATA_URL, datasets)

    insert_resource(session, settings.DOI, settings.RESOURCE.get('datacite'), datasets)

    session.commit()


def update_doi():
    session = init_database_session(settings.DATABASE)

    datasets = []
    for path in settings.RESOURCE.get('path', []):
        datasets += retrieve_datasets(session, path, public=True)

    gather_related_identifiers(settings.RESOURCE, settings.ISIMIP_DATA_URL, datasets)

    update_resource(session, settings.DOI, settings.RESOURCE.get('datacite'), datasets)

    session.commit()
