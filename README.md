ISIMIP publisher
================

A command line tool to publish climate impact data from the ISIMIP project.

**This is still work in progress.**

Setup
-----

Install using pip (preferably in a virtual environment):

```bash
pip install git+https://ISIMIP/isimip-publisher
```

Clone the repository with the config.

```bash
git clone git@github.com:ISIMIP/isimip-publisher-config /path/to/isimip-publisher-config
```

Create a `.env` file with the following (enviroment) variables:

```
LOG_LEVEL=ERROR
LOG_FILE=/path/to/logfile

CONFIG_DIR=/path/to/isimip-publisher-config

WORK_DIR=/path/to/work/%(simulation_round)s/%(sector)s/%(model)s
PUBLIC_DIR=/path/to/public/%(simulation_round)s/%(sector)s/%(model)s

REMOTE_DEST=localhost
REMOTE_DIR=/path/to/remote/%(simulation_round)s/output/%(sector)s/%(model)s

DATABASE=postgresql+psycopg2://USER:PASSWORD@host:port/DBNAME
```

A database user and a database has to be created and the `pg_trgm` extension has to be created:

```pgsql
CREATE USER "USER" WITH PASSWORD 'PASSWORD';
CREATE DATABASE "DBNAME" WITH OWNER "USER";

\c DBNAME
CREATE EXTENSION pg_trgm;
```

Usage
-----

```bash
# list remote files
isimip-publisher <simulation_round> <product> <sector> <model> list_remote

# match remote datasets
isimip-publisher <simulation_round> <product> <sector> <model> match_remote_datasets

# match remote files
isimip-publisher <simulation_round> <product> <sector> <model> match_remote_files

# copy remote files to TMP_DIR
isimip-publisher <simulation_round> <product> <sector> <model> copy_files

# list local files
isimip-publisher <simulation_round> <product> <sector> <model> list_local

# match local datasets
isimip-publisher <simulation_round> <product> <sector> <model> match_local_datasets

# match local files
isimip-publisher <simulation_round> <product> <sector> <model> match_local_files

# update the global attributes accoding to the config
isimip-publisher <simulation_round> <product> <sector> <model> update_files

# create a JSON file with metadata
isimip-publisher <simulation_round> <product> <sector> <model> create_jsons

# create a checksum file with the sha256 checksum of the file
isimip-publisher <simulation_round> <product> <sector> <model> create_checksums

# finds datasets and ingest their metadata into the database
isimip-publisher <simulation_round> <product> <sector> <model> ingest_datasets

# ingest the metadata from the files into the database
isimip-publisher <simulation_round> <product> <sector> <model> ingest_files

# copy files from WORK_DIR to PUPLIC_DIR
isimip-publisher <simulation_round> <product> <sector> <model> publish_files

# cleanup the WORK_DIR
isimip-publisher <simulation_round> <product> <sector> <model> clean
```

For all commands but `list_remote` and `list_local` a list of files *relative* to `REMOTE_DIR` or `WORK_DIR` (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher <simulation_round> <sector> <model> copy_files -f /path/to/files.txt
```

Test
----

Install test dependencies

```
pip install -r requirements/dev.txt
```

Copy `.env.pytest` to `.env`. This sets the environment variables to the directories in `testing`.

Run:

```
pytest
```

Run a specific test, e.g.:

```
pytest isimip_publisher/tests/test_commands.py::test_empty
```
