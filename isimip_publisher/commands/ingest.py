from isimip_publisher.utils.config import parse_config, parse_filelist


def parser(subparsers):
    parser = subparsers.add_parser('ingest')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)
    filelist = parse_filelist(args)
