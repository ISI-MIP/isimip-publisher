import argparse

from .commands import (archive_datasets, clean, fetch_files, ingest_datasets,
                       list_local, list_public, list_remote, match_local,
                       match_remote, publish_datasets, update_files,
                       write_jsons, write_thumbnails)
from .utils import setup_env, setup_logging
from .utils.config import parse_config, parse_filelist, parse_version


def main():
    setup_env()
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path of the files to publish')
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    # add a subparser for each subcommand
    subparsers.add_parser('clean').set_defaults(func=clean)
    subparsers.add_parser('archive_datasets').set_defaults(func=archive_datasets)
    subparsers.add_parser('ingest_datasets').set_defaults(func=ingest_datasets)
    subparsers.add_parser('fetch_files').set_defaults(func=fetch_files)
    subparsers.add_parser('list_remote').set_defaults(func=list_remote)
    subparsers.add_parser('list_local').set_defaults(func=list_local)
    subparsers.add_parser('list_public').set_defaults(func=list_public)
    subparsers.add_parser('match_local').set_defaults(func=match_local)
    subparsers.add_parser('match_remote').set_defaults(func=match_remote)
    subparsers.add_parser('publish_datasets').set_defaults(func=publish_datasets)
    subparsers.add_parser('update_files').set_defaults(func=update_files)
    subparsers.add_parser('write_jsons').set_defaults(func=write_jsons)
    subparsers.add_parser('write_thumbnails').set_defaults(func=write_thumbnails)

    subparsers.add_parser('run').set_defaults(func=run)
    subparsers.add_parser('run_all').set_defaults(func=run_all)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        version = parse_version(args.version)
        config = parse_config(args.path, version)
        filelist = parse_filelist(args.filelist_file)

        if config is False:
            parser.error('no pattern/schema could be found for path')

        args.func(version, config, filelist)
    else:
        parser.print_help()


def run(version, config, filelist=None):
    clean(version, config, filelist)
    match_remote(version, config, filelist)
    fetch_files(version, config, filelist)
    write_jsons(version, config, filelist)
    write_thumbnails(version, config, filelist)
    ingest_datasets(version, config, filelist)
    publish_datasets(version, config, filelist)


def run_all(version, config, filelist=None):
    clean(version, config, filelist)
    list_remote(version, config, filelist)
    match_remote(version, config, filelist)
    fetch_files(version, config, filelist)
    list_local(version, config, filelist)
    match_local(version, config, filelist)
    write_jsons(version, config, filelist)
    write_thumbnails(version, config, filelist)
    ingest_datasets(version, config, filelist)
    publish_datasets(version, config, filelist)
    archive_datasets(version, config, filelist)
