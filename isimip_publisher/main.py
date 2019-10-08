import argparse

from .commands import (chmod_files, ingest_datasets, ingest_files, fetch_files,
                       list_local, list_remote, match_local_datasets, match_local_files,
                       match_remote_datasets, match_remote_files, publish_files,
                       update_files, update_index, write_checksums,
                       write_dataset_jsons, write_file_jsons,
                       run, run_all)
from .utils import setup_env, setup_logging
from .utils.config import parse_config, parse_filelist, parse_version


def main():
    setup_env()
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('simulation_round', help='name of the simulation_round')
    parser.add_argument('product', help='type of data product')
    parser.add_argument('sector', help='name of the sector')
    parser.add_argument('model', help='models to process')
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    # add a subparser for each subcommand
    subparsers.add_parser('chmod_files').set_defaults(func=chmod_files)
    subparsers.add_parser('ingest_datasets').set_defaults(func=ingest_datasets)
    subparsers.add_parser('ingest_files').set_defaults(func=ingest_files)
    subparsers.add_parser('fetch_files').set_defaults(func=fetch_files)
    subparsers.add_parser('list_local').set_defaults(func=list_local)
    subparsers.add_parser('list_remote').set_defaults(func=list_remote)
    subparsers.add_parser('match_local_datasets').set_defaults(func=match_local_datasets)
    subparsers.add_parser('match_local_files').set_defaults(func=match_local_files)
    subparsers.add_parser('match_remote_datasets').set_defaults(func=match_remote_datasets)
    subparsers.add_parser('match_remote_files').set_defaults(func=match_remote_files)
    subparsers.add_parser('publish_files').set_defaults(func=publish_files)
    subparsers.add_parser('update_files').set_defaults(func=update_files)
    subparsers.add_parser('update_index').set_defaults(func=update_index)
    subparsers.add_parser('write_checksums').set_defaults(func=write_checksums)
    subparsers.add_parser('write_dataset_jsons').set_defaults(func=write_dataset_jsons)
    subparsers.add_parser('write_file_jsons').set_defaults(func=write_file_jsons)

    subparsers.add_parser('run').set_defaults(func=run)
    subparsers.add_parser('run_all').set_defaults(func=run_all)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        version = parse_version(args.version)
        config = parse_config(args.simulation_round, args.product, args.sector, args.model, version)
        filelist = parse_filelist(args.filelist_file)

        args.func(version, config, filelist)
    else:
        parser.print_help()
