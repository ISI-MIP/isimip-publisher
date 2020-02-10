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
LOCAL_DIR=/path/to/work/
PUBLIC_DIR=/path/to/public/

PATH_PATTERN=^(?P<simulation_round>\w+)/(?P<product>\w+)/(?P<sector>\w+)/(?P<model>[\w-+]+)/

DATABASE=postgresql+psycopg2://USER:PASSWORD@host:port/DBNAME
```

A database user and a database has to be created:

```pgsql
CREATE USER "USER" WITH PASSWORD 'PASSWORD';
CREATE DATABASE "DBNAME" WITH OWNER "USER";
```

Usage
-----

```bash
# list remote files
isimip-publisher <simulation_round>/<product>/<sector>/<model> list_remote

# match remote datasets
isimip-publisher <simulation_round>/<product>/<sector>/<model> match_remote_datasets

# match remote files
isimip-publisher <simulation_round>/<product>/<sector>/<model> match_remote_files

# copy remote files to TMP_DIR
isimip-publisher <simulation_round>/<product>/<sector>/<model> fetch_files

# list local files
isimip-publisher <simulation_round>/<product>/<sector>/<model> list_local

# match local datasets
isimip-publisher <simulation_round>/<product>/<sector>/<model> match_local_datasets

# match local files
isimip-publisher <simulation_round>/<product>/<sector>/<model> match_local_files

# update the global attributes accoding to the config
isimip-publisher <simulation_round>/<product>/<sector>/<model> update_files

# create a checksum file with the sha256 checksum of the file
isimip-publisher <simulation_round>/<product>/<sector>/<model> write_checksums

# create a JSON file with metadata for each dataset
isimip-publisher <simulation_round>/<product>/<sector>/<model> write_dataset_jsons

# create a JSON file with metadata for each file
isimip-publisher <simulation_round>/<product>/<sector>/<model> write_file_jsons

# create a thumbnail file for each dataset
isimip-publisher <simulation_round>/<product>/<sector>/<model> write_dataset_thumbnails

# create a thumbnail file for each file
isimip-publisher <simulation_round>/<product>/<sector>/<model> write_file_thumbnails

# finds datasets and ingest their metadata into the database
isimip-publisher <simulation_round>/<product>/<sector>/<model> ingest_datasets

# ingest the metadata from the files into the database
isimip-publisher <simulation_round>/<product>/<sector>/<model> ingest_files

# copy files from WORK_DIR to PUPLIC_DIR
isimip-publisher <simulation_round>/<product>/<sector>/<model> publish_files

# cleanup the WORK_DIR
isimip-publisher <simulation_round>/<product>/<sector>/<model> clean
```

For all commands a list of files *relative* to `REMOTE_DIR` or `WORK_DIR` (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher  -f /path/to/files.txt <simulation_round>/<product>/<sector>/<model> fetch_files
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
