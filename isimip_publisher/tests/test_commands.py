import os
import shutil

import pytest
from isimip_publisher.utils import setup_env
from isimip_publisher.utils.database import (Dataset, File,
                                             init_database_session)


@pytest.fixture(scope='session')
def setup():
    setup_env()

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    test_dir = os.path.join(base_dir, 'testing')
    work_dir = os.path.join(test_dir, 'work')
    public_dir = os.path.join(test_dir, 'public')

    shutil.rmtree(work_dir, ignore_errors=True)
    shutil.rmtree(public_dir, ignore_errors=True)

    session = init_database_session()
    session.query(File).delete()
    session.query(Dataset).delete()
    session.commit()


def test_empty(setup, script_runner):
    response = script_runner.run('isimip-publisher')
    assert response.returncode == 2


def test_help(setup, script_runner):
    response = script_runner.run('isimip-publisher', '--help')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr


def test_list_remote(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'list_remote')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_remote_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'match_remote_datasets')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_match_remote_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'match_remote_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_fetch_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'fetch_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('fetch_files')


def test_fetch_files_error(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'fetch_files')
    assert not response.success
    assert not response.stdout


def test_list_local(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'list_local')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_local_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'match_local_datasets')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_match_local_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'match_local_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'update_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('update_files')


def test_write_dataset_jsons(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'write_dataset_jsons')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_dataset_jsons')


def test_write_file_jsons(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'write_file_jsons')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_file_jsons')


def test_write_dataset_thumbnails(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'write_dataset_thumbnails')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_dataset_thumbnails')


def test_write_file_thumbnails(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'write_file_thumbnails')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_file_thumbnails')


def test_write_checksums(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'write_checksums')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_checksums')


def test_ingest_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'ingest_datasets')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('ingest_datasets')


def test_ingest_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'ingest_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('ingest_files')


def test_update_index(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'update_index')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_publish_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'publish_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_files')


def test_clean(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'test-round',
        'test-product',
        'test-sector',
        'test-model',
        'clean')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
