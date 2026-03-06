ISIMIP publisher
================

[![Latest release](https://shields.io/github/v/release/ISI-MIP/isimip-publisher)](https://github.com/ISI-MIP/isimip-publisher/releases)
[![Python Version](https://img.shields.io/badge/python-3.13-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/ISI-MIP/django-datacite/blob/master/LICENSE)
[![pytest Workflow Status](https://github.com/ISI-MIP/isimip-publisher/actions/workflows/pytest.yml/badge.svg)](https://github.com/ISI-MIP/isimip-publisher/actions/workflows/pytest.yml)
[![Coverage Status](https://coveralls.io/repos/github/ISI-MIP/isimip-publisher/badge.svg?branch=master)](https://coveralls.io/github/ISI-MIP/isimip-publisher?branch=master)

A command line tool to publish climate impact data from the ISIMIP project. This tool is used for the [ISIMIP repository](https://data.isimip.org).

Setup
-----

First create a virtual environment in the directory `env` using:

```
python3 -m venv env
```

Next, install `isimip-publisher` directly from GitHub using

```
pip install git+https://github.com/ISI-MIP/isimip-publisher
```

If you want to make changes to the source code, clone the repository and use `pip install -e` instead:

```
git clone git@github.com:ISI-MIP/isimip-publisher
pip install -e isimip-publisher
```

PostgreSQL has to be available and a database user and a database has to be created, and the `pg_trgm` extension needs to be activated:

```pgsql
CREATE USER "isimip_metadata" WITH PASSWORD 'supersecretpassword';
CREATE DATABASE "isimip_metadata" WITH OWNER "isimip_metadata";
\c isimip_metadata
CREATE EXTENSION pg_trgm;
```

Usage
-----

The publisher has several options which can be inspected using the help option `-h, --help`:

```
usage: isimip-publisher [-h] [-i INCLUDE] [-e EXCLUDE] [-v VERSION] [--remote-dest REMOTE_DEST]
                        [--remote-dir REMOTE_DIR] [--local-dir LOCAL_DIR] [--public-dir PUBLIC_DIR]
                        [--restricted-dir RESTRICTED_DIR] [--archive-dir ARCHIVE_DIR]
                        [--database DATABASE] [--mock] [--restricted]
                        [--protocol-location PROTOCOL_LOCATIONS]
                        [--datacite-username DATACITE_USERNAME]
                        [--datacite-password DATACITE_PASSWORD] [--datacite-prefix DATACITE_PREFIX]
                        [--datacite-test-mode] [--data-url DATA_URL]
                        [--rights {None,CC0,BY,BY-SA,BY-NC,BY-NC-SA}] [--archived]
                        [--skip-registration] [--skip-checksum] [--resolve-links]
                        [--log-level LOG_LEVEL] [--log-file LOG_FILE] [-V]
                        {list_remote,list_remote_links,list_local,list_public,list_public_links,match_remote,match_remote_links,match_local,match_public,match_public_links,count_remote,count_remote_links,count_local,count_public,count_public_links,fetch_files,write_local_jsons,write_public_jsons,insert_datasets,update_datasets,publish_datasets,archive_datasets,diff_remote,diff_remote_links,check,clean,update_search,update_tree,run,insert_doi,update_doi,register_doi,check_doi,link_links,link_files,link_datasets,link,write_link_jsons,init,update_views} ...

options:
  -h, --help            show this help message and exit
  -i, --include INCLUDE
                        Path to a file containing a list of files to include
  -e, --exclude EXCLUDE
                        Path to a file containing a list of files to exclude
  -v, --version VERSION
                        Version date override [default: today]
  --remote-dest REMOTE_DEST
                        Remote destination to fetch files from, e.g. user@example.com
  --remote-dir REMOTE_DIR
                        Remote directory to fetch files from
  --local-dir LOCAL_DIR
                        Local work directory
  --public-dir PUBLIC_DIR
                        Public directory
  --restricted-dir RESTRICTED_DIR
                        Restricted directory
  --archive-dir ARCHIVE_DIR
                        Archive directory
  --database DATABASE   Database connection string, e.g.
                        postgresql+psycopg2://username:password@host:port/dbname
  --mock                If set to True, no files are actually copied. Empty mock files are used
                        instead
  --restricted          If set to True, the files are flagged as restricted in the database.
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol
  --datacite-username DATACITE_USERNAME
                        Username for DataCite
  --datacite-password DATACITE_PASSWORD
                        Password for DataCite
  --datacite-prefix DATACITE_PREFIX
                        Prefix for DataCite
  --datacite-test-mode  If set to True, the test version of DataCite is used
  --data-url DATA_URL   URL of the ISIMIP repository [default: https://data.isimip.org/]
  --rights {None,CC0,BY,BY-SA,BY-NC,BY-NC-SA}
                        Rights/license for the files [default: None]
  --archived            Check also archived files
  --skip-registration   Skip the registration of the DOI when inserting/updating a resource
  --skip-checksum       Skip the computation of the checksum when checking
  --resolve-links       Resolve remote links as if they were files
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file
  -V                    show program's version number and exit

subcommands:
  valid subcommands

  {list_remote,list_remote_links,list_local,list_public,list_public_links,match_remote,match_remote_links,match_local,match_public,match_public_links,count_remote,count_remote_links,count_local,count_public,count_public_links,fetch_files,write_local_jsons,write_public_jsons,insert_datasets,update_datasets,publish_datasets,archive_datasets,diff_remote,diff_remote_links,check,clean,update_search,update_tree,run,insert_doi,update_doi,register_doi,check_doi,link_links,link_files,link_datasets,link,write_link_jsons,init,update_views}
```

The different steps of the publication process are covered by subcommands, which can be invoked separately.

<p align="center">
  <img width="600" src="overview.svg">
</p>

```bash
# list remote files
isimip-publisher list_remote <path>

# match remote datasets
isimip-publisher match_remote <path>

# copy remote files to LOCAL_DIR
isimip-publisher fetch_files <path>

# create a JSON file with metadata for each dataset and file
isimip-publisher write_local_jsons <path>

# finds dataset and file and ingest their metadata into the database
isimip-publisher ingest_datasets <path>

# copy files from LOCAL_DIR to PUBLIC_DIR
isimip-publisher publish_datasets <path>

# copy files from PUBLIC_DIR to ARCHIVE_DIR
isimip-publisher archive_datasets <path>

# insert a new doi resource
isimip-publisher ingest_doi <resource-path>

# register a DOI resource with datacite
isimip-publisher register_doi <DOI>
```

`<path>` starts from `REMOTE_DIR`, `LOCAL_DIR`, etc., and *must* start with `<simulation_round>/<product>/<sector>`. After that more levels can follow to restrict the files to be processed further.

`<resource-path>` is the path to a JSON file containing metadata on the local disk.

`match_remote`, `fetch_files`, `write_jsons`, `ingest_datasets`, and `publish_datasets` can be combined using `run`:

```bash
isimip-publisher run <path>
```

For all commands a list of files with absolute paths (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher -e exclude.txt -i include.txt run <path>
```

Default values for the optional arguments are set in the code, but can also be provided via:

* a config file given by `--config-file`, or located at `isimip.toml`, `~/.isimip.toml`, or `/etc/isimip.toml`. The config file needs to have a section `isimip-publisher` and uses lower case variables and underscores, e.g.:
    ```
    [isimip-publisher]
    log_level = ERROR
    mock = false

    remote_dest = localhost
    remote_dir = /path/to/remote/
    local_dir = /path/to/local/
    public_dir = /path/to/public/
    archive_dir = /path/to/public/
    database = postgresql+psycopg2://USER:PASSWORD@host:port/DBNAME

    protocol_locations = '/path/to/isimip-protocol-3/output/ /path/to/isimip-protocol-3/output/'
    ```

* environment variables (in caps and with underscores, e.g. `MOCK`).


Scripts/Notebooks
-----------------

The different functions of the tool can also be used in Python scripts or Jupyter Notebooks. Before any functions are called,
the global settings object needs to be initialized, e.g.:

```python
from pathlib import Path

from isimip_publisher.config import settings
from isimip_publisher.utils import database

settings_path = Path('isimip.toml').expanduser()
settings.from_toml(settings_path, section='isimip-publisher')

session = database.init_database_session(settings.DATABASE)

datasets = retrieve_datasets(session, path)

...
```

Test
----

Install test dependencies:

```
pip install -e .[pytest]
```

Copy `.env.pytest` to `.env`. This sets the environment variables to the directories in `testing`.

Run `psql < testing/sql/setup.sql` to setup the test database.

Run:

```bash
pytest
```

Run a specific test, e.g.:

```bash
pytest isimip_publisher/tests/test_commands.py::test_empty
```

Run tests with `coverage`:

```bash
pytest --cov=isimip_publisher
```
