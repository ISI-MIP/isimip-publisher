from tqdm import tqdm

from .utils import add_version_to_path
from .utils.checksum import write_checksum
from .utils.database import (init_database_session, insert_dataset,
                             insert_file, update_words_view)
from .utils.files import (chmod_file, delete_file, list_local_files,
                          list_remote_files, rename_file,
                          rsync_files_from_remote, rsync_files_to_public)
from .utils.json import write_dataset_json, write_file_json
from .utils.metadata import (get_dataset_metadata, get_file_metadata,
                             get_netcdf_metadata)
from .utils.netcdf import update_netcdf_global_attributes
from .utils.patterns import match_datasets, match_files


def chmod_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)

    for file_path in tqdm(local_files, desc='chmod_files'):
        chmod_file(file_path)


def ingest_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    session = init_database_session()

    for dataset_path, dataset in tqdm(datasets.items(), desc='ingest_datasets'):
        metadata = get_dataset_metadata(config, dataset['identifiers'])
        dataset_version_path = add_version_to_path(dataset_path, version)
        insert_dataset(session, version, config, dataset_version_path, dataset['name'], metadata)

    session.commit()


def ingest_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    session = init_database_session()

    for file_path, file in tqdm(files.items(), desc='ingest_files'):
        metadata = get_file_metadata(config, file['identifiers'])
        dataset_version_path = add_version_to_path(file['dataset_path'], version)
        file_version_path = add_version_to_path(file_path, version)
        insert_file(session, version, config, file_version_path, file['abspath'], file['name'], dataset_version_path, metadata)

    session.commit()


def fetch_files(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)

    t = tqdm(total=len(remote_files), desc='fetch_files')
    for n in rsync_files_from_remote(config, remote_files):
        t.update(n)


def list_local(version, config, filelist=None):
    for file_path in list_local_files(config):
        print(file_path)


def list_remote(version, config, filelist=None):
    for file_path in list_remote_files(config):
        print(file_path)


def match_local_datasets(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)

    for datasets_path in datasets:
        print(datasets_path)


def match_local_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path in files:
        print(file_path)


def match_remote_datasets(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)
    datasets = match_datasets(config, remote_files)

    for datasets_path in datasets:
        print(datasets_path)


def match_remote_files(version, config, filelist=None):
    remote_files = list_remote_files(config, filelist)
    files = match_files(config, remote_files)

    for file_path in files:
        print(file_path)


def publish_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    datasets = match_datasets(config, local_files)
    files = match_files(config, local_files)

    dataset_json_files = [add_version_to_path(dataset['abspath'] + '.json', version) for dataset in datasets.values()]
    nc4_files = [file['abspath'] for file in files.values()]
    json_files = [file.replace('.nc4', '.json') for file in nc4_files]
    sha256_files = [file.replace('.nc4', '.sha256') for file in nc4_files]

    public_files = dataset_json_files + nc4_files + json_files + sha256_files

    t = tqdm(total=len(public_files), desc='publish_files')
    for n in rsync_files_to_public(config, public_files):
        t.update(n)


def update_files(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='update_files'):
        metadata = get_netcdf_metadata(config, file['identifiers'])
        update_netcdf_global_attributes(config, metadata, file['abspath'])

        version_file_path = add_version_to_path(file['abspath'], version)
        if version_file_path != file['abspath']:
            rename_file(file['abspath'], version_file_path)


def update_index(version, config, filelist=None):
    session = init_database_session()
    update_words_view(session)
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
        metadata = get_dataset_metadata(config, dataset['identifiers'])
        dataset_version_path = add_version_to_path(dataset['abspath'], version)
        write_dataset_json(config, metadata, dataset_version_path)


def write_file_jsons(version, config, filelist=None):
    local_files = list_local_files(config, filelist)
    files = match_files(config, local_files)

    for file_path, file in tqdm(files.items(), desc='write_file_jsons'):
        metadata = get_file_metadata(config, file['identifiers'])
        write_file_json(config, metadata, file['abspath'])


def run(version, config, filelist=None):
    fetch_files(version, config, filelist)
    update_files(version, config, filelist)
    write_checksums(version, config, filelist)
    write_dataset_jsons(version, config, filelist)
    write_file_jsons(version, config, filelist)
    ingest_datasets(version, config, filelist)
    ingest_files(version, config, filelist)
    update_index(version, config, filelist)
    publish_files(version, config, filelist)


def run_all(version, config, filelist=None):
    list_remote(version, config, filelist)
    match_remote_datasets(version, config, filelist)
    match_remote_files(version, config, filelist)
    fetch_files(version, config, filelist)
    list_local(version, config, filelist)
    match_local_datasets(version, config, filelist)
    match_local_files(version, config, filelist)
    update_files(version, config, filelist)
    write_checksums(version, config, filelist)
    write_dataset_jsons(version, config, filelist)
    write_file_jsons(version, config, filelist)
    ingest_datasets(version, config, filelist)
    ingest_files(version, config, filelist)
    update_index(version, config, filelist)
    publish_files(version, config, filelist)
