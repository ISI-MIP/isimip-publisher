from tqdm import tqdm

from .utils.checksum import write_checksum
from .utils.database import (init_database_session, insert_dataset,
                             insert_file, publish_dataset, unpublish_dataset,
                             update_attributes_view, update_words_view)
from .utils.files import (delete_files, list_local_files, list_public_files,
                          list_remote_files, move_files_to_archive,
                          move_files_to_public, rsync_files_from_remote)
from .utils.json import write_dataset_json, write_file_json
from .utils.metadata import get_attributes
from .utils.netcdf import update_netcdf_global_attributes
from .utils.patterns import match_datasets, match_files
from .utils.thumbnails import write_dataset_thumbnail, write_file_thumbnail
from .utils.validation import validate_dataset, validate_file


def archive_datasets(version, config, filelist=None):
    public_files = list_public_files(config, filelist)
    datasets = match_datasets(config, public_files)

    session = init_database_session()

    for dataset in tqdm(datasets, desc='archive_datasets'.ljust(17)):
        validate_dataset(config, dataset)
        dataset_version = unpublish_dataset(session, dataset)

        if dataset_version:
            move_files_to_archive(config, dataset_version, [
                dataset['abspath'].with_suffix('.json'),
                dataset['abspath'].with_suffix('.png')
            ])

            for file in dataset['files']:
                validate_file(config, file)
                move_files_to_archive(config, dataset_version, [
                    file['abspath'],
                    file['abspath'].with_suffix('.json'),
                    file['abspath'].with_suffix('.png'),
                    file['abspath'].with_suffix('.sha256')
                ])

        session.commit()


def clean(version, config, filelist=None):
    delete_files(config)


def ingest_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

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
    remote_files = list_remote_files(config, filelist)

    t = tqdm(total=len(remote_files), desc='fetch_files'.ljust(17))
    for n in rsync_files_from_remote(config, remote_files):
        t.update(n)


def list_local(version, config, filelist=None):
    for file_path in list_local_files(config, filelist):
        print(file_path)


def list_public(version, config, filelist=None):
    for file_path in list_public_files(config, filelist):
        print(file_path)


def list_remote(version, config, filelist=None):
    for file_path in list_remote_files(config, filelist):
        print(file_path)


def match_local(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset in datasets:
        validate_dataset(config, dataset)

        for file in dataset['files']:
            validate_file(config, file)


def match_remote(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)
    datasets = match_datasets(config, remote_files)

    for dataset in datasets:
        validate_dataset(config, dataset)

        for file in dataset['files']:
            validate_file(config, file)


def publish_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    session = init_database_session()

    for dataset in tqdm(datasets, desc='publish_datasets'.ljust(17)):
        validate_dataset(config, dataset)
        publish_dataset(session, version, dataset)
        move_files_to_public(config, [
            dataset['abspath'].with_suffix('.json'),
            dataset['abspath'].with_suffix('.png')
        ])

        for file in dataset['files']:
            validate_file(config, file)
            move_files_to_public(config, [
                file['abspath'],
                file['abspath'].with_suffix('.json'),
                file['abspath'].with_suffix('.png'),
                file['abspath'].with_suffix('.sha256')
            ])

        session.commit()


def update_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file in tqdm(files, desc='update_files'.ljust(17)):
        validate_file(config, file)
        attributes = get_attributes(config, file)
        update_netcdf_global_attributes(config, file, attributes)


def write_checksums(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file in tqdm(files, desc='write_checksums'.ljust(17)):
        write_checksum(file)


def write_jsons(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset in tqdm(datasets, desc='write_jsons'.ljust(17)):
        validate_dataset(config, dataset)
        attributes = get_attributes(config, dataset)
        write_dataset_json(config, dataset, attributes)

        for file in dataset['files']:
            validate_file(config, file)
            attributes = get_attributes(config, file)
            write_file_json(config, file, attributes)


def write_thumbnails(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset in tqdm(datasets, desc='write_thumbnails'.ljust(17)):
        validate_dataset(config, dataset)
        write_dataset_thumbnail(dataset)

        for file in dataset['files']:
            validate_file(config, file)
            write_file_thumbnail(file)
