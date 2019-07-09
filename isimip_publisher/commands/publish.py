from isimip_publisher.utils.config import parse_config, parse_filelist
from isimip_publisher.utils.files import list_local_files, publish_files


def parser(subparsers):
    parser = subparsers.add_parser('publish')
    parser.add_argument('-f|--file', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)
    filelist = parse_filelist(args)
    local_files = list_local_files(config, filelist)
    publish_files(config, local_files)
