from datetime import date

from isimip_utils.cli import ArgumentParser, parse_filelist, parse_locations, parse_version, setup_logs

from . import VERSION
from .commands import (
    archive_datasets,
    check,
    check_doi,
    clean,
    count_local,
    count_public,
    count_public_links,
    count_remote,
    count_remote_links,
    diff_remote,
    diff_remote_links,
    fetch_files,
    insert_datasets,
    insert_doi,
    link_datasets,
    link_files,
    link_links,
    list_local,
    list_public,
    list_public_links,
    list_remote,
    list_remote_links,
    match_local,
    match_public,
    match_public_links,
    match_remote,
    match_remote_links,
    publish_datasets,
    register_doi,
    update_datasets,
    update_doi,
    update_search,
    update_tree,
    update_views,
    write_link_jsons,
    write_local_jsons,
    write_public_jsons,
)
from .config import RIGHTS_CHOICES, settings


def main():
    parser = ArgumentParser(prog='isimip-publisher')

    parser.add_argument('-i', '--include', dest='include', type=parse_filelist,
                        help='Path to a file containing a list of files to include')
    parser.add_argument('-e', '--exclude', dest='exclude', type=parse_filelist,
                        help='Path to a file containing a list of files to exclude')
    parser.add_argument('-v', '--version', dest='version', type=parse_version, default=date.today().strftime('%Y%m%d'),
                        help='Version date override [default: today]')

    parser.add_argument('--remote-dest', dest='remote_dest',
                        help='Remote destination to fetch files from, e.g. user@example.com')
    parser.add_argument('--remote-dir', dest='remote_dir',
                        help='Remote directory to fetch files from')
    parser.add_argument('--local-dir', dest='local_dir',
                        help='Local work directory')
    parser.add_argument('--public-dir', dest='public_dir',
                        help='Public directory')
    parser.add_argument('--restricted-dir', dest='restricted_dir',
                        help='Restricted directory')
    parser.add_argument('--archive-dir', dest='archive_dir',
                        help='Archive directory')
    parser.add_argument('--database', dest='database',
                        help='Database connection string, e.g. postgresql+psycopg2://username:password@host:port/dbname')
    parser.add_argument('--mock', dest='mock', action='store_true', default=False,
                        help='If set to True, no files are actually copied. Empty mock files are used instead')
    parser.add_argument('--restricted', dest='restricted', action='store_true', default=False,
                        help='If set to True, the files are flagged as restricted in the database.')
    parser.add_argument('--protocol-location', dest='protocol_locations', type=parse_locations,
                        default='https://protocol.isimip.org https://protocol2.isimip.org',
                        help='URL or file path to the protocol')
    parser.add_argument('--datacite-username', dest='datacite_username',
                        help='Username for DataCite')
    parser.add_argument('--datacite-password', dest='datacite_password',
                        help='Password for DataCite')
    parser.add_argument('--datacite-prefix', dest='datacite_prefix', type=str,
                        default='10.48364',
                        help='Prefix for DataCite')
    parser.add_argument('--datacite-test-mode', dest='datacite_test_mode', action='store_true', default=False,
                        help='If set to True, the test version of DataCite is used')
    parser.add_argument('--isimip-data-url', dest='isimip_data_url', type=lambda p: p.rstrip('/'),
                        default='https://data.isimip.org',
                        help='URL of the ISIMIP repository [default: https://data.isimip.org/]')
    parser.add_argument('--rights', dest='rights', choices=RIGHTS_CHOICES,
                        help='Rights/license for the files [default: None]')
    parser.add_argument('--archived', dest='archived', action='store_true', default=False,
                        help='Check also archived files')
    parser.add_argument('--skip-registration', dest='skip_registration', action='store_true', default=False,
                         help='Skip the registration of the DOI when inserting/updating a resource')
    parser.add_argument('--skip-checksum', dest='skip_checksum', action='store_true', default=False,
                         help='Skip the computation of the checksum when checking')
    parser.add_argument('--resolve-links', dest='resolve_links', action='store_true', default=False,
                         help='Resolve remote links as if they were files')
    parser.add_argument('--log-level', dest='log_level', default='WARN',
                        help='Log level (ERROR, WARN, INFO, or DEBUG)')
    parser.add_argument('--log-file', dest='log_file',
                        help='Path to the log file')
    parser.add_argument('-V', action='version', version=VERSION)

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    # add a subparser for each subcommand
    for command in [list_remote, list_remote_links, list_local, list_public, list_public_links,
                 match_remote, match_remote_links, match_local, match_public, match_public_links,
                 count_remote, count_remote_links, count_local, count_public, count_public_links,
                 fetch_files, write_local_jsons, write_public_jsons,
                 insert_datasets, update_datasets, publish_datasets, archive_datasets,
                 diff_remote, diff_remote_links, check, clean, update_search, update_tree, run]:
        subparser = subparsers.add_parser(command.__name__)
        subparser.set_defaults(command=command)
        subparser.add_argument('path', help='path of the files to process')

    for command in [insert_doi]:
        subparser = subparsers.add_parser(command.__name__)
        subparser.set_defaults(command=command)
        subparser.add_argument('RESOURCE_LOCATION', help='JSON file with DataCite metadata')
        subparser.add_argument('paths', nargs='+', help='paths of the datasets to process')

    for command in [update_doi]:
        subparser = subparsers.add_parser(command.__name__)
        subparser.set_defaults(command=command)
        subparser.add_argument('RESOURCE_LOCATION', help='JSON file with DataCite metadata')

    for command in [register_doi]:
        subparser = subparsers.add_parser(command.__name__)
        subparser.set_defaults(command=command)
        subparser.add_argument('doi', help='DOI to process')

    for command in [check_doi]:
        subparser = subparsers.add_parser(command.__name__)
        subparser.set_defaults(command=command)
        subparser.add_argument('path', help='path of the datasets to check')

    for command in [link_links, link_files, link_datasets, link, write_link_jsons]:
        subparser = subparsers.add_parser(command.__name__)
        subparser.set_defaults(command=command)
        subparser.add_argument('target_path', help='path of the files to process')
        subparser.add_argument('path', help='path for the links')

    for command in [init, update_views]:
        subparser = subparsers.add_parser(command.__name__)
        subparser.set_defaults(command=command)

    args = parser.parse_args()

    setup_logs(log_level=args.log_level, log_file=args.log_file)

    settings.from_dict(vars(args))

    if hasattr(args, 'command'):
        args.command()
    else:
        parser.print_help()


def init():
    update_views()


def run():
    fetch_files()
    write_local_jsons()
    insert_datasets()
    publish_datasets()


def link():
    link_links()
    write_link_jsons()
    link_datasets()
