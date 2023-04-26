import argparse
from datetime import date

from .commands import (archive_datasets, check, clean, fetch_files, init,
                       insert_datasets, insert_doi, link_datasets, link_files,
                       link_links, list_local, list_public, list_public_links,
                       list_remote, list_remote_links, match_local,
                       match_public, match_public_links, match_remote,
                       match_remote_links, publish_datasets, register_doi,
                       update_datasets, update_doi, update_index,
                       write_link_jsons, write_local_jsons, write_public_jsons)
from .config import RIGHTS_CHOICES, settings


def get_parser(add_path=False, add_subparsers=False):
    parser = argparse.ArgumentParser(prog='isimip-publisher')

    parser.add_argument('--config-file', dest='config_file',
                        help='File path of the config file')

    parser.add_argument('-i', '--include', dest='include_file',
                        help='Path to a file containing a list of files to include')
    parser.add_argument('-e', '--exclude', dest='exclude_file',
                        help='Path to a file containing a list of files to exclude')
    parser.add_argument('-v', '--version', dest='version',
                        default=date.today().strftime('%Y%m%d'),
                        help='Version date override [default: today]')

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
                        default='false',
                        help='If set to True, no files are actually copied. Empty mock files are used instead')
    parser.add_argument('--restricted', dest='restricted',
                        default='false',
                        help='If set to True, the files are flaged as restricted in the database.')
    parser.add_argument('--protocol-location', dest='protocol_locations',
                        default='https://protocol.isimip.org https://protocol2.isimip.org',
                        help='URL or file path to the protocol')
    parser.add_argument('--datacite-username', dest='datacite_username',
                        help='Username for DataCite')
    parser.add_argument('--datacite-password', dest='datacite_password',
                        help='Password for DataCite')
    parser.add_argument('--datacite-prefix', dest='datacite_prefix',
                        default='10.48364',
                        help='Prefix for DataCite')
    parser.add_argument('--datacite-test-mode', dest='datacite_test_mode',
                        default='false',
                        help='If set to True, the test version of DataCite is used')
    parser.add_argument('--isimip-data-url', dest='isimip_data_url',
                        default='https://data.isimip.org/',
                        help='URL of the ISIMIP repository [default: https://data.isimip.org/]')
    parser.add_argument('--rights', dest='rights', choices=RIGHTS_CHOICES,
                        help='Rights/license for the files [default: None]')
    parser.add_argument('--log-level', dest='log_level', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')

    if add_subparsers:
        subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

        # add a subparser for each subcommand
        for func in [list_remote, list_remote_links, list_local, list_public, list_public_links,
                     match_remote, match_remote_links, match_local, match_public, match_public_links,
                     fetch_files, write_local_jsons, write_public_jsons, write_link_jsons,
                     insert_datasets, update_datasets, publish_datasets, archive_datasets,
                     check, clean, update_index, run]:
            subparser = subparsers.add_parser(func.__name__)
            subparser.set_defaults(func=func)
            subparser.add_argument('path', help='path of the files to process')

        for func in [insert_doi]:
            subparser = subparsers.add_parser(func.__name__)
            subparser.set_defaults(func=func)
            subparser.add_argument('RESOURCE_LOCATION', help='JSON file with DataCite metadata')
            subparser.add_argument('paths', nargs='+', help='paths of the files to process')

        for func in [update_doi]:
            subparser = subparsers.add_parser(func.__name__)
            subparser.set_defaults(func=func)
            subparser.add_argument('RESOURCE_LOCATION', help='JSON file with DataCite metadata')

        for func in [register_doi]:
            subparser = subparsers.add_parser(func.__name__)
            subparser.set_defaults(func=func)
            subparser.add_argument('doi', help='DOI to process')

        for func in [link_links, link_files, link_datasets, link]:
            subparser = subparsers.add_parser(func.__name__)
            subparser.set_defaults(func=func)
            subparser.add_argument('target_path', help='path of the files to process')
            subparser.add_argument('path', help='path for the links')

        for func in [init]:
            subparser = subparsers.add_parser(func.__name__)
            subparser.set_defaults(func=func)

    return parser


def main():
    parser = get_parser(add_path=True, add_subparsers=True)
    settings.setup(parser)

    if hasattr(settings, 'FUNC'):
        try:
            settings.FUNC()
        except AssertionError as e:
            parser.error(e)
    else:
        parser.print_help()


def run():
    fetch_files()
    write_local_jsons()
    insert_datasets()
    publish_datasets()


def link():
    link_links()
    write_link_jsons()
    link_datasets()
