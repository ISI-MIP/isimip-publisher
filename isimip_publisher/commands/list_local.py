from isimip_publisher.utils.config import parse_config
from isimip_publisher.utils.files import list_local_files


def parser(subparsers):
    parser = subparsers.add_parser('list_local')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)

    for file in list_local_files(config):
        print(file)
