from isimip_publisher.utils.config import parse_config, parse_filelist
from isimip_publisher.utils.files import list_local_files, list_remote_files
from isimip_publisher.utils.validation import validate_file_path


def parser(subparsers):
    parser = subparsers.add_parser('validate')
    parser.add_argument('-f|--file', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('--remote', action='store_true',
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)
    filelist = parse_filelist(args)

    if args.remote:
        files = list_remote_files(config, filelist)
    else:
        files = list_local_files(config, filelist)

    for file in files:
        validate_file_path(config, file)
