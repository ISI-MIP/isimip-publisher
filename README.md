ISIMIP publisher
================

A command line tool to publish climate impact data from the ISIMIP project.

**This is work in progress.**

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

CONFIG_DIR=/path/to/isimip-publisher-config

TMP_DIR=/path/to/tmp/%(simulation_round)s/%(sector)s/%(model)s
PUB_DIR=/path/to/pub/%(simulation_round)s/%(sector)s/%(model)s

REMOTE_DEST=user@example.com
REMOTE_DIR=/path/to/data/%(simulation_round)s/OutputData/%(sector)s/%(model)s

DATABASE=postgresql+psycopg2://user:password@host:port/dbname
```


Usage
-----

```bash
# list remote files
isimip-publisher <simulation_round> <sector> <model> list --remote

# copy remote files to TMP_DIR
isimip-publisher <simulation_round> <sector> <model> copy

# list local files
isimip-publisher <simulation_round> <sector> <model> list

# validate files
isimip-publisher <simulation_round> <sector> <model> validate

# update the global attributes accoding to the config
isimip-publisher <simulation_round> <sector> <model> update

# create a JSON file with metadata
isimip-publisher <simulation_round> <sector> <model> json

# create a checksum file with the sha256 checksum of the file
isimip-publisher <simulation_round> <sector> <model> checksum

# ingest the metadata from the files into the database
isimip-publisher <simulation_round> <sector> <model> ingest

# copy files from TMP_DIR to PUP_DIR
isimip-publisher <simulation_round> <sector> <model> publish

# cleanup the TMP_DIR
isimip-publisher <simulation_round> <sector> <model> clean
```

For all commands but `list_remote` and `list_local` a list of files *relative* to `REMOTE_DIR` or `TMP_DIR` (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher <simulation_round> <sector> <model> fetch -f /path/to/files.txt
```
