import os
import pytest
import shutil

from isimip_publisher.utils import setup_env
from isimip_publisher.utils.database import Dataset, File, init_database_session


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
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'list_remote')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 3


def test_match_remote_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'match_remote_files')
    assert response.success, response.stderr
    assert response.stdout.strip() == 'Success!', response.stdout
    assert not response.stderr


def test_match_remote_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'match_remote_datasets')
    assert response.success, response.stderr
    assert response.stdout.strip() == 'Success!', response.stdout
    assert not response.stderr


def test_copy_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'copy_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_list_local(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'list_local')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 3


def test_match_local_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'match_local_files')
    assert response.success, response.stderr
    assert response.stdout.strip() == 'Success!', response.stdout
    assert not response.stderr


def test_match_local_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'match_local_datasets')
    assert response.success, response.stderr
    assert response.stdout.strip() == 'Success!', response.stdout
    assert not response.stderr


def test_update_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'update_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_create_checksums(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'create_checksums')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_create_jsons(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'create_jsons')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_ingest_datasets(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'ingest_datasets')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_ingest_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'ingest_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_publish_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testproduct',
        'testsector',
        'testmodel',
        'publish_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
