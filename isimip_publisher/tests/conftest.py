import os
import shutil
from datetime import datetime
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import close_all_sessions

from isimip_publisher.utils.database import init_database_session


@pytest.fixture(scope='session')
def setup():
    load_dotenv(Path().cwd() / '.env')


@pytest.fixture()
def db():
    session = init_database_session(os.getenv('ISIMIP_DATABASE'))
    engine = session.get_bind()

    with engine.connect() as conn:
        conn.execute(text('TRUNCATE datasets, datasets_files, files, resources, resources_datasets CASCADE;'))
        conn.commit()

    yield

    # commands which fail leave their session open, which would block the next truncate
    close_all_sessions()


@pytest.fixture
def empty_store():
    from isimip_publisher.config import store

    store.datasets = []
    yield
    store.datasets = []


@pytest.fixture
def empty_local():
    local_path = Path(os.getenv('ISIMIP_LOCAL_DIR'))
    shutil.rmtree(local_path, ignore_errors=True)
    local_path.mkdir(parents=True)


@pytest.fixture
def empty_public():
    public_path = Path(os.getenv('ISIMIP_PUBLIC_DIR'))
    shutil.rmtree(public_path, ignore_errors=True)


@pytest.fixture
def empty_archive():
    archive_path = Path(os.getenv('ISIMIP_ARCHIVE_DIR'))
    shutil.rmtree(archive_path, ignore_errors=True)


@pytest.fixture
def remote_files():
    base_path = Path(__file__).parent.parent.parent
    nc_path = base_path / 'testing' / 'files'
    remote_path = base_path / 'testing' / os.getenv('ISIMIP_REMOTE_DIR')

    shutil.rmtree(remote_path, ignore_errors=True)
    shutil.copytree(nc_path, remote_path)


@pytest.fixture
def remote_links():
    base_path = Path(__file__).parent.parent.parent
    nc_path = base_path / 'testing' / 'files'
    remote_path = base_path / 'testing' / os.getenv('ISIMIP_REMOTE_DIR')

    shutil.rmtree(remote_path, ignore_errors=True)
    shutil.copytree(nc_path, remote_path, symlinks=True)


@pytest.fixture
def local_files():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    local_path = base_path / 'testing' / os.getenv('ISIMIP_LOCAL_DIR')

    shutil.rmtree(local_path, ignore_errors=True)
    shutil.copytree(files_path, local_path)


@pytest.fixture
def public_files():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    public_path = base_path / 'testing' / os.getenv('ISIMIP_PUBLIC_DIR')

    shutil.rmtree(public_path, ignore_errors=True)
    shutil.copytree(files_path, public_path)


@pytest.fixture
def public_links():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    public_path = base_path / 'testing' / os.getenv('ISIMIP_PUBLIC_DIR')

    shutil.rmtree(public_path, ignore_errors=True)
    shutil.copytree(files_path, public_path, symlinks=True)


@pytest.fixture
def archive_files():
    base_path = Path(__file__).parent.parent.parent
    files_path = base_path / 'testing' / 'files'
    archive_path = base_path / 'testing' / os.getenv('ISIMIP_ARCHIVE_DIR')

    shutil.rmtree(archive_path, ignore_errors=True)
    shutil.copytree(files_path, archive_path)


@pytest.fixture()
def local_datasets():
    base_path = Path(__file__).parent.parent.parent
    session = init_database_session(os.getenv('ISIMIP_DATABASE'))
    engine = session.get_bind()

    version = datetime.now().date().strftime('%Y%m%d')

    with engine.connect() as conn:
        for file_name in ['datasets.sql', 'files.sql', 'datasets_files.sql']:
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
    session = init_database_session(os.getenv('ISIMIP_DATABASE'))
    engine = session.get_bind()

    with engine.connect() as conn:
        for file_name in ['datasets.sql', 'files.sql', 'datasets_files.sql']:
            with open(base_path / 'testing' / 'sql' / file_name) as fp:
                conn.execute(text(fp.read()))
        conn.commit()


@pytest.fixture()
def resources():
    base_path = Path(__file__).parent.parent.parent
    session = init_database_session(os.getenv('ISIMIP_DATABASE'))
    engine = session.get_bind()

    with engine.connect() as conn:
        for file_name in ['resources.sql', 'resources_datasets.sql']:
            with open(base_path / 'testing' / 'sql' / file_name) as fp:
                conn.execute(text(fp.read()))
        conn.commit()


@pytest.fixture
def amend_file(tmp_path):
    def write_amend_file(*file_paths):
        amend_path = tmp_path / 'amend.txt'
        amend_path.write_text('\n'.join(file_paths) + '\n')
        return amend_path.as_posix()

    return write_amend_file
