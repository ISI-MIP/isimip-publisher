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
        'round/product/sector/model',
        'list_remote')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_remote(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'match_remote')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_fetch_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'fetch_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('fetch_files')


def test_fetch_files_error(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'fetch_files')
    assert not response.success
    assert not response.stdout


def test_list_local(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'list_local')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_local(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'match_local')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'update_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('update_files')


def test_write_jsons(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'write_jsons')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_jsons')


def test_write_thumbnails(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'write_thumbnails')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_thumbnails')


def test_write_checksums(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'write_checksums')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_checksums')


def test_ingest_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'ingest_datasets')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('ingest_datasets')


def test_publish_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'publish_datasets')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_datasets')


def test_list_public(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'list_public')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_archive_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'archive_datasets')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('archive_datasets')


def test_clean(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'round/product/sector/model',
        'clean')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
