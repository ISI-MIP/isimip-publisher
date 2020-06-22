import os
from pathlib import Path

from tqdm import tqdm

from .utils.database import (init_database_session, update_attributes_view,
                             update_words_view)
from .utils.files import copy_files, delete_files, list_files, move_files
from .utils.patterns import match_datasets


def archive_datasets(store):
    public_path = Path(os.environ['PUBLIC_DIR'])
    archive_path = Path(os.environ['ARCHIVE_DIR']) / store.version
    public_files = list_files(public_path, store.path, store.pattern, filelist=store.filelist)
    store.datasets = match_datasets(store.pattern, public_path, public_files)

    session = init_database_session()

    for dataset in tqdm(store.datasets, desc='archive_datasets'.ljust(18)):
        dataset.validate(store.schema)
        dataset_version = dataset.unpublish(session)

        if dataset_version:
            for file in dataset.files:
                file.validate(store.schema)
                move_files(public_path, archive_path, [
                    file.abspath,
                    file.abspath.with_suffix('.json'),
                    file.abspath.with_suffix('.png')
                ])

        session.commit()


def clean(store):
    local_path = Path(os.environ['LOCAL_DIR'])
    delete_files(local_path, store.path)


def ingest_datasets(store):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(local_path, store.path, store.pattern, filelist=store.filelist)

    if not store.datasets:
        local_files = list_files(local_path, store.path, store.pattern, filelist=store.filelist)
        store.datasets = match_datasets(store.pattern, local_path, local_files)

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


def fetch_files(store):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR'])
    local_path = Path(os.environ['LOCAL_DIR'])
    remote_files = list_files(remote_path, store.path, store.pattern, remote_dest=remote_dest, filelist=store.filelist)

    t = tqdm(total=len(remote_files), desc='fetch_files'.ljust(18))
    for n in copy_files(remote_dest, remote_path, local_path, store.path, remote_files):
        t.update(n)


def list_local(store):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(local_path, store.path, store.pattern, filelist=store.filelist)

    for file_path in local_files:
        print(file_path)


def list_public(store):
    public_path = Path(os.environ['PUBLIC_DIR'])
    public_files = list_files(public_path, store.path, store.pattern, filelist=store.filelist)

    for file_path in public_files:
        print(file_path)


def list_remote(store):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR'])
    remote_files = list_files(remote_path, store.path, store.pattern, remote_dest=remote_dest, filelist=store.filelist)

    for file_path in remote_files:
        print(file_path)


def match_local(store):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(local_path, store.path, store.pattern, filelist=store.filelist)
    store.datasets = match_datasets(store.pattern, local_path, local_files)

    for dataset in store.datasets:
        dataset.validate(store.schema)

        for file in dataset.files:
            file.validate(store.schema)


def match_remote(store):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR'])
    remote_files = list_files(remote_path, store.path, store.pattern, remote_dest=remote_dest, filelist=store.filelist)
    store.datasets = match_datasets(store.pattern, remote_path, remote_files)

    for dataset in store.datasets:
        dataset.validate(store.schema)

        for file in dataset.files:
            file.validate(store.schema)


def publish_datasets(store):
    local_path = Path(os.environ['LOCAL_DIR'])
    public_path = Path(os.environ['PUBLIC_DIR'])

    if not store.datasets:
        local_files = list_files(local_path, store.path, store.pattern, filelist=store.filelist)
        store.datasets = match_datasets(store.pattern, local_path, local_files)

    session = init_database_session()

    for dataset in tqdm(store.datasets, desc='publish_datasets'.ljust(18)):
        dataset.validate(store.schema)
        dataset.publish(session, store.version)

        for file in dataset.files:
            file.validate(store.schema)
            move_files(local_path, public_path, [
                file.abspath,
                file.abspath.with_suffix('.json'),
                file.abspath.with_suffix('.png')
            ])

        session.commit()


def write_jsons(store):
    local_path = Path(os.environ['LOCAL_DIR'])

    if not store.datasets:
        local_files = list_files(local_path, store.path, store.pattern, filelist=store.filelist)
        store.datasets = match_datasets(store.pattern, local_path, local_files)

    for dataset in tqdm(store.datasets, desc='write_jsons'.ljust(18)):
        for file in dataset.files:
            file.validate(store.schema)
            file.write_json()


def write_thumbnails(store):
    local_path = Path(os.environ['LOCAL_DIR'])

    if not store.datasets:
        local_files = list_files(local_path, store.path, store.pattern, filelist=store.filelist)
        store.datasets = match_datasets(store.pattern, local_path, local_files)

    for dataset in tqdm(store.datasets, desc='write_thumbnails'.ljust(18)):
        for file in dataset.files:
            file.validate(store.schema)
            file.write_thumbnail()
