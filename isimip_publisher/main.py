import argparse

from .commands import (clean, copy_files,
                       ingest_datasets, ingest_files, list_local, list_remote,
                       match_local_datasets, match_local_files,
                       match_remote_datasets, match_remote_files, publish_files,
                       update_files, write_checksums,
                       write_dataset_jsons, write_file_jsons)
from .utils import setup_env, setup_logging


def main():
    setup_env()
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('simulation_round', help='name of the simulation_round')
    parser.add_argument('product', help='type of data product')
    parser.add_argument('sector', help='name of the sector')
    parser.add_argument('model', help='models to process')

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    clean.parser(subparsers)
    copy_files.parser(subparsers)
    ingest_datasets.parser(subparsers)
    ingest_files.parser(subparsers)
    list_local.parser(subparsers)
    list_remote.parser(subparsers)
    match_local_datasets.parser(subparsers)
    match_local_files.parser(subparsers)
    match_remote_datasets.parser(subparsers)
    match_remote_files.parser(subparsers)
    publish_files.parser(subparsers)
    update_files.parser(subparsers)
    write_checksums.parser(subparsers)
    write_dataset_jsons.parser(subparsers)
    write_file_jsons.parser(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # here we call clean.main, fetch.main, etc
        args.func(args)
    else:
        parser.print_help()
