from ..utils import get_subparser_title
from ..utils.config import parse_config
from ..utils.files import list_remote_files


def parser(subparsers):
    parser = subparsers.add_parser(get_subparser_title(__name__))
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args.simulation_round, args.sector, args.model)

    for file in list_remote_files(config):
        print(file)
