import os
import pytest
import shutil


@pytest.fixture(scope='session')
def setup():
    test_dir = os.path.dirname(os.path.abspath(__file__))

    shutil.rmtree(os.path.join(test_dir, 'work'), ignore_errors=True)
    shutil.rmtree(os.path.join(test_dir, 'public'), ignore_errors=True)


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
        'testsector',
        'testmodel',
        'list_remote')
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 3


def test_validate_remote(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testsector',
        'testmodel',
        'validate_remote')
    assert response.success, response.stderr
    assert response.stdout.strip() == 'Success!', response.stdout
    assert not response.stderr


def test_copy_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
        'testsector',
        'testmodel',
        'copy_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_files(setup, script_runner):
    response = script_runner.run(
        'isimip-publisher',
        'testround',
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
        'testsector',
        'testmodel',
        'publish_files')
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
