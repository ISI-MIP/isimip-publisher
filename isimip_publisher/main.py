import argparse

from isimip_publisher.commands import (
    clean,
    copy,
    checksum,
    json,
    list_files,
    publish,
    ingest,
    update,
    validate
)

from isimip_publisher.utils import setup_logging, setup_env


def main():
    setup_env()
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument('simulation_round', help='name of the simulation_round')
    parser.add_argument('sector', help='name of the sector')
    parser.add_argument('model', help='models to process')

    subparsers = parser.add_subparsers(title='subcommands', description='valid subcommands')

    clean.parser(subparsers)
    copy.parser(subparsers)
    checksum.parser(subparsers)
    json.parser(subparsers)
    list_files.parser(subparsers)
    publish.parser(subparsers)
    ingest.parser(subparsers)
    update.parser(subparsers)
    validate.parser(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # here we call clean.main, fetch.main, etc
        args.func(args)
    else:
        parser.print_help()
