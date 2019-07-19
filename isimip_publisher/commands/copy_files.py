from isimip_publisher.utils import get_subparser_title
from isimip_publisher.utils.config import parse_config, parse_filelist
from isimip_publisher.utils.files import list_remote_files, copy_files, chmod_file


def parser(subparsers):
    parser = subparsers.add_parser(get_subparser_title(__name__))
    parser.add_argument('-f', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args.simulation_round, args.sector, args.model)
    filelist = parse_filelist(args.filelist_file)
    remote_files = list_remote_files(config, filelist)
    local_files = copy_files(config, remote_files)

    for file_path in local_files:
        chmod_file(file_path)
