from isimip_publisher.utils.config import parse_config, parse_filelist
from isimip_publisher.utils.files import list_remote_files, copy_files, chmod_files


def parser(subparsers):
    parser = subparsers.add_parser('fetch')
    parser.add_argument('-f|--file', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)
    filelist = parse_filelist(args)
    remote_files = list_remote_files(config, filelist)
    local_files = copy_files(config, remote_files)
    chmod_files(local_files)
