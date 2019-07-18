from isimip_publisher.utils.config import parse_config
from isimip_publisher.utils.files import list_local_files, list_remote_files


def parser(subparsers):
    parser = subparsers.add_parser('list')
    parser.add_argument('--remote', action='store_true',
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)

    if args.remote:
        files = list_remote_files(config)
    else:
        files = list_local_files(config)

    for file in files:
        print(file)
