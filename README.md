ISIMIP publisher
================

[![Latest release](https://shields.io/github/v/release/ISI-MIP/isimip-publisher)](https://github.com/ISI-MIP/isimip-publisher/releases)
[![Python Version: 3.6|3.7|3.8|3.9|3.10](https://img.shields.io/badge/python-3.6|3.7|3.8|3.9|3.10-blue)](https://www.python.org/)
[![License: MIT](http://img.shields.io/badge/license-MIT-yellow.svg)](https://github.com/ISI-MIP/isimip-publisher/blob/master/LICENSE)
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
usage: isimip-publisher [-h] [--config-file CONFIG_FILE] [-i INCLUDE_FILE] [-e EXCLUDE_FILE]
                        [-v VERSION] [--remote-dest REMOTE_DEST] [--remote-dir REMOTE_DIR]
                        [--local-dir LOCAL_DIR] [--public-dir PUBLIC_DIR]
                        [--archive-dir ARCHIVE_DIR] [--database DATABASE] [--mock MOCK]
                        [--protocol-location PROTOCOL_LOCATIONS]
                        [--datacite-username DATACITE_USERNAME]
                        [--datacite-password DATACITE_PASSWORD]
                        [--datacite-prefix DATACITE_PREFIX]
                        [--datacite-test-mode DATACITE_TEST_MODE]
                        [--isimip-data-url ISIMIP_DATA_URL]
                        [--rights {None,CC0,BY,BY-SA,BY-NC,BY-NC-SA}] [--log-level LOG_LEVEL]
                        [--log-file LOG_FILE]
                        {list_remote,list_remote_links,list_local,list_public,list_public_links,match_remote,match_remote_links,match_local,match_public,match_public_links,fetch_files,write_local_jsons,write_public_jsons,write_link_jsons,insert_datasets,update_datasets,publish_datasets,archive_datasets,check,clean,update_index,run,insert_doi,update_doi,register_doi,link_files,link_datasets,link,init}
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
                        Version date override [default: today]
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
  --database DATABASE   Database connection string, e.g.
                        postgresql+psycopg2://username:password@host:port/dbname
  --mock MOCK           If set to True, no files are actually copied. Empty mock files are used
                        instead
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol
  --datacite-username DATACITE_USERNAME
                        Username for DataCite
  --datacite-password DATACITE_PASSWORD
                        Password for DataCite
  --datacite-prefix DATACITE_PREFIX
                        Prefix for DataCite
  --datacite-test-mode DATACITE_TEST_MODE
                        If set to True, the test version of DataCite is used
  --isimip-data-url ISIMIP_DATA_URL
                        URL of the ISIMIP repository [default: https://data.isimip.org/]
  --rights {None,CC0,BY,BY-SA,BY-NC,BY-NC-SA}
                        Rights/license for the files [default: None]
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-file LOG_FILE   Path to the log file

subcommands:
  valid subcommands

  {list_remote,list_remote_links,list_local,list_public,list_public_links,match_remote,match_remote_links,match_local,match_public,match_public_links,fetch_files,write_local_jsons,write_public_jsons,write_link_jsons,insert_datasets,update_datasets,publish_datasets,archive_datasets,check,clean,update_index,run,insert_doi,update_doi,register_doi,link_files,link_datasets,link,init}
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

# copy files from LOCAL_DIR to PUPLIC_DIR
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

For all commands a list of files with absolute pathes (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher -e exclude.txt -i include.txt run <path> 
```

Default values for the optional arguments are set in the code, but can also be provided via:

* a config file given by `--config-file`, or located at `isimip.conf`, `~/.isimip.conf`, or `/etc/isimip.conf`. The config file needs to have a section `isimip-publisher` and uses lower case variables and underscores, e.g.:
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
pip install -r requirements/pytest.txt
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


Database schema
---------------

The database schema is automatically created when `insert_datasets` or `init` is used the first time. The tool creates 3 main tables, one for the `datasets`, one for the `files` (in each dataset), and one for the `resources`, for which DOI are created.:

```
                          Table "public.datasets"
   Column    |            Type             | Collation | Nullable | Default 
-------------+-----------------------------+-----------+----------+---------
 id          | uuid                        |           | not null | 
 target_id   | uuid                        |           |          | 
 name        | text                        |           | not null | 
 path        | text                        |           | not null | 
 version     | character varying(8)        |           | not null | 
 size        | bigint                      |           | not null | 
 specifiers  | jsonb                       |           | not null | 
 identifiers | text[]                      |           | not null | 
 public      | boolean                     |           | not null | 
 tree_path   | text                        |           |          | 
 rights      | text                        |           |          | 
 created     | timestamp without time zone |           |          | 
 updated     | timestamp without time zone |           |          | 
 published   | timestamp without time zone |           |          | 
 archived    | timestamp without time zone |           |          |
```

```
                             Table "public.files"
    Column     |            Type             | Collation | Nullable | Default 
---------------+-----------------------------+-----------+----------+---------
 id            | uuid                        |           | not null | 
 dataset_id    | uuid                        |           |          | 
 target_id     | uuid                        |           |          | 
 name          | text                        |           | not null | 
 path          | text                        |           | not null | 
 version       | character varying(8)        |           | not null | 
 size          | bigint                      |           | not null | 
 checksum      | text                        |           | not null | 
 checksum_type | text                        |           | not null | 
 netcdf_header | jsonb                       |           |          | 
 specifiers    | jsonb                       |           | not null | 
 identifiers   | text[]                      |           | not null | 
 created       | timestamp without time zone |           |          | 
 updated       | timestamp without time zone |           |          | 
```

```
                        Table "public.resources"
  Column  |            Type             | Collation | Nullable | Default 
----------+-----------------------------+-----------+----------+---------
 id       | uuid                        |           | not null | 
 doi      | text                        |           | not null | 
 title    | text                        |           | not null | 
 version  | text                        |           |          | 
 paths    | text[]                      |           | not null | 
 datacite | jsonb                       |           | not null | 
 created  | timestamp without time zone |           |          | 
 updated  | timestamp without time zone |           |          | 
```

The many-to-many relation between `datasets` and `resources` is implemented using a seperate table:

```
          Table "public.resources_datasets"
   Column    | Type | Collation | Nullable | Default 
-------------+------+-----------+----------+---------
 resource_id | uuid |           |          | 
 dataset_id  | uuid |           |          | 
```

Additional tables are created for the search and tree functionality of the repository.

```
                           Table "public.search"
   Column   |            Type             | Collation | Nullable | Default 
------------+-----------------------------+-----------+----------+---------
 dataset_id | uuid                        |           | not null | 
 vector     | tsvector                    |           | not null | 
 created    | timestamp without time zone |           |          | 
 updated    | timestamp without time zone |           |          | 
```

```
                           Table "public.trees"
  Column   |            Type             | Collation | Nullable | Default 
-----------+-----------------------------+-----------+----------+---------
 id        | uuid                        |           | not null | 
 tree_dict | jsonb                       |           | not null | 
 created   | timestamp without time zone |           |          | 
 updated   | timestamp without time zone |           |          |
```

Two materialized views are used to allow a fast lookup to all `identifiers` (with the list of corresponding specifiers), as well as all `words` (the list of tokens for the search):

```
       Materialized view "public.identifiers"
   Column   | Type | Collation | Nullable | Default 
------------+------+-----------+----------+---------
 identifier | text |           |          | 
 specifiers | json |           |          | 
```

```
        Materialized view "public.words"
 Column | Type | Collation | Nullable | Default 
--------+------+-----------+----------+---------
 word   | text |           |          | 
```
