import logging
from pathlib import Path

from tqdm import tqdm

from .config import settings, store
from .utils.checksum import write_checksum_file
from .utils.database import (clean_tree, init_database_session, insert_dataset,
                             insert_file, insert_resource, publish_dataset,
                             retrieve_datasets, unpublish_dataset,
                             update_attributes_view, update_tree,
                             update_words_view)
from .utils.files import copy_files, delete_files, list_files, move_files
from .utils.json import write_json_file
from .utils.patterns import match_datasets
from .utils.region import get_region
from .utils.thumbnails import write_thumbnail_file

logger = logging.getLogger(__name__)


def list_local(path):
    local_files = list_files(settings.LOCAL_PATH, path, settings.PATTERN,
                             include=settings.INCLUDE, exclude=settings.EXCLUDE)
    for file_path in local_files:
        print(file_path)


def list_public(path):
    public_files = list_files(settings.PUBLIC_PATH, path, settings.PATTERN,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    for file_path in public_files:
        print(file_path)


def list_remote(path):
    remote_files = list_files(settings.REMOTE_PATH, path, settings.PATTERN,
                              remote_dest=settings.REMOTE_DEST, include=settings.INCLUDE, exclude=settings.EXCLUDE)
    for file_path in remote_files:
        print(file_path)


def match_remote(path):
    remote_files = list_files(settings.REMOTE_PATH, path, settings.PATTERN,
                              remote_dest=settings.REMOTE_DEST, include=settings.INCLUDE, exclude=settings.EXCLUDE)

    for dataset in match_datasets(settings.PATTERN, settings.REMOTE_PATH, remote_files):
        dataset.validate(settings.SCHEMA)
        for file in dataset.files:
            file.validate(settings.SCHEMA)


def match_local(path):
    local_files = list_files(settings.LOCAL_PATH, path, settings.PATTERN,
                             include=settings.INCLUDE, exclude=settings.EXCLUDE)

    for dataset in match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files):
        dataset.validate(settings.SCHEMA)
        for file in dataset.files:
            file.validate(settings.SCHEMA)


def match_public(path):
    public_files = list_files(settings.PUBLIC_PATH, path, settings.PATTERN,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)

    for dataset in match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files):
        dataset.validate(settings.SCHEMA)
        for file in dataset.files:
            file.validate(settings.SCHEMA)


def fetch_files(path):
    remote_files = list_files(settings.REMOTE_PATH, path, settings.PATTERN,
                              remote_dest=settings.REMOTE_DEST, include=settings.INCLUDE, exclude=settings.EXCLUDE)

    t = tqdm(total=len(remote_files), desc='fetch_files'.ljust(18))
    for n in copy_files(settings.REMOTE_DEST, settings.REMOTE_PATH, settings.LOCAL_PATH, path, remote_files):
        t.update(n)


def write_thumbnails(path):
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, path, settings.PATTERN,
                                 include=settings.INCLUDE, exclude=settings.EXCLUDE)
        store.datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)

        for dataset in store.datasets:
            dataset.validate(settings.SCHEMA)
            for file in dataset.files:
                file.validate(settings.SCHEMA)

    for dataset in tqdm(store.datasets, desc='write_thumbnails'.ljust(18)):
        region = get_region(settings.DEFINITIONS, dataset.specifiers)

        for file in dataset.files:
            write_thumbnail_file(file.abspath, region)


def write_jsons(path):
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, path, settings.PATTERN,
                                 include=settings.INCLUDE, exclude=settings.EXCLUDE)
        store.datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)

        for dataset in store.datasets:
            dataset.validate(settings.SCHEMA)
            for file in dataset.files:
                file.validate(settings.SCHEMA)

    for dataset in tqdm(store.datasets, desc='write_jsons'.ljust(18)):
        for file in dataset.files:
            write_json_file(file.abspath, file.json)


def write_checksums(path):
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, path, settings.PATTERN,
                                 include=settings.INCLUDE, exclude=settings.EXCLUDE)
        store.datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)

        for dataset in store.datasets:
            dataset.validate(settings.SCHEMA)
            for file in dataset.files:
                file.validate(settings.SCHEMA)

    for dataset in tqdm(store.datasets, desc='write_checksums'.ljust(18)):
        for file in dataset.files:
            write_checksum_file(file.abspath, file.checksum, file.path)


def ingest_datasets(path):
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, path, settings.PATTERN,
                                 include=settings.INCLUDE, exclude=settings.EXCLUDE)
        store.datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)

        for dataset in store.datasets:
            dataset.validate(settings.SCHEMA)
            for file in dataset.files:
                file.validate(settings.SCHEMA)

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(store.datasets, desc='ingest_datasets'.ljust(18)):
        insert_dataset(session, settings.VERSION, dataset.name, dataset.path, dataset.size, dataset.specifiers)

        for file in dataset.files:
            insert_file(session, settings.VERSION, file.dataset.path, file.uuid, file.name, file.path,
                        file.size, file.checksum, file.checksum_type, file.specifiers)

        session.commit()

    update_words_view(session)
    update_attributes_view(session)

    session.commit()


