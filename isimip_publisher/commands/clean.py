from ..utils import get_subparser_title
from ..utils.config import parse_config, parse_filelist
from ..utils.files import delete_file, list_local_files


def parser(subparsers):
    parser = subparsers.add_parser(get_subparser_title(__name__))
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args.simulation_round, args.sector, args.model)
    filelist = parse_filelist(args.filelist_file)

    for file_path in list_local_files(config, filelist):
        delete_file(file_path)
