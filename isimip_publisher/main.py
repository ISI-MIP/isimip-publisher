import argparse

from isimip_publisher.commands import checksum, clean, copy, ingest, json, list, \
                                      publish, update, validate

from isimip_publisher.utils import setup_logging, setup_env


def main():
    setup_env()
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('simulation_round', help='name of the simulation_round')
    parser.add_argument('sector', help='name of the sector')
    parser.add_argument('model', help='models to process')

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    checksum.parser(subparsers)
    clean.parser(subparsers)
    copy.parser(subparsers)
    ingest.parser(subparsers)
    json.parser(subparsers)
    list.parser(subparsers)
    publish.parser(subparsers)
    update.parser(subparsers)
    validate.parser(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # here we call clean.main, fetch.main, etc
        args.func(args)
    else:
        parser.print_help()
