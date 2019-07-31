import argparse

from isimip_publisher.commands import (
    clean,
    copy_files,
    create_checksums,
    create_datasets,
    create_jsons,
    list_local,
    list_remote,
    publish_files,
    update_database,
    update_files,
    validate_local,
    validate_remote,
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
    copy_files.parser(subparsers)
    create_checksums.parser(subparsers)
    create_datasets.parser(subparsers)
    create_jsons.parser(subparsers)
    list_local.parser(subparsers)
    list_remote.parser(subparsers)
    publish_files.parser(subparsers)
    update_database.parser(subparsers)
    update_files.parser(subparsers)
    validate_local.parser(subparsers)
    validate_remote.parser(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # here we call clean.main, fetch.main, etc
        args.func(args)
    else:
        parser.print_help()
