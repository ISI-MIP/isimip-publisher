from isimip_publisher.utils.config import parse_config, parse_filelist
from isimip_publisher.utils.files import list_local_files
from isimip_publisher.utils.netcdf import update_netcdf_global_attributes
from isimip_publisher.utils.validation import validate_file
from isimip_publisher.utils.metadata import get_netcdf_metadata


def parser(subparsers):
    parser = subparsers.add_parser('update')
    parser.add_argument('-f|--file', dest='filelist_file', default=None,
                        help='path to a file containing the list of files')
    parser.set_defaults(func=main)


def main(args):
    config = parse_config(args)
    filelist = parse_filelist(args)

    for file in list_local_files(config, filelist):
        identifiers = validate_file(config, file)
        metadata = get_netcdf_metadata(config, identifiers)
        update_netcdf_global_attributes(config, metadata, file)
