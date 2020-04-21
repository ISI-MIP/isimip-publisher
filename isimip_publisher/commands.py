import os
from pathlib import Path

from tqdm import tqdm

from .utils.database import (init_database_session, insert_dataset,
                             insert_file, publish_dataset, unpublish_dataset,
                             update_attributes_view, update_words_view)
from .utils.files import copy_files, delete_files, list_files, move_files
from .utils.json import write_file_json
from .utils.metadata import get_attributes
from .utils.netcdf import update_netcdf_global_attributes
from .utils.patterns import match_datasets, match_files
from .utils.thumbnails import write_thumbnail
from .utils.validation import validate_dataset, validate_file


def archive_datasets(version, config, filelist=None):
    public_path = Path(os.environ['PUBLIC_DIR'])
    archive_path = Path(os.environ['ARCHIVE_DIR']) / version
    public_files = list_files(config, public_path, filelist=filelist)
    datasets = match_datasets(config, public_path, public_files)

    session = init_database_session()

    for dataset in tqdm(datasets, desc='archive_datasets'.ljust(17)):
        validate_dataset(config, dataset)
        dataset_version = unpublish_dataset(session, dataset)
        if dataset_version:
            for file in dataset['files']:
                validate_file(config, file)
                move_files(public_path, archive_path, [
                    file['abspath'],
                    file['abspath'].with_suffix('.json'),
                    file['abspath'].with_suffix('.png')
                ])

        session.commit()


def clean(version, config, filelist=None):
    delete_files(config)


def ingest_datasets(version, config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(config, local_path, filelist=filelist)
    datasets = match_datasets(config, local_path, local_files)

    session = init_database_session()

    for dataset in tqdm(datasets, desc='ingest_datasets'.ljust(17)):
        validate_dataset(config, dataset)
        attributes = get_attributes(config, dataset)
        insert_dataset(session, version, config, dataset, attributes)

        for file in dataset['files']:
            validate_file(config, file)
            attributes = get_attributes(config, file)
            insert_file(session, version, config, file, attributes)

        session.commit()

    update_words_view(session)
    update_attributes_view(session)
    session.commit()


def fetch_files(version, config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR'])
    local_path = Path(os.environ['LOCAL_DIR'])
    remote_files = list_files(config, remote_path, remote_dest=remote_dest, filelist=filelist)

    t = tqdm(total=len(remote_files), desc='fetch_files'.ljust(17))
    for n in copy_files(config, remote_dest, remote_path, local_path, remote_files):
        t.update(n)


def list_local(version, config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(config, local_path, filelist=filelist)

    for file_path in local_files:
        print(file_path)


def list_public(version, config, filelist=None):
    public_path = Path(os.environ['PUBLIC_DIR'])
    public_files = list_files(config, public_path, filelist=filelist)

    for file_path in public_files:
        print(file_path)


def list_remote(version, config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR'])
    remote_files = list_files(config, remote_path, remote_dest=remote_dest, filelist=filelist)

    for file_path in remote_files:
        print(file_path)


def match_local(version, config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(config, local_path, filelist=filelist)
    datasets = match_datasets(config, local_path, local_files)

    for dataset in datasets:
        validate_dataset(config, dataset)

        for file in dataset['files']:
            validate_file(config, file)


def match_remote(version, config, filelist=None):
    remote_dest = os.environ['REMOTE_DEST']
    remote_path = Path(os.environ['REMOTE_DIR'])
    remote_files = list_files(config, remote_path, remote_dest=remote_dest, filelist=filelist)
    datasets = match_datasets(config, remote_path, remote_files)

    for dataset in datasets:
        validate_dataset(config, dataset)

        for file in dataset['files']:
            validate_file(config, file)


def publish_datasets(version, config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR'])
    public_path = Path(os.environ['PUBLIC_DIR'])
    local_files = list_files(config, local_path, filelist=filelist)
    datasets = match_datasets(config, local_path, local_files)

    session = init_database_session()

    for dataset in tqdm(datasets, desc='publish_datasets'.ljust(17)):
        validate_dataset(config, dataset)
        publish_dataset(session, version, dataset)

        for file in dataset['files']:
            validate_file(config, file)
            move_files(local_path, public_path, [
                file['abspath'],
                file['abspath'].with_suffix('.json'),
                file['abspath'].with_suffix('.png')
            ])

        session.commit()


def update_files(version, config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(config, local_path, filelist=filelist)
    files = match_files(config, local_path, local_files)

    for file in tqdm(files, desc='update_files'.ljust(17)):
        validate_file(config, file)
        attributes = get_attributes(config, file)
        update_netcdf_global_attributes(config, file, attributes)


def write_jsons(version, config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(config, local_path, filelist=filelist)
    files = match_files(config, local_path, local_files)

    for file in tqdm(files, desc='write_jsons'.ljust(17)):
        validate_file(config, file)
        attributes = get_attributes(config, file)
        write_file_json(config, file, attributes)


def write_thumbnails(version, config, filelist=None):
    local_path = Path(os.environ['LOCAL_DIR'])
    local_files = list_files(config, local_path, filelist=filelist)
    files = match_files(config, local_path, local_files)

    for file in tqdm(files, desc='write_thumbnails'.ljust(17)):
        validate_file(config, file)
        write_thumbnail(file)
