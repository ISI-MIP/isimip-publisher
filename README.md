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

TMP_DIR=/path/to/tmp/%(simulation_run)s/%(sector)s/%(model)s
PUB_DIR=/path/to/pub/%(simulation_run)s/%(sector)s/%(model)s

REMOTE_DEST=user@example.com
REMOTE_DIR=/path/to/data/%(simulation_run)s/OutputData/%(sector)s/%(model)s
```


Usage
-----

```bash
# list remote files
isimip-publisher <simulation_run> <sector> <model> list_remote

# copy remote files to TMP_DIR
isimip-publisher <simulation_run> <sector> <model> fetch

# list local files
isimip-publisher <simulation_run> <sector> <model> list_local

# validate file pathes
isimip-publisher <simulation_run> <sector> <model> validate_path

# validate files
isimip-publisher <simulation_run> <sector> <model> validate

# update the global attributes accoding to the config
isimip-publisher <simulation_run> <sector> <model> update

# ingest the metadata from the files into the database
isimip-publisher <simulation_run> <sector> <model> ingest

# copy files from TMP_DIR to PUP_DIR
isimip-publisher <simulation_run> <sector> <model> publish

# cleanup the TMP_DIR
isimip-publisher <simulation_run> <sector> <model> clean
```

For all commands but `list_remote` and `list_local` a list of files *relative* to `REMOTE_DIR` or `TMP_DIR` (as line separated txt file) can be provided to restrict the files processed, e.g.:

```bash
isimip-publisher <simulation_run> <sector> <model> fetch -f /path/to/files.txt
```
