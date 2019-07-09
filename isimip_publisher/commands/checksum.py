from isimip_publisher.utils.config import parse_config, parse_filelist
from isimip_publisher.utils.files import list_local_files
from isimip_publisher.utils.checksum import write_checksum


def parser(subparsers):
    parser = subparsers.add_parser('checksum')
    parser.add_argument('-f|--file', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)
    filelist = parse_filelist(args)

    for file in list_local_files(config, filelist):
        write_checksum(file)
