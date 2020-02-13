from tqdm import tqdm

from .utils.checksum import write_checksum
from .utils.database import (commit_ingest, init_database_session,
                             insert_dataset, insert_file)
from .utils.files import (copy_files_from_remote, copy_files_to_public,
                          delete_files, list_local_files, list_public_files,
                          list_remote_files, move_files_to_archive)
from .utils.json import write_dataset_json, write_file_json
from .utils.metadata import get_attributes
from .utils.netcdf import update_netcdf_global_attributes
from .utils.patterns import match_datasets, match_files
from .utils.thumbnails import write_dataset_thumbnail, write_file_thumbnail
from .utils.validation import validate_dataset, validate_file


def archive_datasets(version, config, filelist=None):
    public_files = list_public_files(config, filelist)
    datasets = match_datasets(config, public_files)
    files = match_files(config, public_files)

    archive_files = ['%s.json' % dataset['abspath'] for dataset in datasets.values()]
    archive_files += ['%s.png' % dataset['abspath'] for dataset in datasets.values()]
    archive_files += [file['abspath'] for file in files.values()]
    archive_files += [file['abspath'].replace('.nc4', '.json') for file in files.values()]
    archive_files += [file['abspath'].replace('.nc4', '.sha256') for file in files.values()]
    archive_files += [file['abspath'].replace('.nc4', '.png') for file in files.values()]

    t = tqdm(total=len(archive_files), desc='archive_datasets'.ljust(17))
    for n in move_files_to_archive(version, config, archive_files):
        t.update(n)


def clean(version, config, filelist=None):
    delete_files(config)


def ingest_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    session = init_database_session()

    for dataset_path, dataset in tqdm(datasets.items(), desc='ingest_datasets'.ljust(17)):
        validate_dataset(config, dataset_path, dataset)
        attributes = get_attributes(config, dataset['identifiers'])
        insert_dataset(session, version, config, dataset_path, dataset['name'], attributes)

        files = match_files(config, dataset['files'])
        for file_path, file in files.items():
            validate_file(config, file_path, file)
            attributes = get_attributes(config, file['identifiers'])
            insert_file(session, version, config, file_path, file['abspath'], file['name'],
                        file['dataset_path'], attributes)

    commit_ingest(session)


def fetch_files(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)

    t = tqdm(total=len(remote_files), desc='fetch_files'.ljust(17))
    for n in copy_files_from_remote(config, remote_files):
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

    for dataset_path, dataset in datasets.items():
        validate_dataset(config, dataset_path, dataset)

        files = match_files(config, dataset['files'])
        for file_path, file in files.items():
            validate_file(config, file_path, file)


def match_remote(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)
    datasets = match_datasets(config, remote_files)

    for dataset_path, dataset in datasets.items():
        validate_dataset(config, dataset_path, dataset)

        files = match_files(config, dataset['files'])
        for file_path, file in files.items():
            validate_file(config, file_path, file)


def publish_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)
    files = match_files(config, local_files)

    public_files = ['%s.json' % dataset['abspath'] for dataset in datasets.values()]
    public_files += ['%s.png' % dataset['abspath'] for dataset in datasets.values()]
    public_files += [file['abspath'] for file in files.values()]
    public_files += [file['abspath'].replace('.nc4', '.json') for file in files.values()]
    public_files += [file['abspath'].replace('.nc4', '.sha256') for file in files.values()]
    public_files += [file['abspath'].replace('.nc4', '.png') for file in files.values()]

    t = tqdm(total=len(public_files), desc='publish_datasets'.ljust(17))
    for n in copy_files_to_public(version, config, public_files):
        t.update(n)


def update_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='update_files'.ljust(17)):
        validate_file(config, file_path, file)
        attributes = get_attributes(config, file['identifiers'])
        update_netcdf_global_attributes(config, file['abspath'], attributes)


def write_checksums(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='write_checksums'.ljust(17)):
        write_checksum(file['abspath'])


def write_jsons(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset_path, dataset in tqdm(datasets.items(), desc='write_jsons'.ljust(17)):
        validate_dataset(config, dataset_path, dataset)
        attributes = get_attributes(config, dataset['identifiers'])
        write_dataset_json(config, dataset['abspath'], attributes)

        files = match_files(config, dataset['files'])
        for file_path, file in files.items():
            validate_file(config, file_path, file)
            attributes = get_attributes(config, file['identifiers'])
            write_file_json(config, file['abspath'], attributes)


def write_thumbnails(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset_path, dataset in tqdm(datasets.items(), desc='write_thumbnails'.ljust(17)):
        validate_dataset(config, dataset_path, dataset)
        write_dataset_thumbnail(dataset['abspath'], dataset['files'])

        files = match_files(config, dataset['files'])
        for file_path, file in files.items():
            validate_file(config, file_path, file)
            write_file_thumbnail(file['abspath'])
