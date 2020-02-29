ISIMIP publisher
================

[![Python Version](https://img.shields.io/badge/python-3.6|3.7|3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/ISI-MIP/isimip-publisher/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/ISI-MIP/isimip-publisher.svg?branch=master)](https://travis-ci.org/ISI-MIP/isimip-publisher)
[![Coverage Status](https://coveralls.io/repos/github/ISI-MIP/isimip-publisher/badge.svg?branch=master)](https://coveralls.io/github/ISI-MIP/isimip-publisher?branch=master)
[![pyup Status](https://pyup.io/repos/github/ISI-MIP/isimip-publisher/shield.svg)](https://pyup.io/repos/github/ISI-MIP/isimip-publisher/)

A command line tool to publish climate impact data from the ISIMIP project.

**This is still work in progress.**

Setup
-----

For a `conda` setup, an environment and install `cartopy`:

```bash
conda create isimip
conda install cartopy
```

For a regular setup install some prerequisites using the systems package manager:

```bash
# Debian/Ubuntu
apt install

# CentOS
yum install

# openSUSE
zypper install libproj-devel geos-devel
```

Install, using pip:

```bash
pip install git+https://github.com/ISI-MIP/isimip-publisher
```

Create a `.env` file with the following (enviroment) variables:

```
LOG_LEVEL=ERROR
LOG_FILE=/path/to/logfile

CONFIG_DIR=.

REMOTE_DEST=localhost
REMOTE_DIR=/path/to/remote/
LOCAL_DIR=/path/to/local/
PUBLIC_DIR=/path/to/public/
ARCHIVE_DIR=/path/to/public/

PATH_PATTERN=^(?P<simulation_round>\w+)/(?P<product>\w+)/(?P<sector>\w+)/(?P<model>[\w-+]+)/

DATABASE=postgresql+psycopg2://USER:PASSWORD@host:port/DBNAME
```

A database user and a database has to be created:

```pgsql
CREATE USER "isimip_metadata" WITH PASSWORD 'supersecretpassword';
CREATE DATABASE "isimip_metadata" WITH OWNER "isimip_metadata";
\c isimip_metadata
CREATE EXTENSION pg_trgm;
```

Usage
-----

```bash
# list remote files
isimip-publisher <path> list_remote

# match remote datasets
isimip-publisher <path> match_remote

# copy remote files to LOCAL_DIR
isimip-publisher <path> fetch_files

# list local files
isimip-publisher <path> list_local

# match local datasets
isimip-publisher <path> match_local

# update the global attributes accoding to the config
isimip-publisher <path> update_files

# create a checksum file with the sha256 checksum of the file
isimip-publisher <path> write_checksums

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

# cleanup the LOCAL_DIR
isimip-publisher <path> clean
```

`<path>` starts from `REMOTE_DIR`, `LOCAL_DIR`, etc., and *must* start with `<simulation_round>/<product>/<sector>`. After that more levels can follow to restrict the files to be processed further.

`fetch_files`, `update_files`, `write_checksums`, `write_jsons`, `write_thumbnails`, `ingest_datasets`, and `publish_datasets` can be combined using `run`:

```bash
isimip-publisher <path> run
```

For all commands a list of files with absolute pathes (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher  -f /path/to/files.txt <path> run
```

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
