import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

import pytest
from isimip_publisher.utils.database import (Dataset, Resource,
                                             init_database_session)


@pytest.fixture(scope='session')
def setup():
    load_dotenv(Path().cwd() / '.env')

    base_dir = Path(__file__).parent.parent.parent
    test_dir = base_dir / 'testing'

    shutil.rmtree(test_dir / 'work', ignore_errors=True)
    shutil.rmtree(test_dir / 'public', ignore_errors=True)
    shutil.rmtree(test_dir / 'archive', ignore_errors=True)

    session = init_database_session(os.getenv('DATABASE'))
    for resource in session.query(Resource):
        session.delete(resource)
    session.commit()

    for dataset in session.query(Dataset):
        for file in dataset.files:
            session.delete(file)
        session.delete(dataset)
    session.commit()


def test_empty(setup, script_runner):
    response = script_runner.run('isimip-publisher')
    assert not response.stderr
    assert response.returncode == 0


def test_help(setup, script_runner):
    response = script_runner.run('isimip-publisher', '--help')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr


def test_list_remote(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'list_remote', 'round/product/sector/model')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_remote(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'match_remote', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_fetch_files(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'fetch_files', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('fetch_files')


def test_list_local(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'list_local', 'round/product/sector/model')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_local(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'match_local', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_write_jsons(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'write_jsons', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_jsons')


def test_write_checksums(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'write_checksums', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_checksums')


def test_write_thumbnails(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'write_thumbnails', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_thumbnails')


def test_insert_datasets(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'insert_datasets', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('insert_datasets')


def test_publish_datasets(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'publish_datasets', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_datasets')


def test_list_public(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'list_public', 'round/product/sector/model')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_public(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'match_public', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_insert_doi(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'insert_doi', 'testing/resources/ISIMIP.001.json')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_doi(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'update_doi', 'testing/resources/ISIMIP.001.json')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_index(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'update_index', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_check(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'check', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_archive_datasets(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'archive_datasets', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('archive_datasets')


def test_clean(setup, script_runner):
    response = script_runner.run('isimip-publisher', 'clean', 'round/product/sector/model')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
