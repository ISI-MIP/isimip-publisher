import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import text

from isimip_publisher.utils.database import init_database_session


@pytest.fixture(scope='session')
def setup():
    load_dotenv(Path().cwd() / '.env')


@pytest.fixture
def remote_files():
    base_path = Path(__file__).parent.parent.parent
    nc_path = base_path / 'testing' / 'files'
    remote_path = base_path / 'testing' / os.getenv('REMOTE_DIR')

    shutil.rmtree(remote_path, ignore_errors=True)
    shutil.copytree(nc_path, remote_path)


@pytest.fixture
def remote_links():
    base_path = Path(__file__).parent.parent.parent
    nc_path = base_path / 'testing' / 'files'
    remote_path = base_path / 'testing' / os.getenv('REMOTE_DIR')

    shutil.rmtree(remote_path, ignore_errors=True)
    shutil.copytree(nc_path, remote_path, symlinks=True)


@pytest.fixture
def local_files():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    local_path = base_path / 'testing' / os.getenv('LOCAL_DIR')

    shutil.rmtree(local_path, ignore_errors=True)
    shutil.copytree(files_path, local_path)


@pytest.fixture
def public_files():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    public_path = base_path / 'testing' / os.getenv('PUBLIC_DIR')

    shutil.rmtree(public_path, ignore_errors=True)
    shutil.copytree(files_path, public_path)


@pytest.fixture
def public_links():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    public_path = base_path / 'testing' / os.getenv('PUBLIC_DIR')

    shutil.rmtree(public_path, ignore_errors=True)
    shutil.copytree(files_path, public_path, symlinks=True)


@pytest.fixture
def archive_files():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    archive_path = base_path / 'testing' / os.getenv('ARCHIVE_DIR')

    shutil.rmtree(archive_path, ignore_errors=True)
    shutil.copytree(files_path, archive_path)


@pytest.fixture()
def db():
    session = init_database_session(os.getenv('DATABASE'))
    engine = session.get_bind()

    with engine.connect() as conn:
        conn.execute(text('TRUNCATE resources_datasets CASCADE;'))
        conn.execute(text('TRUNCATE resources CASCADE;'))
        conn.execute(text('TRUNCATE datasets CASCADE;'))
        conn.commit()


@pytest.fixture()
def local_datasets():
    base_path = Path(__file__).parent.parent.parent
    session = init_database_session(os.getenv('DATABASE'))
    engine = session.get_bind()

    version = datetime.now().date().strftime('%Y%m%d')

    with engine.connect() as conn:
        for file_name in ['datasets.sql', 'files.sql']:
            with open(base_path / 'testing' / 'sql' / file_name) as fp:
                conn.execute(text(fp.read()))
        conn.commit()

    session.commit()

    with engine.connect() as conn:
        conn.execute(text('UPDATE public.datasets SET public = false;'), {'version': version})
        conn.execute(text('UPDATE public.datasets SET version = :version;'), {'version': version})
        conn.commit()

    session.commit()


@pytest.fixture()
def public_datasets():
    base_path = Path(__file__).parent.parent.parent
    session = init_database_session(os.getenv('DATABASE'))
    engine = session.get_bind()

    with engine.connect() as conn:
        for file_name in ['datasets.sql', 'files.sql']:
            with open(base_path / 'testing' / 'sql' / file_name) as fp:
                conn.execute(text(fp.read()))
        conn.commit()


@pytest.fixture()
def resources():
    base_path = Path(__file__).parent.parent.parent
    session = init_database_session(os.getenv('DATABASE'))
    engine = session.get_bind()

    with engine.connect() as conn:
        for file_name in ['resources.sql', 'resources_datasets.sql']:
            with open(base_path / 'testing' / 'sql' / file_name) as fp:
                conn.execute(text(fp.read()))
        conn.commit()


def test_empty(setup, script_runner):
    response = script_runner.run(['isimip-publisher'])
    assert not response.stderr
    assert response.returncode == 0


def test_help(setup, script_runner):
    response = script_runner.run(['isimip-publisher', '--help'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr


def test_list_remote(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_list_remote2(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_remote', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 0


def test_list_remote_links(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_remote_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_list_local(setup, local_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_local', 'round/product/sector'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_list_public(setup, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'list_public', 'round/product/sector'])
    assert response.success, response.stderr
    assert response.stdout
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_remote(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_remote', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_remote_links(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_remote_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_local(setup, local_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_local', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_public(setup, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_public', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_match_public_links(setup, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'match_public_links', 'round/product/sector2'])
    assert response.success, response.stderr
    assert not response.stderr
    assert len(response.stdout.splitlines()) == 6


def test_fetch_files(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'fetch_files', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('fetch_files')


def test_write_local_jsons(setup, local_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'write_local_jsons', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_local_jsons')


def test_write_public_jsons(setup, public_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'write_public_jsons', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_public_jsons')


def test_write_link_jsons(setup, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'write_link_jsons', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('write_link_jsons')


def test_insert_datasets(setup, local_files, db, script_runner):
    response = script_runner.run(['isimip-publisher', 'insert_datasets', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('insert_datasets')


def test_link_links(setup, remote_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'link_links',
                                  'round/product/sector/model', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('link_links')


def test_link_files(setup, remote_files, script_runner):
    response = script_runner.run(['isimip-publisher', 'link_files',
                                  'round/product/sector/model', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('link_files')


def test_link_datasets(setup, public_links, script_runner):
    response = script_runner.run(['isimip-publisher', 'link_datasets',
                                  'round/product/sector/model', 'round/product/sector2/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('link_datasets')


def test_publish_datasets(setup, local_files, db, local_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'publish_datasets', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('publish_datasets')


def test_update_datasets(setup, public_files, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_datasets', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert response.stderr.strip().startswith('update_datasets')


def test_archive_datasets_yes(setup, db, mocker, public_datasets, script_runner):
    mocker.patch('builtins.input', return_value='yes')

    response = script_runner.run('isimip-publisher', 'archive_datasets', 'round/product/sector/model')
    assert response.success, response.stderr
    assert response.stdout.strip().startswith('Archiving')
    assert response.stderr.strip().startswith('archive_datasets')


def test_archive_datasets_no(setup, db, mocker, public_datasets, script_runner):
    mocker.patch('builtins.input', return_value='no')

    response = script_runner.run(['isimip-publisher', 'archive_datasets', 'round/product/sector/model'])
    assert response.success
    assert response.stdout.strip().startswith('Archiving')
    assert not response.stderr


def test_check(setup, public_files, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'check', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_tree(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_tree', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_search(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_search', 'round/product/sector'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_views(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_views'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_clean(setup, script_runner):
    response = script_runner.run(['isimip-publisher', 'clean', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_insert_doi(setup, db, public_datasets, script_runner):
    response = script_runner.run(['isimip-publisher', 'insert_doi',
                                  'testing/resources/test.json', 'round/product/sector/model'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr


def test_update_doi(setup, db, public_datasets, resources, script_runner):
    response = script_runner.run(['isimip-publisher', 'update_doi', 'testing/resources/test1.json'])
    assert response.success, response.stderr
    assert not response.stdout
    assert not response.stderr
