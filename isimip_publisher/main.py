import argparse

from .commands import (archive_datasets, check, clean, fetch_files,
                       ingest_datasets, ingest_resource, list_local,
                       list_public, list_remote, match_local, match_public,
                       match_remote, publish_datasets, write_jsons,
                       write_thumbnails)
from .models import Store
from .utils import setup_env, setup_logging


def main():
    setup_env()
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path of the files to publish')
    parser.add_argument('-i', dest='include_file', default=None,
                        help='path to a file containing a list of files to include')
    parser.add_argument('-e', dest='exclude_file', default=None,
                        help='path to a file containing a list of files to exclude')
    parser.add_argument('-d', dest='datacite_file', default=None,
                        help='path to a file containing DateCite metadata (only for ingest_resource)')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    # add a subparser for each subcommand
    subparsers.add_parser('archive_datasets').set_defaults(func=archive_datasets)
    subparsers.add_parser('check').set_defaults(func=check)
    subparsers.add_parser('clean').set_defaults(func=clean)
    subparsers.add_parser('fetch_files').set_defaults(func=fetch_files)
    subparsers.add_parser('ingest_datasets').set_defaults(func=ingest_datasets)
    subparsers.add_parser('ingest_resource').set_defaults(func=ingest_resource)
    subparsers.add_parser('list_remote').set_defaults(func=list_remote)
    subparsers.add_parser('list_local').set_defaults(func=list_local)
    subparsers.add_parser('list_public').set_defaults(func=list_public)
    subparsers.add_parser('match_local').set_defaults(func=match_local)
    subparsers.add_parser('match_remote').set_defaults(func=match_remote)
    subparsers.add_parser('match_public').set_defaults(func=match_public)
    subparsers.add_parser('publish_datasets').set_defaults(func=publish_datasets)
    subparsers.add_parser('write_jsons').set_defaults(func=write_jsons)
    subparsers.add_parser('write_thumbnails').set_defaults(func=write_thumbnails)

    subparsers.add_parser('run').set_defaults(func=run)
    subparsers.add_parser('run_all').set_defaults(func=run_all)

    args = parser.parse_args()

    if args.include_file and args.exclude_file:
        parser.error('include_file and exclude_file are mutually exclusive')

    if hasattr(args, 'func'):
        store = Store(args)
        if store.pattern is None:
            parser.error('no pattern could be found for path')
        elif store.schema is None:
            parser.error('no schema could be found for path')
        elif (args.func == ingest_resource):
            if store.datacite is None:
                parser.error('no DateCite metadata file was provided')

        args.func(store)
    else:
        parser.print_help()


def run(store=None):
    match_remote(store)
    fetch_files(store)
    match_local(store)
    write_jsons(store)
    write_thumbnails(store)
    ingest_datasets(store)
    publish_datasets(store)


def run_all(store=None):
    clean(store)
    list_remote(store)
    match_remote(store)
    fetch_files(store)
    list_local(store)
    match_local(store)
    write_jsons(store)
    write_thumbnails(store)
    ingest_datasets(store)
    publish_datasets(store)
    list_public(store)
    match_public(store)
    archive_datasets(store)
