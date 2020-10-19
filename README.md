ISIMIP publisher
================

[![Python Version](https://img.shields.io/badge/python-3.7|3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/ISI-MIP/isimip-publisher/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/ISI-MIP/isimip-publisher.svg?branch=master)](https://travis-ci.org/ISI-MIP/isimip-publisher)
[![Coverage Status](https://coveralls.io/repos/github/ISI-MIP/isimip-publisher/badge.svg?branch=master)](https://coveralls.io/github/ISI-MIP/isimip-publisher?branch=master)
[![pyup Status](https://pyup.io/repos/github/ISI-MIP/isimip-publisher/shield.svg)](https://pyup.io/repos/github/ISI-MIP/isimip-publisher/)

A command line tool to publish climate impact data from the ISIMIP project.

**This is still work in progress.**

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

The application can then be used:

```
usage: isimip-publisher [-h] [--config-file CONFIG_FILE] [-i INCLUDE_FILE] [-e EXCLUDE_FILE] [-d DATACITE_FILE] [-v VERSION]
                        [--remote-dest REMOTE_DEST] [--remote-dir REMOTE_DIR] [--local-dir LOCAL_DIR] [--public-dir PUBLIC_DIR]
                        [--archive-dir ARCHIVE_DIR] [--database DATABASE] [--mock MOCK] [--protocol-location PROTOCOL_LOCATIONS]
                        [--isimip-data-url ISIMIP_DATA_URL] [--log-level LOG_LEVEL] [--log-file LOG_FILE]
                        path
                        {list_remote,list_local,list_public,match_remote,match_local,match_public,fetch_files,write_jsons,write_thumbnails,ingest_datasets,publish_datasets,archive_datasets,register_doi,update_doi,check,clean,update_index,run}
                        ...

positional arguments:
  path                  path of the files to publish

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        File path of the config file
  -i INCLUDE_FILE, --include INCLUDE_FILE
                        Path to a file containing a list of files to include
  -e EXCLUDE_FILE, --exclude EXCLUDE_FILE
                        Path to a file containing a list of files to exclude
  -d DATACITE_FILE, --datacite-file DATACITE_FILE
                        Path to a file containing DateCite metadata (only for register_doi, update_doi)
  -v VERSION, --version VERSION
                        version date override [default: today]
  --remote-dest REMOTE_DEST
                        Remote destination to fetch files from, e.g. user@example.com
  --remote-dir REMOTE_DIR
                        Remote directory to fetch files from
  --local-dir LOCAL_DIR
                        Local work directory
  --public-dir PUBLIC_DIR
                        Public directory
  --archive-dir ARCHIVE_DIR
                        Archive directory
  --database DATABASE   Database connection string, e.g. postgresql+psycopg2://username:password@host:port/dbname
  --mock MOCK           If set to True no files are actually copied. Empty mock files are used instead
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol
  --isimip-data-url ISIMIP_DATA_URL
                        URL of the ISIMIP repository [default: https://data.isimip.org/]
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file

subcommands:
  valid subcommands

  {list_remote,list_local,list_public,match_remote,match_local,match_public,fetch_files,write_jsons,write_thumbnails,ingest_datasets,publish_datasets,archive_datasets,register_doi,update_doi,check,clean,update_index,run}
```

The different steps of the publication process are covered by subcommands, which can be invoked separately.

<p align="center">
  <img width="600" src="overview.svg">
</p>

```bash
# list remote files
isimip-publisher <path> list_remote

# match remote datasets
isimip-publisher <path> match_remote

# copy remote files to LOCAL_DIR
isimip-publisher <path> fetch_files

# create a JSON file with metadata for each dataset and file
isimip-publisher <path> write_jsons

# create a thumbnail file for each dataset and file
isimip-publisher <path> write_thumbnails

# finds dataset and file and ingest their metadata into the database
isimip-publisher <path> ingest_datasets

# copy files from LOCAL_DIR to PUPLIC_DIR
isimip-publisher <path> publish_datasets

# copy files from PUBLIC_DIR to ARCHIVE_DIR
isimip-publisher <path> archive_datasets

# register a new doi
isimip-publisher -d <doi-template> <path> register_doi

# update an existing doi
isimip-publisher -d <doi-template> <path> update_doi
```

`<path>` starts from `REMOTE_DIR`, `LOCAL_DIR`, etc., and *must* start with `<simulation_round>/<product>/<sector>`. After that more levels can follow to restrict the files to be processed further.

`match_remote`, `fetch_files`, `write_jsons`, `write_thumbnails`, `ingest_datasets`, and `publish_datasets` can be combined using `run`:

```bash
isimip-publisher <path> run
```

For all commands a list of files with absolute pathes (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher -f /path/to/files.txt <path> run
```

Default values for the optional arguments are set in the code, but can also be provided via:

* a config file given by `--config-file`, or located at `isimip-qc.conf`, `~/.isimip-qc.conf`, or `/etc/isimip-qc.conf`. The config file needs to have a section `isimip-publisher` and uses lower case variables and underscores, e.g.:
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


Test
----

Install test dependencies

```
pip install -r requirements/dev.txt
```

Copy `.env.pytest` to `.env`. This sets the environment variables to the directories in `testing`.

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