def publish_datasets(path):
    if not store.datasets:
        local_files = list_files(settings.LOCAL_PATH, path, settings.PATTERN,
                                 include=settings.INCLUDE, exclude=settings.EXCLUDE)
        store.datasets = match_datasets(settings.PATTERN, settings.LOCAL_PATH, local_files)

    for dataset in store.datasets:
        dataset.validate(settings.SCHEMA)
        for file in dataset.files:
            file.validate(settings.SCHEMA)

            assert Path(file.abspath).is_file()
            assert Path(file.abspath).with_suffix('.json').is_file()
            assert Path(file.abspath).with_suffix('.png').is_file()

    session = init_database_session(settings.DATABASE)

    for dataset in tqdm(store.datasets, desc='publish_datasets'.ljust(18)):
        publish_dataset(session, settings.VERSION, dataset.path)

        for file in dataset.files:
            move_files(settings.LOCAL_PATH, settings.PUBLIC_PATH, [
                Path(file.abspath),
                Path(file.abspath).with_suffix('.png'),
                Path(file.abspath).with_suffix('.' + file.checksum_type),
                Path(file.abspath).with_suffix('.json')
            ])

        session.commit()

    update_tree(session, path, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def archive_datasets(path):
    public_files = list_files(settings.PUBLIC_PATH, path, settings.PATTERN,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)

    session = init_database_session(settings.DATABASE)

    # remove datasets from db_datasets which have no files in public_files
    db_datasets = []
    for db_dataset in retrieve_datasets(session, path, public=True):
        if any([file.path in public_files for file in db_dataset.files]):
            db_datasets.append(db_dataset)

    for db_dataset in tqdm(db_datasets, desc='archive_datasets'.ljust(18)):
        dataset_version = unpublish_dataset(session, db_dataset.path)

        if dataset_version:
            archive_path = settings.ARCHIVE_PATH / dataset_version

            for file in db_dataset.files:
                files = []
                file_abspath = settings.PUBLIC_PATH / file.path
                if file_abspath.is_file():
                    files.append(file_abspath)
                for suffix in ['.png', '.' + file.checksum_type, '.json']:
                    if file_abspath.with_suffix(suffix).is_file():
                        files.append(file_abspath.with_suffix(suffix))

                move_files(settings.PUBLIC_PATH, archive_path, files)

        session.commit()

    update_tree(session, path, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()


def ingest_resource(path):
    session = init_database_session(settings.DATABASE)

    datasets = retrieve_datasets(session, path, public=True)

    insert_resource(session, path, settings.VERSION, settings.DATACITE, settings.ISIMIP_DATA_URL, datasets)

    session.commit()


def update_resource(path):
    session = init_database_session(settings.DATABASE)

    datasets = retrieve_datasets(session, path, public=True)

    insert_resource(session, path, settings.VERSION, settings.DATACITE, settings.ISIMIP_DATA_URL, datasets, update=True)

    session.commit()


def check(path):
    public_files = list_files(settings.PUBLIC_PATH, path, settings.PATTERN,
                              include=settings.INCLUDE, exclude=settings.EXCLUDE)
    datasets = match_datasets(settings.PATTERN, settings.PUBLIC_PATH, public_files)

    for dataset in datasets:
        dataset.validate(settings.SCHEMA)
        for file in dataset.files:
            file.validate(settings.SCHEMA)

    session = init_database_session(settings.DATABASE)

    # remove datasets from db_datasets which have no files in public_files
    db_datasets = []
    for db_dataset in retrieve_datasets(session, path, public=True):
        if any([file.path in public_files for file in db_dataset.files]):
            db_datasets.append(db_dataset)

    assert len(datasets) == len(db_datasets), \
        'Length mismatch {} != {}'.format(len(datasets), len(db_datasets))

    for dataset, db_dataset in zip(datasets, db_datasets):
        for file, db_file in zip(dataset.files, db_dataset.files):
            # check file
            assert file.path == db_file.path, \
                'Path mismatch {} != {} for file {}'.format(file.path, db_file.path, db_file.id)

            if file.uuid:
                assert str(file.uuid) == db_file.id, \
                    'UUID mismatch {} != {} for file {}'.format(file.uuid, db_file.id, db_file.id)

            # patch checksum_type in order to compute checksum with a non default checksum_type
            file.checksum_type = db_file.checksum_type
            assert file.checksum == db_file.checksum, \
                'Checksum mismatch {} != {} for file {}'.format(file.checksum, db_file.checksum, db_file.id)

        # check dataset
        assert dataset.path == db_dataset.path, \
            'Path mismatch {} != {} for dataset {}'.format(dataset.path, db_dataset.path, db_dataset.id)


def clean(path):
    delete_files(settings.LOCAL_PATH, path)


def update_index(path):
    session = init_database_session(settings.DATABASE)

    update_tree(session, path, settings.TREE)
    session.commit()
    clean_tree(session)
    session.commit()

    update_words_view(session)
    update_attributes_view(session)
    session.commit()
