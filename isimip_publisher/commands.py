import os
from pathlib import Path

from tqdm import tqdm

from .utils.database import (init_database_session, insert_resource,
                             retrieve_datasets, update_attributes_view,
                             update_words_view)
from .utils.files import copy_files, delete_files, list_files, move_files
from .utils.patterns import match_datasets


def archive_datasets(store):
    if not store.datasets:
        public_files = list_files(store.public_path, store.path, store.pattern,
                                  include=store.include, exclude=store.exclude)
        store.datasets = match_datasets(store.pattern, store.public_path, public_files)

    session = init_database_session()

    for dataset in tqdm(store.datasets, desc='archive_datasets'.ljust(18)):
        dataset.validate(store.schema)
        dataset_version = dataset.unpublish(session)

        if dataset_version:
            archive_path = Path(os.environ['ARCHIVE_DIR']) / dataset_version

            for file in dataset.files:
                file.validate(store.schema)
                move_files(store.public_path, archive_path, [
                    file.abspath,
                    file.abspath.with_suffix('.json'),
                    file.abspath.with_suffix('.png')
                ])

        session.commit()


def check(store):
    public_files = list_files(store.public_path, store.path, store.pattern,
                              include=store.include, exclude=store.exclude)
    store.datasets = match_datasets(store.pattern, store.public_path, public_files)

    session = init_database_session()

    db_datasets = retrieve_datasets(session, store.path, public=True)

    assert len(store.datasets) == len(db_datasets)

    for dataset, db_dataset in zip(store.datasets, db_datasets):
        for file, db_file in zip(dataset.files, db_dataset.files):
            file.validate(store.schema)
            file.check(db_file)
        dataset.validate(store.schema)
        dataset.check(db_dataset)


def clean(store):
    delete_files(store.local_path, store.path)


def ingest_datasets(store):
    if not store.datasets:
        local_files = list_files(store.local_path, store.path, store.pattern,
                                 include=store.include, exclude=store.exclude)
        store.datasets = match_datasets(store.pattern, store.local_path, local_files)

    session = init_database_session()

    for dataset in tqdm(store.datasets, desc='ingest_datasets'.ljust(18)):
        dataset.validate(store.schema)
        dataset.insert(session, store.version)

        for file in dataset.files:
            file.validate(store.schema)
            file.insert(session, store.version)

        session.commit()

    update_words_view(session)
    update_attributes_view(session)
    session.commit()


def ingest_resource(store):
    public_files = list_files(store.public_path, store.path, store.pattern,
                              include=store.include, exclude=store.exclude)
    store.datasets = match_datasets(store.pattern, store.public_path, public_files)

    session = init_database_session()

    db_datasets = retrieve_datasets(session, store.path, public=True)

    assert len(store.datasets) == len(db_datasets)

    for dataset, db_dataset in zip(store.datasets, db_datasets):
        for file, db_file in zip(dataset.files, db_dataset.files):
            file.validate(store.schema)
            file.check(db_file)
        dataset.validate(store.schema)
        dataset.check(db_dataset)

        store.datacite['relatedIdentifiers'].append({
            'relationType': 'HasPart',
            'relatedIdentifier': store.datasets_base_url + db_dataset.id,
            'relatedIdentifierType': 'URL'
        })

    insert_resource(session, store.path, store.version, store.datacite, db_datasets)
    session.commit()


def fetch_files(store):
    remote_files = list_files(store.remote_path, store.path, store.pattern,
                              remote_dest=store.remote_dest, include=store.include, exclude=store.exclude)

    t = tqdm(total=len(remote_files), desc='fetch_files'.ljust(18))
    for n in copy_files(store.remote_dest, store.remote_path, store.local_path, store.path,
                        remote_files, mock=store.mock):
        t.update(n)


def list_local(store):
    local_files = list_files(store.local_path, store.path, store.pattern,
                             include=store.include, exclude=store.exclude)
    for file_path in local_files:
        print(file_path)


def list_public(store):
    public_files = list_files(store.public_path, store.path, store.pattern,
                              include=store.include, exclude=store.exclude)
    for file_path in public_files:
        print(file_path)


def list_remote(store):
    remote_files = list_files(store.remote_path, store.path, store.pattern,
                              remote_dest=store.remote_dest, include=store.include, exclude=store.exclude)
    for file_path in remote_files:
        print(file_path)


def match_local(store):
    local_files = list_files(store.local_path, store.path, store.pattern,
                             include=store.include, exclude=store.exclude)
    store.datasets = match_datasets(store.pattern, store.local_path, local_files)

    for dataset in store.datasets:
        dataset.validate(store.schema)

        for file in dataset.files:
            file.validate(store.schema)


def match_remote(store):
    remote_files = list_files(store.remote_path, store.path, store.pattern,
                              remote_dest=store.remote_dest, include=store.include, exclude=store.exclude)
    store.datasets = match_datasets(store.pattern, store.remote_path, remote_files)

    for dataset in store.datasets:
        dataset.validate(store.schema)

        for file in dataset.files:
            file.validate(store.schema)


def match_public(store):
    public_files = list_files(store.public_path, store.path, store.pattern,
                              include=store.include, exclude=store.exclude)
    store.datasets = match_datasets(store.pattern, store.public_path, public_files)

    for dataset in store.datasets:
        dataset.validate(store.schema)

        for file in dataset.files:
            file.validate(store.schema)


def publish_datasets(store):
    if not store.datasets:
        local_files = list_files(store.local_path, store.path, store.pattern,
                                 include=store.include, exclude=store.exclude)
        store.datasets = match_datasets(store.pattern, store.local_path, local_files)

    session = init_database_session()

    for dataset in tqdm(store.datasets, desc='publish_datasets'.ljust(18)):
        dataset.validate(store.schema)
        dataset.publish(session, store.version)

        for file in dataset.files:
            file.validate(store.schema)
            move_files(store.local_path, store.public_path, [
                file.abspath,
                file.abspath.with_suffix('.json'),
                file.abspath.with_suffix('.png')
            ])

        session.commit()


def write_jsons(store):
    if not store.datasets:
        local_files = list_files(store.local_path, store.path, store.pattern,
                                 include=store.include, exclude=store.exclude)
        store.datasets = match_datasets(store.pattern, store.local_path, local_files)

    for dataset in tqdm(store.datasets, desc='write_jsons'.ljust(18)):
        for file in dataset.files:
            file.validate(store.schema)
            file.write_json()


def write_thumbnails(store):
    if not store.datasets:
        local_files = list_files(store.local_path, store.path, store.pattern,
                                 include=store.include, exclude=store.exclude)
        store.datasets = match_datasets(store.pattern, store.local_path, local_files)

    for dataset in tqdm(store.datasets, desc='write_thumbnails'.ljust(18)):
        for file in dataset.files:
            file.validate(store.schema)
            file.write_thumbnail(mock=store.mock)
