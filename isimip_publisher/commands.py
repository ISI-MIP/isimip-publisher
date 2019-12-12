from tqdm import tqdm

from .utils.checksum import write_checksum
from .utils.database import (init_database_session, insert_dataset,
                             insert_file, update_attributes_view,
                             update_latest_view, update_words_view)
from .utils.files import (chmod_file, copy_files_from_remote,
                          copy_files_to_public, delete_files, list_local_files,
                          list_remote_files)
from .utils.json import write_dataset_json, write_file_json
from .utils.netcdf import update_netcdf_global_attributes
from .utils.patterns import match_datasets, match_files
from .utils.thumbnails import write_dataset_thumbnail, write_file_thumbnail
from .utils.validation import validate_dataset, validate_file


def chmod_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)

    for file_path in tqdm(local_files, desc='chmod_files'):
        chmod_file(file_path)


def clean(version, config, filelist=None):
    delete_files(config)


def ingest_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    session = init_database_session()

    for dataset_path, dataset in tqdm(datasets.items(), desc='ingest_datasets'):
        validate_dataset(config, dataset_path, dataset)
        insert_dataset(session, version, config, dataset_path, dataset['name'], dataset['identifiers'])

    session.commit()


def ingest_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    session = init_database_session()

    for file_path, file in tqdm(files.items(), desc='ingest_files'):
        validate_file(config, file_path, file)
        insert_file(session, version, config, file_path, file['abspath'], file['name'], file['dataset_path'], file['identifiers'])

    session.commit()


def fetch_files(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)

    t = tqdm(total=len(remote_files), desc='fetch_files')
    for n in copy_files_from_remote(config, remote_files):
        t.update(n)


def list_local(version, config, filelist=None):
    for file_path in list_local_files(config, filelist):
        print(file_path)


def list_remote(version, config, filelist=None):
    for file_path in list_remote_files(config, filelist):
        print(file_path)


def match_local_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset_path, dataset in datasets.items():
        validate_dataset(config, dataset_path, dataset)


def match_local_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in files.items():
        validate_file(config, file_path, file)


def match_remote_datasets(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)
    datasets = match_datasets(config, remote_files)

    for dataset_path, dataset in datasets.items():
        validate_dataset(config, dataset_path, dataset)


def match_remote_files(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)
    files = match_files(config, remote_files)

    for file_path, file in files.items():
        validate_file(config, file_path, file)


def publish_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)
    files = match_files(config, local_files)

    public_files = ['%s.json' % dataset['abspath'] for dataset in datasets.values()]
    public_files += ['%s.png' % dataset['abspath'] for dataset in datasets.values()]
    public_files += [file['abspath'] for file in files.values()]
    public_files += [file['abspath'].replace('.nc4', '.json') for file in files.values()]
    public_files += [file['abspath'].replace('.nc4', '.sha256') for file in files.values()]
    public_files += [file['abspath'].replace('.nc4', '.png') for file in files.values()]

    t = tqdm(total=len(public_files), desc='publish_files')
    for n in copy_files_to_public(version, config, public_files):
        t.update(n)


def update_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='update_files'):
        validate_file(config, file_path, file)
        update_netcdf_global_attributes(config, file['abspath'], file['identifiers'])


def update_index(version, config, filelist=None):
    session = init_database_session()

    update_words_view(session)
    session.commit()

    update_latest_view(session)
    session.commit()

    update_attributes_view(session)
    session.commit()


def write_checksums(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='write_checksums'):
        write_checksum(file['abspath'])


def write_dataset_jsons(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset_path, dataset in tqdm(datasets.items(), desc='write_dataset_jsons'):
        validate_dataset(config, dataset_path, dataset)
        write_dataset_json(config, dataset['abspath'], dataset['identifiers'])


def write_file_jsons(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='write_file_jsons'):
        validate_file(config, file_path, file)
        write_file_json(config, file['abspath'], file['identifiers'])


def write_dataset_thumbnails(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for dataset_path, dataset in tqdm(datasets.items(), desc='write_dataset_thumbnails'):
        validate_dataset(config, dataset_path, dataset)
        write_dataset_thumbnail(dataset['abspath'], dataset['files'])


def write_file_thumbnails(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='write_file_thumbnails'):
        validate_file(config, file_path, file)
        write_file_thumbnail(file['abspath'])
