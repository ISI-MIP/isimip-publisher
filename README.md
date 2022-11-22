ISIMIP publisher
================

[![Python Version](https://img.shields.io/badge/python-3.6-3.7-3.8-3.9-3.10-blue)](https://www.python.org/)
[![pytest Workflow Status](https://github.com/ISI-MIP/isimip-publisher/actions/workflows/pytest.yml/badge.svg)](https://github.com/ISI-MIP/isimip-publisher/actions/workflows/pytest.yml)
[![License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat)](https://github.com/ISI-MIP/isimip-publisher/blob/master/LICENSE)

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
usage: isimip-publisher [-h] [--config-file CONFIG_FILE] [-i INCLUDE_FILE]
                        [-e EXCLUDE_FILE] [-v VERSION]
                        [--remote-dest REMOTE_DEST] [--remote-dir REMOTE_DIR]
                        [--local-dir LOCAL_DIR] [--public-dir PUBLIC_DIR]
                        [--archive-dir ARCHIVE_DIR]
                        [--resource-dir RESOURCE_DIR] [--database DATABASE]
                        [--mock MOCK] [--protocol-location PROTOCOL_LOCATIONS]
                        [--datacite-metadata-url DATACITE_METADATA_URL]
                        [--datacite-doi-url DATACITE_DOI_URL]
                        [--datacite-username DATACITE_USERNAME]
                        [--datacite-password DATACITE_PASSWORD]
                        [--isimip-data-url ISIMIP_DATA_URL]
                        [--rights {None,CC0,BY,BY-SA,BY-NC,BY-NC-SA}]
                        [--log-level LOG_LEVEL] [--log-file LOG_FILE]
                        {list_remote,list_local,list_public,match_remote,match_local,match_public,fetch_files,write_jsons,update_jsons,insert_datasets,update_datasets,publish_datasets,archive_datasets,check,clean,update_index,run,insert_doi,update_doi,register_doi,init}
                        ...

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        File path of the config file
  -i INCLUDE_FILE, --include INCLUDE_FILE
                        Path to a file containing a list of files to include
  -e EXCLUDE_FILE, --exclude EXCLUDE_FILE
                        Path to a file containing a list of files to exclude
  -v VERSION, --version VERSION
                        version date override [default: today]
  --remote-dest REMOTE_DEST
                        Remote destination to fetch files from, e.g.
                        user@example.com
  --remote-dir REMOTE_DIR
                        Remote directory to fetch files from
  --local-dir LOCAL_DIR
                        Local work directory
  --public-dir PUBLIC_DIR
                        Public directory
  --archive-dir ARCHIVE_DIR
                        Archive directory
  --resource-dir RESOURCE_DIR
                        Resource metadata directory
  --database DATABASE   Database connection string, e.g. postgresql+psycopg2:/
                        /username:password@host:port/dbname
  --mock MOCK           If set to True no files are actually copied. Empty
                        mock files are used instead
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol
  --datacite-metadata-url DATACITE_METADATA_URL
                        Metadata endpoint for the DataCite MDS API, default:
                        https://mds.datacite.org/metadata
  --datacite-doi-url DATACITE_DOI_URL
                        DOI endpoint for the DataCite MDS API, default:
                        https://mds.datacite.org/doi
  --datacite-username DATACITE_USERNAME
                        Username the DataCite MDS API
  --datacite-password DATACITE_PASSWORD
                        Password the DataCite MDS API
  --isimip-data-url ISIMIP_DATA_URL
                        URL of the ISIMIP repository [default:
                        https://data.isimip.org/]
  --rights {None,CC0,BY,BY-SA,BY-NC,BY-NC-SA}
                        Rights/license for the files [default: None]
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file

subcommands:
  valid subcommands

  {list_remote,list_local,list_public,match_remote,match_local,match_public,fetch_files,write_jsons,update_jsons,insert_datasets,update_datasets,publish_datasets,archive_datasets,check,clean,update_index,run,insert_doi,update_doi,register_doi,init}

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
isimip-publisher write_jsons <path>

# finds dataset and file and ingest their metadata into the database
isimip-publisher ingest_datasets <path>

# copy files from LOCAL_DIR to PUPLIC_DIR
isimip-publisher publish_datasets <path>

# copy files from PUBLIC_DIR to ARCHIVE_DIR
isimip-publisher archive_datasets <path>

# insert a new doi resource
isimip-publisher ingest_doi <resource-path>

# register a DOI resource with datacite
isimip-publisher ingest_doi <DOI>
```

`<path>` starts from `REMOTE_DIR`, `LOCAL_DIR`, etc., and *must* start with `<simulation_round>/<product>/<sector>`. After that more levels can follow to restrict the files to be processed further.

`<resource-path>` is the path to a JSON file containing metadata on the local disk.

`match_remote`, `fetch_files`, `write_jsons`, `ingest_datasets`, and `publish_datasets` can be combined using `run`:

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

Install test dependencies:

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
