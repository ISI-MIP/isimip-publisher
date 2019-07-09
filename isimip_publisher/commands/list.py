from isimip_publisher.utils.config import parse_config
from isimip_publisher.utils.files import list_remote_files, list_local_files


def parser(subparsers):
    parser = subparsers.add_parser('list')
    parser.add_argument('--remote', action='store_true', default=None,
                        help='work on the remote files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)

    if args.remote:
        files = list_remote_files(config)
    else:
        files = list_local_files(config)

    for file in files:
        print(file)
