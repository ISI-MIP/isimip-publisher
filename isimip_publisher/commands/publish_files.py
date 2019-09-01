from ..utils import get_subparser_title
from ..utils.config import parse_config, parse_filelist, parse_version
from ..utils.files import list_local_files, publish_files


def parser(subparsers):
    parser = subparsers.add_parser(get_subparser_title(__name__))
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.add_argument('-v', dest='version', default=False,
                        help='version date override [default: today]')
    parser.set_defaults(func=main)


def main(args):
    version = parse_version(args.version)
    config = parse_config(args.simulation_round, args.product, args.sector, args.model, version)
    filelist = parse_filelist(args.filelist_file)
    local_files = list_local_files(config, filelist)
    publish_files(config, local_files)
