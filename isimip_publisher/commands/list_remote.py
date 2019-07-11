from isimip_publisher.utils.config import parse_config
from isimip_publisher.utils.files import list_remote_files


def parser(subparsers):
    parser = subparsers.add_parser('list_remote')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)

    for file in list_remote_files(config):
        print(file)
