import argparse

from .commands import (archive_datasets, check, clean, fetch_files,
                       ingest_datasets, ingest_resource, list_local,
                       list_public, list_remote, match_local, match_public,
                       match_remote, publish_datasets, update_index,
                       update_resource, write_jsons, write_thumbnails)
from .config import settings
from .models import Store


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path of the files to publish')

    parser.add_argument('--config-file', dest='config_file',
                        help='File path of the config file')

    parser.add_argument('-i', '--include', dest='include_file',
                        help='Path to a file containing a list of files to include')
    parser.add_argument('-e', '--exclude', dest='exclude_file',
                        help='Path to a file containing a list of files to exclude')
    parser.add_argument('-d', '--datacite-file', dest='datacite_file',
                        help='Path to a file containing DateCite metadata (only for ingest_resource, update_resource)')
    parser.add_argument('-v', '--version', dest='version',
                        help='version date override [default: today]')

    parser.add_argument('--remote-dest', dest='remote_dest',
                        help='Remote destination to fetch files from, e.g. user@example.com')
    parser.add_argument('--remote-dir', dest='remote_dir',
                        help='Remote directory to fetch files from')
    parser.add_argument('--local-dir', dest='local_dir',
                        help='Local work directory')
    parser.add_argument('--public-dir', dest='public_dir',
                        help='Public directory')
    parser.add_argument('--archive-dir', dest='archive_dir',
                        help='Archive directory')
    parser.add_argument('--database', dest='database',
                        help='Database connection string, e.g. postgresql+psycopg2://username:password@host:port/dbname')
    parser.add_argument('--mock', dest='mock',
                        help='If set to True no files are actually copied. Empty mock files are used instead')
    parser.add_argument('--pattern-location', dest='pattern_locations',
                        help='URL or file path to the pattern json [default: https://protocol.isimip.org/pattern/]')
    parser.add_argument('--schema-location', dest='schema_locations',
                        help='URL or file path to the json schema [default: https://protocol.isimip.org/schema/]')
    parser.add_argument('--isimip-data-url', dest='isimip_data_url',
                        help='URL of the ISIMIP repository [default: https://data.isimip.org/]')
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')

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
    subparsers.add_parser('update_index').set_defaults(func=update_index)
    subparsers.add_parser('update_resource').set_defaults(func=update_resource)
    subparsers.add_parser('write_jsons').set_defaults(func=write_jsons)
    subparsers.add_parser('write_thumbnails').set_defaults(func=write_thumbnails)

    subparsers.add_parser('run').set_defaults(func=run)
    subparsers.add_parser('run_all').set_defaults(func=run_all)

    args = parser.parse_args()
    settings.setup(args)

    if hasattr(args, 'func'):
        store = Store(args.path)
        if store.pattern is None:
            parser.error('no pattern could be found for path')
        elif store.schema is None:
            parser.error('no schema could be found for path')
        elif (args.func in ['ingest_resource', 'update_resource']):
            if store.datacite is None:
                parser.error('no DateCite metadata file was provided')

        try:
            args.func(store)
        except AssertionError as e:
            parser.error(e)
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
