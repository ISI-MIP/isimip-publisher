import argparse

from .commands import (archive_datasets, check, clean, fetch_files,
                       ingest_datasets, list_local, list_public, list_remote,
                       match_local, match_public, match_remote,
                       publish_datasets, register_doi, update_doi,
                       update_index, write_checksums, write_jsons,
                       write_thumbnails)
from .config import settings
from .models import Store


def get_parser(add_subparsers=False):
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path of the files to publish')

    parser.add_argument('--config-file', dest='config_file',
                        help='File path of the config file')

    parser.add_argument('-i', '--include', dest='include_file',
                        help='Path to a file containing a list of files to include')
    parser.add_argument('-e', '--exclude', dest='exclude_file',
                        help='Path to a file containing a list of files to exclude')
    parser.add_argument('-d', '--datacite-file', dest='datacite_file',
                        help='Path to a file containing DateCite metadata (only for register_doi, update_doi)')
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
    parser.add_argument('--protocol-location', dest='protocol_locations',
                        help='URL or file path to the protocol')
    parser.add_argument('--isimip-data-url', dest='isimip_data_url',
                        help='URL of the ISIMIP repository [default: https://data.isimip.org/]')
    parser.add_argument('--log-level', dest='log_level',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')

    if add_subparsers:
        subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

        # add a subparser for each subcommand
        subparsers.add_parser('list_remote').set_defaults(func=list_remote)
        subparsers.add_parser('list_local').set_defaults(func=list_local)
        subparsers.add_parser('list_public').set_defaults(func=list_public)
        subparsers.add_parser('match_remote').set_defaults(func=match_remote)
        subparsers.add_parser('match_local').set_defaults(func=match_local)
        subparsers.add_parser('match_public').set_defaults(func=match_public)
        subparsers.add_parser('fetch_files').set_defaults(func=fetch_files)
        subparsers.add_parser('write_thumbnails').set_defaults(func=write_thumbnails)
        subparsers.add_parser('write_jsons').set_defaults(func=write_jsons)
        subparsers.add_parser('write_checksums').set_defaults(func=write_checksums)
        subparsers.add_parser('ingest_datasets').set_defaults(func=ingest_datasets)
        subparsers.add_parser('publish_datasets').set_defaults(func=publish_datasets)
        subparsers.add_parser('archive_datasets').set_defaults(func=archive_datasets)
        subparsers.add_parser('register_doi').set_defaults(func=register_doi)
        subparsers.add_parser('update_doi').set_defaults(func=update_doi)
        subparsers.add_parser('check').set_defaults(func=check)
        subparsers.add_parser('clean').set_defaults(func=clean)
        subparsers.add_parser('update_index').set_defaults(func=update_index)
        subparsers.add_parser('run').set_defaults(func=run)

    return parser


def main():
    parser = get_parser(add_subparsers=True)
    args = parser.parse_args()
    settings.setup(args)

    if hasattr(args, 'func'):
        store = Store(args.path)

        try:
            args.func(store)
        except AssertionError as e:
            parser.error(e)
    else:
        parser.print_help()


def run(store=None):
    match_remote(store)
    fetch_files(store)
    write_thumbnails(store)
    write_checksums(store)
    write_jsons(store)
    ingest_datasets(store)
    publish_datasets(store)
